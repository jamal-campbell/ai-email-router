#!/usr/bin/env python3
"""
Email Classification & Routing Pipeline
Main CLI for processing email corpora through the classification system.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List

from config import CATEGORIES
from classifier import EmailClassifier, ClassificationResult
from router import EmailRouter
from queues import QueueManager
from evaluate import Evaluator


def load_corpus(filepath: str) -> List[Dict]:
    """Load email corpus from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Handle both formats: list of emails or {emails: [...]}
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "emails" in data:
        return data["emails"]
    else:
        raise ValueError("Invalid corpus format. Expected list or {emails: [...]}")


def progress_callback(current: int, total: int, result: ClassificationResult):
    """Display progress during classification."""
    pct = (current / total) * 100
    bar_width = 30
    filled = int(bar_width * current / total)
    bar = "█" * filled + "░" * (bar_width - filled)

    # Truncate subject for display
    cat_display = result.predicted_category[:12].ljust(12)
    conf_display = f"{result.confidence:.0%}"

    sys.stdout.write(f"\r[{bar}] {pct:5.1f}% | {current}/{total} | {cat_display} ({conf_display})")
    sys.stdout.flush()

    if current == total:
        print()  # Newline at end


def run_pipeline(
    input_file: str,
    output_dir: str,
    limit: int = None,
    evaluate_accuracy: bool = True,
    verbose: bool = False
) -> Dict:
    """
    Run the full classification and routing pipeline.

    Args:
        input_file: Path to email corpus JSON
        output_dir: Directory for output files
        limit: Optional limit on number of emails to process
        evaluate_accuracy: Whether to evaluate against ground truth
        verbose: Print detailed progress

    Returns:
        Dict with pipeline results summary
    """
    print(f"\n{'='*60}")
    print("EMAIL CLASSIFICATION & ROUTING PIPELINE")
    print(f"{'='*60}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    queues_dir = os.path.join(output_dir, "queues")

    # Load corpus
    print(f"\n[1/4] Loading corpus from: {input_file}")
    emails = load_corpus(input_file)
    total_emails = len(emails)

    if limit and limit < total_emails:
        emails = emails[:limit]
        print(f"      Limited to {limit} emails (of {total_emails})")
    else:
        print(f"      Loaded {total_emails} emails")

    # Initialize components
    print("\n[2/4] Classifying emails...")
    classifier = EmailClassifier()
    queue_manager = QueueManager(output_dir=queues_dir)
    router = EmailRouter(queue_manager=queue_manager)
    evaluator = Evaluator() if evaluate_accuracy else None

    # Classify emails
    callback = progress_callback if not verbose else None
    classifications = classifier.classify_batch(emails, progress_callback=callback)

    if verbose:
        for result in classifications:
            print(f"  {result.email_id}: {result.predicted_category} "
                  f"(conf: {result.confidence:.2f}, urgent: {result.is_urgent})")

    # Route emails
    print("\n[3/4] Routing emails to queues...")
    routing_results = router.route_batch(emails, classifications)

    success_count = sum(1 for r in routing_results if r.success)
    print(f"      Routed {success_count}/{len(routing_results)} emails successfully")

    # Save queues
    saved_files = router.save_queues()
    print(f"      Saved to {len(saved_files)} queue files")

    # Generate routing report
    routing_report_path = os.path.join(output_dir, "routing_report.json")
    router.save_routing_report(routing_report_path)

    # Evaluate accuracy (if ground truth available)
    evaluation_report = None
    if evaluate_accuracy:
        print("\n[4/4] Evaluating classification accuracy...")
        evaluator.add_batch_results(emails, classifications)

        try:
            evaluation_report = evaluator.evaluate()
            evaluator.print_report(evaluation_report)

            # Save evaluation report
            eval_report_path = os.path.join(output_dir, "evaluation_report.json")
            evaluator.save_report(eval_report_path, evaluation_report)
            print(f"\n      Saved evaluation report to: {eval_report_path}")
        except Exception as e:
            print(f"      Warning: Could not evaluate accuracy: {e}")
    else:
        print("\n[4/4] Skipping evaluation (no ground truth or --no-eval flag)")

    # Save classification results
    results_path = os.path.join(output_dir, "classification_results.json")
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "input_file": input_file,
        "total_processed": len(emails),
        "results": [
            {
                "email_id": r.email_id,
                "predicted_category": r.predicted_category,
                "confidence": r.confidence,
                "is_urgent": r.is_urgent,
                "suggested_priority": r.suggested_priority,
                "reasoning": r.reasoning
            }
            for r in classifications
        ]
    }
    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)

    # Summary
    summary = router.get_routing_summary()

    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"\nProcessed: {len(emails)} emails")
    print(f"Output directory: {output_dir}")

    print("\nQueue distribution:")
    for queue_name, stats in sorted(summary["queues"].items()):
        cat_name = stats["category"]["name"] if stats["category"] else queue_name
        print(f"  {cat_name}: {stats['count']} emails")

    if evaluation_report:
        print(f"\nAccuracy: {evaluation_report.overall_accuracy:.1%}")
        print(f"F1 Score: {evaluation_report.macro_f1:.1%} (macro)")

    print(f"\nOutput files:")
    print(f"  - {results_path}")
    print(f"  - {routing_report_path}")
    if evaluate_accuracy:
        print(f"  - {os.path.join(output_dir, 'evaluation_report.json')}")
    for queue_name, filepath in saved_files.items():
        print(f"  - {filepath}")

    return {
        "total_processed": len(emails),
        "accuracy": evaluation_report.overall_accuracy if evaluation_report else None,
        "f1_score": evaluation_report.macro_f1 if evaluation_report else None,
        "output_dir": output_dir,
        "queue_counts": {q: s["count"] for q, s in summary["queues"].items()}
    }


def main():
    parser = argparse.ArgumentParser(
        description="Email Classification & Routing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --input email_corpus.json --output output/
  python pipeline.py -i emails.json -o results/ --limit 50
  python pipeline.py -i emails.json -o results/ --no-eval --verbose
        """
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to input email corpus (JSON)"
    )

    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output/)"
    )

    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=None,
        help="Limit number of emails to process"
    )

    parser.add_argument(
        "--no-eval",
        action="store_true",
        help="Skip accuracy evaluation"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    try:
        results = run_pipeline(
            input_file=args.input,
            output_dir=args.output,
            limit=args.limit,
            evaluate_accuracy=not args.no_eval,
            verbose=args.verbose
        )
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
