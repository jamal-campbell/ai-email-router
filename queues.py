"""
Queue Manager for Email Routing System
Handles queue operations and persistence to JSON files.
"""

import json
import os
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import Priority, CATEGORIES


@dataclass
class QueuedEmail:
    """An email item in a queue."""
    id: str
    from_addr: str
    from_name: str
    to: str
    subject: str
    body: str
    timestamp: str
    original_category: str  # Ground truth if available
    predicted_category: str
    confidence: float
    priority: str
    queued_at: str
    reasoning: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "QueuedEmail":
        return cls(**data)


class QueueManager:
    """Manages email queues with in-memory storage and JSON persistence."""

    def __init__(self, output_dir: str = "output/queues"):
        self.output_dir = output_dir
        self.queues: Dict[str, List[QueuedEmail]] = defaultdict(list)
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)

    def enqueue(self, queue_name: str, email: QueuedEmail) -> None:
        """Add an email to a queue."""
        self.queues[queue_name].append(email)

    def dequeue(self, queue_name: str) -> Optional[QueuedEmail]:
        """Remove and return the first email from a queue."""
        if self.queues[queue_name]:
            return self.queues[queue_name].pop(0)
        return None

    def peek(self, queue_name: str) -> Optional[QueuedEmail]:
        """View the first email in a queue without removing it."""
        if self.queues[queue_name]:
            return self.queues[queue_name][0]
        return None

    def get_queue_size(self, queue_name: str) -> int:
        """Get the number of emails in a queue."""
        return len(self.queues[queue_name])

    def get_all_queue_names(self) -> List[str]:
        """Get names of all queues that have emails."""
        return list(self.queues.keys())

    def get_queue_contents(self, queue_name: str) -> List[QueuedEmail]:
        """Get all emails in a queue (without removing them)."""
        return self.queues[queue_name].copy()

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues."""
        stats = {
            "total_emails": sum(len(q) for q in self.queues.values()),
            "queues": {}
        }

        for queue_name, emails in self.queues.items():
            priority_counts = defaultdict(int)
            for email in emails:
                priority_counts[email.priority] += 1

            stats["queues"][queue_name] = {
                "count": len(emails),
                "by_priority": dict(priority_counts)
            }

        return stats

    def save_to_files(self) -> Dict[str, str]:
        """Save all queues to individual JSON files."""
        saved_files = {}

        for queue_name, emails in self.queues.items():
            if not emails:
                continue

            filename = f"{queue_name}.json"
            filepath = os.path.join(self.output_dir, filename)

            queue_data = {
                "queue_name": queue_name,
                "saved_at": datetime.now().isoformat(),
                "count": len(emails),
                "emails": [email.to_dict() for email in emails]
            }

            with open(filepath, 'w') as f:
                json.dump(queue_data, f, indent=2)

            saved_files[queue_name] = filepath

        return saved_files

    def load_from_file(self, filepath: str) -> str:
        """Load a queue from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        queue_name = data["queue_name"]
        self.queues[queue_name] = [
            QueuedEmail.from_dict(email_data)
            for email_data in data["emails"]
        ]

        return queue_name

    def clear_queue(self, queue_name: str) -> int:
        """Clear all emails from a queue. Returns count of removed emails."""
        count = len(self.queues[queue_name])
        self.queues[queue_name] = []
        return count

    def clear_all_queues(self) -> int:
        """Clear all queues. Returns total count of removed emails."""
        total = sum(len(q) for q in self.queues.values())
        self.queues = defaultdict(list)
        return total

    def get_emails_by_priority(self, priority: str) -> List[QueuedEmail]:
        """Get all emails across queues with a specific priority."""
        results = []
        for emails in self.queues.values():
            for email in emails:
                if email.priority == priority:
                    results.append(email)
        return results

    def save_summary_report(self, filepath: str = None) -> str:
        """Save a summary report of all queues."""
        if filepath is None:
            filepath = os.path.join(self.output_dir, "queue_summary.json")

        stats = self.get_queue_stats()
        stats["generated_at"] = datetime.now().isoformat()

        # Add category mapping info
        stats["category_queue_mapping"] = {
            cat_id: cat.queue for cat_id, cat in CATEGORIES.items()
        }

        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)

        return filepath


def create_queued_email(
    email_data: Dict,
    predicted_category: str,
    confidence: float,
    priority: str,
    reasoning: str = None
) -> QueuedEmail:
    """Factory function to create a QueuedEmail from raw email data."""
    return QueuedEmail(
        id=email_data.get("id", ""),
        from_addr=email_data.get("from", ""),
        from_name=email_data.get("from_name", ""),
        to=email_data.get("to", ""),
        subject=email_data.get("subject", ""),
        body=email_data.get("body", ""),
        timestamp=email_data.get("timestamp", ""),
        original_category=email_data.get("category", ""),
        predicted_category=predicted_category,
        confidence=confidence,
        priority=priority,
        queued_at=datetime.now().isoformat(),
        reasoning=reasoning
    )
