"""
AI Reply Generator for Email Routing System
Generates draft replies for classified emails using Claude API.
"""

import os
import time
from typing import Dict, Optional
from dotenv import load_dotenv
import anthropic

from config import CATEGORIES, REPLY_CONFIG, RATE_LIMIT, get_category_by_id

load_dotenv()


class ReplyGenerator:
    """Generates AI draft replies for emails based on their classification."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set it in .env file or pass directly."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = REPLY_CONFIG["model"]
        self.max_tokens = REPLY_CONFIG["max_tokens"]
        self.temperature = REPLY_CONFIG["temperature"]

        # Rate limiting
        self.request_delay = RATE_LIMIT["delay_between_requests"]
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def _get_category_context(self, category: str) -> str:
        """Get context about the email category for better replies."""
        cat_config = get_category_by_id(category)
        if cat_config:
            return f"Category: {cat_config.name}\nDescription: {cat_config.description}"
        return f"Category: {category}"

    def _build_system_prompt(self, category: str) -> str:
        """Build system prompt for reply generation."""
        category_context = self._get_category_context(category)

        return f"""You are a professional customer service representative drafting email replies.

{category_context}

## Guidelines
1. Be professional, friendly, and helpful
2. Address the sender by name if provided
3. Acknowledge their specific concern or question
4. Provide a clear, actionable response appropriate for the category
5. Keep the reply concise but complete
6. End with appropriate next steps or an offer to help further
7. Use a warm but professional sign-off

## Important Notes
- This is a DRAFT for human review - it will be reviewed and possibly edited before sending
- Do not make specific promises about timelines unless standard for the category
- For billing/refund requests, acknowledge receipt and explain next steps
- For complaints, show empathy and a commitment to resolve
- For technical issues, ask clarifying questions if needed
- For spam/marketing emails, generate a brief "no action needed" note instead

Write ONLY the email reply body. Do not include subject line or email headers."""

    def _build_user_prompt(
        self,
        subject: str,
        body: str,
        from_name: str
    ) -> str:
        """Build user prompt with email details."""
        sender = from_name if from_name else "the sender"
        return f"""Draft a reply to this email:

**From:** {sender}
**Subject:** {subject}

**Email Body:**
{body}

Write a professional draft reply:"""

    def generate_reply(
        self,
        subject: str,
        body: str,
        category: str,
        from_name: str = ""
    ) -> str:
        """Generate a draft reply for an email."""
        self._rate_limit()

        # For spam, return a simple note
        if category == "spam":
            return "[No reply needed - flagged as spam/marketing]"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self._build_system_prompt(category),
                messages=[
                    {
                        "role": "user",
                        "content": self._build_user_prompt(subject, body, from_name)
                    }
                ]
            )

            return response.content[0].text.strip()

        except anthropic.APIError as e:
            return f"[Error generating reply: {str(e)}]"

    def generate_batch_replies(
        self,
        emails: list,
        progress_callback=None
    ) -> Dict[str, str]:
        """Generate replies for a batch of emails.

        Args:
            emails: List of dicts with 'id', 'subject', 'body', 'category', 'from_name'
            progress_callback: Optional callback(current, total)

        Returns:
            Dict mapping email_id to generated reply
        """
        replies = {}
        total = len(emails)

        for i, email in enumerate(emails):
            email_id = email.get("id", f"email_{i}")
            reply = self.generate_reply(
                subject=email.get("subject", ""),
                body=email.get("body", ""),
                category=email.get("category", "general"),
                from_name=email.get("from_name", "")
            )
            replies[email_id] = reply

            if progress_callback:
                progress_callback(i + 1, total)

        return replies


def generate_reply(
    subject: str,
    body: str,
    category: str,
    from_name: str = "",
    api_key: str = None
) -> str:
    """Convenience function to generate a single reply."""
    generator = ReplyGenerator(api_key=api_key)
    return generator.generate_reply(subject, body, category, from_name)
