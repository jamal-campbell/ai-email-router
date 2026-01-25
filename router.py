"""
Email Router
Routes classified emails to appropriate queues based on category.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from config import CATEGORIES, get_queue_for_category, get_category_by_id
from classifier import ClassificationResult
from queues import QueueManager, QueuedEmail, create_queued_email


@dataclass
class RoutingResult:
    """Result of routing a single email."""
    email_id: str
    queue_name: str
    priority: str
    success: bool
    error: Optional[str] = None


class EmailRouter:
    """Routes emails to queues based on classification results."""

    def __init__(self, queue_manager: QueueManager = None, output_dir: str = "output/queues"):
        self.queue_manager = queue_manager or QueueManager(output_dir=output_dir)

    def route_email(
        self,
        email_data: Dict,
        classification: ClassificationResult
    ) -> RoutingResult:
        """Route a single email to the appropriate queue."""
        try:
            # Get queue name for the category
            queue_name = get_queue_for_category(classification.predicted_category)

            # Create queued email object
            queued_email = create_queued_email(
                email_data=email_data,
                predicted_category=classification.predicted_category,
                confidence=classification.confidence,
                priority=classification.suggested_priority,
                reasoning=classification.reasoning
            )

            # Add to queue
            self.queue_manager.enqueue(queue_name, queued_email)

            return RoutingResult(
                email_id=classification.email_id,
                queue_name=queue_name,
                priority=classification.suggested_priority,
                success=True
            )

        except Exception as e:
            return RoutingResult(
                email_id=classification.email_id,
                queue_name="error-queue",
                priority="normal",
                success=False,
                error=str(e)
            )

    def route_batch(
        self,
        emails: List[Dict],
        classifications: List[ClassificationResult],
        progress_callback=None
    ) -> List[RoutingResult]:
        """Route a batch of emails based on their classifications."""
        results = []
        total = len(emails)

        # Create email lookup by ID
        email_lookup = {e.get("id", f"email_{i}"): e for i, e in enumerate(emails)}

        for i, classification in enumerate(classifications):
            email_data = email_lookup.get(classification.email_id, {})
            result = self.route_email(email_data, classification)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, total, result)

        return results

    def get_routing_summary(self) -> Dict:
        """Get a summary of routing results."""
        stats = self.queue_manager.get_queue_stats()

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_routed": stats["total_emails"],
            "queues": {}
        }

        for queue_name, queue_stats in stats["queues"].items():
            # Find category for this queue
            category_info = None
            for cat in CATEGORIES.values():
                if cat.queue == queue_name:
                    category_info = {
                        "id": cat.id,
                        "name": cat.name,
                        "default_priority": cat.priority.name
                    }
                    break

            summary["queues"][queue_name] = {
                "count": queue_stats["count"],
                "by_priority": queue_stats["by_priority"],
                "category": category_info
            }

        return summary

    def save_queues(self) -> Dict[str, str]:
        """Save all queues to files and return file paths."""
        return self.queue_manager.save_to_files()

    def save_routing_report(self, filepath: str = None) -> str:
        """Save a detailed routing report."""
        return self.queue_manager.save_summary_report(filepath)

    def get_high_priority_emails(self) -> List[QueuedEmail]:
        """Get all emails marked as high priority or urgent."""
        high = self.queue_manager.get_emails_by_priority("high")
        urgent = self.queue_manager.get_emails_by_priority("urgent")
        return high + urgent


def default_routing_callback(current: int, total: int, result: RoutingResult):
    """Default progress callback for routing."""
    status = "OK" if result.success else f"FAILED: {result.error}"
    print(f"[{current}/{total}] {result.email_id} -> {result.queue_name} ({result.priority}) [{status}]")
