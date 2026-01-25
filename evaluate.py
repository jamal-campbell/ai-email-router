"""
Evaluation Module for Email Classification
Calculates accuracy metrics and generates performance reports.
"""

import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config import CATEGORIES, get_all_category_ids
from classifier import ClassificationResult


@dataclass
class CategoryMetrics:
    """Metrics for a single category."""
    category_id: str
    category_name: str
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1_score: float
    support: int  # Number of actual instances


@dataclass
class EvaluationReport:
    """Complete evaluation report."""
    timestamp: str
    total_samples: int
    overall_accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    category_metrics: Dict[str, CategoryMetrics]
    confusion_matrix: Dict[str, Dict[str, int]]
    misclassified_emails: List[Dict]


class Evaluator:
    """Evaluates classification performance against ground truth."""

    def __init__(self):
        self.predictions: List[Tuple[str, str, str]] = []  # (email_id, true, predicted)
        self.email_details: Dict[str, Dict] = {}  # email_id -> email data

    def add_result(
        self,
        email_id: str,
        true_category: str,
        predicted_category: str,
        email_data: Dict = None,
        confidence: float = None,
        reasoning: str = None
    ):
        """Add a single classification result for evaluation."""
        self.predictions.append((email_id, true_category, predicted_category))

        if email_data:
            self.email_details[email_id] = {
                "email": email_data,
                "true_category": true_category,
                "predicted_category": predicted_category,
                "confidence": confidence,
                "reasoning": reasoning,
                "correct": true_category == predicted_category
            }

    def add_batch_results(
        self,
        emails: List[Dict],
        classifications: List[ClassificationResult]
    ):
        """Add batch results from classification."""
        email_lookup = {e.get("id"): e for e in emails}

        for classification in classifications:
            email = email_lookup.get(classification.email_id, {})
            true_category = email.get("category_id", email.get("category", "unknown"))

            self.add_result(
                email_id=classification.email_id,
                true_category=true_category,
                predicted_category=classification.predicted_category,
                email_data=email,
                confidence=classification.confidence,
                reasoning=classification.reasoning
            )

    def _calculate_confusion_matrix(self) -> Dict[str, Dict[str, int]]:
        """Calculate the confusion matrix."""
        categories = get_all_category_ids()
        matrix = {cat: {c: 0 for c in categories} for cat in categories}

        for _, true_cat, pred_cat in self.predictions:
            if true_cat in matrix and pred_cat in categories:
                matrix[true_cat][pred_cat] += 1

        return matrix

    def _calculate_category_metrics(
        self,
        confusion_matrix: Dict[str, Dict[str, int]]
    ) -> Dict[str, CategoryMetrics]:
        """Calculate per-category metrics from confusion matrix."""
        categories = get_all_category_ids()
        metrics = {}

        for category in categories:
            # True positives: predicted category correctly
            tp = confusion_matrix[category][category]

            # False positives: predicted this category when it was something else
            fp = sum(
                confusion_matrix[other][category]
                for other in categories if other != category
            )

            # False negatives: was this category but predicted something else
            fn = sum(
                confusion_matrix[category][other]
                for other in categories if other != category
            )

            # True negatives: correctly not predicted as this category
            tn = sum(
                confusion_matrix[other1][other2]
                for other1 in categories if other1 != category
                for other2 in categories if other2 != category
            )

            # Calculate precision, recall, F1
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            # Support is the number of actual instances of this category
            support = sum(confusion_matrix[category].values())

            cat_config = CATEGORIES.get(category)
            cat_name = cat_config.name if cat_config else category

            metrics[category] = CategoryMetrics(
                category_id=category,
                category_name=cat_name,
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                true_negatives=tn,
                precision=precision,
                recall=recall,
                f1_score=f1,
                support=support
            )

        return metrics

    def _get_misclassified_emails(self) -> List[Dict]:
        """Get list of misclassified emails with details."""
        misclassified = []

        for email_id, details in self.email_details.items():
            if not details["correct"]:
                misclassified.append({
                    "email_id": email_id,
                    "subject": details["email"].get("subject", ""),
                    "true_category": details["true_category"],
                    "predicted_category": details["predicted_category"],
                    "confidence": details["confidence"],
                    "reasoning": details["reasoning"]
                })

        return misclassified

    def evaluate(self) -> EvaluationReport:
        """Run full evaluation and generate report."""
        if not self.predictions:
            raise ValueError("No predictions to evaluate")

        # Calculate confusion matrix
        confusion_matrix = self._calculate_confusion_matrix()

        # Calculate per-category metrics
        category_metrics = self._calculate_category_metrics(confusion_matrix)

        # Calculate overall accuracy
        correct = sum(1 for _, true, pred in self.predictions if true == pred)
        total = len(self.predictions)
        accuracy = correct / total if total > 0 else 0.0

        # Calculate macro averages (simple average across categories)
        valid_metrics = [m for m in category_metrics.values() if m.support > 0]

        macro_precision = sum(m.precision for m in valid_metrics) / len(valid_metrics) if valid_metrics else 0.0
        macro_recall = sum(m.recall for m in valid_metrics) / len(valid_metrics) if valid_metrics else 0.0
        macro_f1 = sum(m.f1_score for m in valid_metrics) / len(valid_metrics) if valid_metrics else 0.0

        # Get misclassified emails
        misclassified = self._get_misclassified_emails()

        return EvaluationReport(
            timestamp=datetime.now().isoformat(),
            total_samples=total,
            overall_accuracy=accuracy,
            macro_precision=macro_precision,
            macro_recall=macro_recall,
            macro_f1=macro_f1,
            category_metrics=category_metrics,
            confusion_matrix=confusion_matrix,
            misclassified_emails=misclassified
        )

    def print_report(self, report: EvaluationReport = None):
        """Print a formatted evaluation report to console."""
        if report is None:
            report = self.evaluate()

        print("\n" + "=" * 60)
        print("EMAIL CLASSIFICATION EVALUATION REPORT")
        print("=" * 60)
        print(f"\nTimestamp: {report.timestamp}")
        print(f"Total Samples: {report.total_samples}")

        print("\n--- OVERALL METRICS ---")
        print(f"Accuracy:  {report.overall_accuracy:.2%}")
        print(f"Precision: {report.macro_precision:.2%} (macro)")
        print(f"Recall:    {report.macro_recall:.2%} (macro)")
        print(f"F1 Score:  {report.macro_f1:.2%} (macro)")

        print("\n--- PER-CATEGORY METRICS ---")
        print(f"{'Category':<25} {'Precision':>10} {'Recall':>10} {'F1':>10} {'Support':>10}")
        print("-" * 65)

        for cat_id, metrics in sorted(report.category_metrics.items()):
            print(f"{metrics.category_name:<25} "
                  f"{metrics.precision:>10.2%} "
                  f"{metrics.recall:>10.2%} "
                  f"{metrics.f1_score:>10.2%} "
                  f"{metrics.support:>10}")

        print("\n--- CONFUSION MATRIX ---")
        categories = get_all_category_ids()
        # Print header (abbreviated)
        abbrevs = {cat: cat[:4] for cat in categories}
        header = "True\\Pred  " + " ".join(f"{abbrevs[c]:>5}" for c in categories)
        print(header)
        print("-" * len(header))

        for true_cat in categories:
            row = f"{abbrevs[true_cat]:<10} "
            row += " ".join(
                f"{report.confusion_matrix[true_cat][pred_cat]:>5}"
                for pred_cat in categories
            )
            print(row)

        if report.misclassified_emails:
            print(f"\n--- MISCLASSIFIED EMAILS ({len(report.misclassified_emails)}) ---")
            for i, email in enumerate(report.misclassified_emails[:10]):  # Show first 10
                print(f"\n{i+1}. [{email['email_id']}]")
                print(f"   Subject: {email['subject'][:50]}...")
                print(f"   True: {email['true_category']} | Predicted: {email['predicted_category']}")
                print(f"   Confidence: {email['confidence']:.2f}")
                if email['reasoning']:
                    print(f"   Reasoning: {email['reasoning'][:80]}...")

            if len(report.misclassified_emails) > 10:
                print(f"\n   ... and {len(report.misclassified_emails) - 10} more")

        print("\n" + "=" * 60)

    def save_report(self, filepath: str, report: EvaluationReport = None) -> str:
        """Save evaluation report to JSON file."""
        if report is None:
            report = self.evaluate()

        # Convert to serializable dict
        report_dict = {
            "timestamp": report.timestamp,
            "total_samples": report.total_samples,
            "overall_accuracy": report.overall_accuracy,
            "macro_precision": report.macro_precision,
            "macro_recall": report.macro_recall,
            "macro_f1": report.macro_f1,
            "category_metrics": {
                cat_id: asdict(metrics)
                for cat_id, metrics in report.category_metrics.items()
            },
            "confusion_matrix": report.confusion_matrix,
            "misclassified_emails": report.misclassified_emails
        }

        with open(filepath, 'w') as f:
            json.dump(report_dict, f, indent=2)

        return filepath
