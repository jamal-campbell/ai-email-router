"""
LLM-Based Email Classifier using Claude API
Classifies emails into predefined categories with high accuracy.
"""

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import anthropic

from config import (
    CATEGORIES,
    API_CONFIG,
    RATE_LIMIT,
    get_all_category_ids,
    get_category_by_id,
)

# Load environment variables
load_dotenv()


@dataclass
class ClassificationResult:
    """Result of classifying a single email."""
    email_id: str
    predicted_category: str
    confidence: float
    reasoning: str
    is_urgent: bool
    suggested_priority: str


class EmailClassifier:
    """Classifies emails using Claude API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Set it in .env file or pass directly."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = API_CONFIG["model"]
        self.max_tokens = API_CONFIG["max_tokens"]
        self.temperature = API_CONFIG["temperature"]

        # Rate limiting
        self.request_delay = RATE_LIMIT["delay_between_requests"]
        self.last_request_time = 0

    def _build_system_prompt(self) -> str:
        """Build the system prompt with category definitions."""
        category_descriptions = "\n".join([
            f"- **{cat.id}**: {cat.name} - {cat.description}"
            for cat in CATEGORIES.values()
        ])

        return f"""You are an expert email classification system. Your task is to categorize incoming emails into one of the predefined categories.

## Categories
{category_descriptions}

## Instructions
1. Analyze the email's subject and body carefully
2. Consider the sender's intent and the nature of the request
3. Choose the SINGLE most appropriate category
4. Determine if the email is urgent based on language cues (words like "ASAP", "urgent", "immediately", "critical")
5. Provide brief reasoning for your classification

## Response Format
You MUST respond with valid JSON in exactly this format:
{{
    "category": "<category_id>",
    "confidence": <0.0-1.0>,
    "reasoning": "<brief explanation>",
    "is_urgent": <true/false>
}}

Only use category IDs from this list: {get_all_category_ids()}
"""

    def _build_user_prompt(self, email: Dict) -> str:
        """Build the user prompt with email content."""
        return f"""Classify this email:

**From:** {email.get('from_name', 'Unknown')} <{email.get('from', 'unknown@email.com')}>
**To:** {email.get('to', 'unknown')}
**Subject:** {email.get('subject', '(no subject)')}

**Body:**
{email.get('body', '(empty)')}

Respond with JSON only."""

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request_time = time.time()

    def _parse_response(self, response_text: str, email_id: str) -> ClassificationResult:
        """Parse the LLM response into a ClassificationResult."""
        try:
            # Try to extract JSON from response
            text = response_text.strip()

            # Handle case where response might have markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)

            category = data.get("category", "general")
            # Validate category
            if category not in get_all_category_ids():
                category = "general"

            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

            # Determine priority based on category and urgency
            is_urgent = data.get("is_urgent", False)
            cat_config = get_category_by_id(category)
            if is_urgent:
                suggested_priority = "urgent"
            elif cat_config:
                suggested_priority = cat_config.priority.name.lower()
            else:
                suggested_priority = "normal"

            return ClassificationResult(
                email_id=email_id,
                predicted_category=category,
                confidence=confidence,
                reasoning=data.get("reasoning", ""),
                is_urgent=is_urgent,
                suggested_priority=suggested_priority
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Return default classification on parse error
            return ClassificationResult(
                email_id=email_id,
                predicted_category="general",
                confidence=0.3,
                reasoning=f"Parse error: {str(e)}",
                is_urgent=False,
                suggested_priority="normal"
            )

    def classify(self, email: Dict) -> ClassificationResult:
        """Classify a single email."""
        self._rate_limit()

        email_id = email.get("id", "unknown")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self._build_system_prompt(),
                messages=[
                    {"role": "user", "content": self._build_user_prompt(email)}
                ]
            )

            response_text = response.content[0].text
            return self._parse_response(response_text, email_id)

        except anthropic.APIError as e:
            return ClassificationResult(
                email_id=email_id,
                predicted_category="general",
                confidence=0.0,
                reasoning=f"API error: {str(e)}",
                is_urgent=False,
                suggested_priority="normal"
            )

    def classify_batch(
        self,
        emails: List[Dict],
        progress_callback=None
    ) -> List[ClassificationResult]:
        """Classify a batch of emails with optional progress reporting."""
        results = []
        total = len(emails)

        for i, email in enumerate(emails):
            result = self.classify(email)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total, result)

        return results


def default_progress_callback(current: int, total: int, result: ClassificationResult):
    """Default progress callback that prints to console."""
    pct = (current / total) * 100
    print(f"[{current}/{total}] ({pct:.1f}%) {result.email_id}: "
          f"{result.predicted_category} (conf: {result.confidence:.2f})")


# Convenience function for quick classification
def classify_email(email: Dict, api_key: str = None) -> ClassificationResult:
    """Quick function to classify a single email."""
    classifier = EmailClassifier(api_key=api_key)
    return classifier.classify(email)
