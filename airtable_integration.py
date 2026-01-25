"""
Airtable Integration for Email Routing System
Pushes classified emails to Airtable for human review and approval workflow.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

try:
    from pyairtable import Api, Table
    AIRTABLE_AVAILABLE = True
except ImportError:
    AIRTABLE_AVAILABLE = False

from config import AIRTABLE_CONFIG, get_category_by_id

load_dotenv()


@dataclass
class AirtableRecord:
    """Represents a record to be pushed to Airtable."""
    email_id: str
    from_addr: str
    from_name: str
    subject: str
    body: str
    queue: str
    category: str
    confidence: float
    priority: str
    is_urgent: bool
    reasoning: str
    ai_draft_reply: str
    status: str = "Pending Review"
    modified_reply: str = ""
    reviewer_notes: str = ""

    def to_airtable_fields(self) -> Dict[str, Any]:
        """Convert to Airtable field format."""
        return {
            "Email ID": self.email_id,
            "From": f"{self.from_name} <{self.from_addr}>",
            "Subject": self.subject,
            "Body": self.body[:100000],  # Airtable long text limit
            "Queue": self.queue,
            "Category": self.category,
            "Confidence": self.confidence,
            "Priority": self.priority,
            "Is Urgent": self.is_urgent,
            "AI Reasoning": self.reasoning,
            "AI Draft Reply": self.ai_draft_reply,
            "Status": self.status,
            "Modified Reply": self.modified_reply,
            "Reviewer Notes": self.reviewer_notes,
            "Created At": datetime.now().isoformat(),
        }


class AirtableClient:
    """Client for interacting with Airtable API."""

    def __init__(
        self,
        api_key: str = None,
        base_id: str = None,
        table_name: str = None
    ):
        if not AIRTABLE_AVAILABLE:
            raise ImportError(
                "pyairtable is not installed. Run: pip install pyairtable"
            )

        self.api_key = api_key or os.getenv("AIRTABLE_API_KEY")
        self.base_id = base_id or os.getenv("AIRTABLE_BASE_ID") or AIRTABLE_CONFIG.get("base_id")
        self.table_name = table_name or AIRTABLE_CONFIG.get("table_name", "Email Queue")

        if not self.api_key:
            raise ValueError(
                "AIRTABLE_API_KEY not found. Set it in .env file or pass directly."
            )
        if not self.base_id:
            raise ValueError(
                "AIRTABLE_BASE_ID not found. Set it in .env file or config.py."
            )

        self.api = Api(self.api_key)
        self.table = self.api.table(self.base_id, self.table_name)

    def push_email(self, record: AirtableRecord) -> Dict:
        """Push a single email record to Airtable."""
        fields = record.to_airtable_fields()
        result = self.table.create(fields)
        return result

    def push_batch(
        self,
        records: List[AirtableRecord],
        progress_callback=None
    ) -> List[Dict]:
        """Push multiple email records to Airtable."""
        results = []
        total = len(records)

        # Airtable batch create (up to 10 at a time)
        batch_size = 10
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]
            fields_batch = [r.to_airtable_fields() for r in batch]
            batch_results = self.table.batch_create(fields_batch)
            results.extend(batch_results)

            if progress_callback:
                progress_callback(min(i + batch_size, total), total)

        return results

    def get_pending_reviews(self) -> List[Dict]:
        """Get all records pending human review."""
        formula = "{Status} = 'Pending Review'"
        return self.table.all(formula=formula)

    def get_approved_emails(self) -> List[Dict]:
        """Get all approved emails ready to send."""
        formula = "{Status} = 'Approved'"
        return self.table.all(formula=formula)

    def get_by_queue(self, queue_name: str) -> List[Dict]:
        """Get all records for a specific queue."""
        formula = f"{{Queue}} = '{queue_name}'"
        return self.table.all(formula=formula)

    def update_status(self, record_id: str, status: str, notes: str = None) -> Dict:
        """Update the status of a record."""
        fields = {"Status": status}
        if notes:
            fields["Reviewer Notes"] = notes
        return self.table.update(record_id, fields)

    def mark_approved(self, record_id: str, modified_reply: str = None) -> Dict:
        """Mark a record as approved, optionally with a modified reply."""
        fields = {
            "Status": "Approved",
            "Approved At": datetime.now().isoformat()
        }
        if modified_reply:
            fields["Modified Reply"] = modified_reply
        return self.table.update(record_id, fields)

    def mark_rejected(self, record_id: str, reason: str = None) -> Dict:
        """Mark a record as rejected."""
        fields = {"Status": "Rejected"}
        if reason:
            fields["Reviewer Notes"] = reason
        return self.table.update(record_id, fields)


def create_airtable_record(
    queued_email: "QueuedEmail",
    ai_draft_reply: str = ""
) -> AirtableRecord:
    """Create an AirtableRecord from a QueuedEmail."""
    cat_config = get_category_by_id(queued_email.predicted_category)
    category_name = cat_config.name if cat_config else queued_email.predicted_category

    return AirtableRecord(
        email_id=queued_email.id,
        from_addr=queued_email.from_addr,
        from_name=queued_email.from_name,
        subject=queued_email.subject,
        body=queued_email.body,
        queue=cat_config.queue if cat_config else "general-queue",
        category=category_name,
        confidence=queued_email.confidence,
        priority=queued_email.priority,
        is_urgent=queued_email.priority == "urgent",
        reasoning=queued_email.reasoning or "",
        ai_draft_reply=ai_draft_reply
    )


class AirtableRouter:
    """Routes classified emails to Airtable with AI-generated draft replies."""

    def __init__(
        self,
        airtable_client: AirtableClient = None,
        reply_generator=None
    ):
        self.client = airtable_client or AirtableClient()
        self.reply_generator = reply_generator

    def route_email(
        self,
        queued_email: "QueuedEmail",
        generate_reply: bool = True
    ) -> Dict:
        """Route a single email to Airtable with optional AI reply generation."""
        ai_draft = ""
        if generate_reply and self.reply_generator:
            ai_draft = self.reply_generator.generate_reply(
                subject=queued_email.subject,
                body=queued_email.body,
                category=queued_email.predicted_category,
                from_name=queued_email.from_name
            )

        record = create_airtable_record(queued_email, ai_draft)
        return self.client.push_email(record)

    def route_batch(
        self,
        queued_emails: List["QueuedEmail"],
        generate_replies: bool = True,
        progress_callback=None
    ) -> List[Dict]:
        """Route a batch of emails to Airtable."""
        records = []
        total = len(queued_emails)

        for i, email in enumerate(queued_emails):
            ai_draft = ""
            if generate_replies and self.reply_generator:
                ai_draft = self.reply_generator.generate_reply(
                    subject=email.subject,
                    body=email.body,
                    category=email.predicted_category,
                    from_name=email.from_name
                )

            record = create_airtable_record(email, ai_draft)
            records.append(record)

            if progress_callback:
                progress_callback(i + 1, total, "Generating replies")

        return self.client.push_batch(records, progress_callback)


def default_progress_callback(current: int, total: int, stage: str = ""):
    """Default progress callback."""
    pct = (current / total) * 100
    print(f"[{current}/{total}] ({pct:.1f}%) {stage}")
