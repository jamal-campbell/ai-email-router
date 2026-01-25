#!/usr/bin/env python3
"""
Demo script for Airtable integration with human approval workflow.
Classifies emails, generates AI reply drafts, and pushes to Airtable for review.
"""

import argparse
import json
import sys
from typing import List, Dict

from classifier import EmailClassifier, ClassificationResult
from queues import create_queued_email
from reply_generator import ReplyGenerator
from airtable_integration import AirtableClient, AirtableRouter, create_airtable_record
from config import get_queue_for_category


def load_corpus(filepath: str) -> List[Dict]:
    """Load email corpus from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "emails" in data:
        return data["emails"]
    else:
        raise ValueError("Invalid corpus format")


def main():
    parser = argparse.ArgumentParser(
        description="Demo: Classify emails and push to Airtable with AI reply drafts"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input email corpus JSON file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Limit number of emails to process (default: 5)"
    )
    parser.add_argument(
        "--no-replies",
        action="store_true",
        help="Skip AI reply generation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process emails but don't push to Airtable"
    )

    args = parser.parse_args()

    # Load emails
    print(f"Loading emails from {args.input}...")
    emails = load_corpus(args.input)

    if args.limit:
        emails = emails[:args.limit]

    print(f"Processing {len(emails)} emails\n")

    # Initialize components
    print("Initializing classifier...")
    classifier = EmailClassifier()

    reply_generator = None
    if not args.no_replies:
        print("Initializing reply generator...")
        reply_generator = ReplyGenerator()

    airtable_client = None
    if not args.dry_run:
        print("Initializing Airtable client...")
        try:
            airtable_client = AirtableClient()
            print(f"  Connected to table: {airtable_client.table_name}")
        except Exception as e:
            print(f"  Warning: Could not connect to Airtable: {e}")
            print("  Continuing in dry-run mode...")
            args.dry_run = True

    print("\n" + "=" * 60)
    print("PROCESSING EMAILS")
    print("=" * 60 + "\n")

    results = []

    for i, email in enumerate(emails, 1):
        email_id = email.get("id", f"email_{i}")
        subject = email.get("subject", "(no subject)")

        print(f"[{i}/{len(emails)}] {email_id}")
        print(f"  Subject: {subject[:50]}...")

        # Step 1: Classify
        classification = classifier.classify(email)
        print(f"  Category: {classification.predicted_category} "
              f"(confidence: {classification.confidence:.0%})")
        print(f"  Priority: {classification.suggested_priority}")

        # Step 2: Generate AI reply
        ai_draft = ""
        if reply_generator:
            print("  Generating AI reply draft...")
            ai_draft = reply_generator.generate_reply(
                subject=email.get("subject", ""),
                body=email.get("body", ""),
                category=classification.predicted_category,
                from_name=email.get("from_name", "")
            )
            # Show preview
            preview = ai_draft[:100].replace("\n", " ")
            print(f"  Draft preview: {preview}...")

        # Step 3: Create queued email
        queued_email = create_queued_email(
            email_data=email,
            predicted_category=classification.predicted_category,
            confidence=classification.confidence,
            priority=classification.suggested_priority,
            reasoning=classification.reasoning
        )

        # Step 4: Push to Airtable
        if airtable_client and not args.dry_run:
            record = create_airtable_record(queued_email, ai_draft)
            try:
                result = airtable_client.push_email(record)
                print(f"  Pushed to Airtable (record: {result['id']})")
            except Exception as e:
                print(f"  Error pushing to Airtable: {e}")

        results.append({
            "email_id": email_id,
            "category": classification.predicted_category,
            "confidence": classification.confidence,
            "priority": classification.suggested_priority,
            "ai_draft_preview": ai_draft[:200] if ai_draft else None
        })

        print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Processed: {len(results)} emails")

    # Category breakdown
    categories = {}
    for r in results:
        cat = r["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\nBy category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    if not args.dry_run and airtable_client:
        print(f"\nEmails are now in Airtable for human review!")
        print("Open your Airtable base to:")
        print("  1. Review AI-generated reply drafts")
        print("  2. Edit drafts if needed (use 'Modified Reply' field)")
        print("  3. Change Status to 'Approved' or 'Rejected'")
    else:
        print("\n(Dry run - no emails pushed to Airtable)")


if __name__ == "__main__":
    main()
