"""
Configuration for Email Categorization & Routing System
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class Priority(Enum):
    LOWEST = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class CategoryConfig:
    """Configuration for a single email category."""
    id: str
    name: str
    queue: str
    priority: Priority
    description: str


# Category definitions with queue mappings
CATEGORIES: Dict[str, CategoryConfig] = {
    "support": CategoryConfig(
        id="support",
        name="Technical Support",
        queue="support-queue",
        priority=Priority.NORMAL,
        description="Technical issues, bugs, how-to questions, account access problems"
    ),
    "sales": CategoryConfig(
        id="sales",
        name="Sales Inquiry",
        queue="sales-queue",
        priority=Priority.NORMAL,
        description="Pricing questions, product demos, purchase inquiries, upgrade requests"
    ),
    "billing": CategoryConfig(
        id="billing",
        name="Billing/Payments",
        queue="billing-queue",
        priority=Priority.NORMAL,
        description="Invoices, refunds, payment issues, subscription changes, charges"
    ),
    "complaint": CategoryConfig(
        id="complaint",
        name="Customer Complaint",
        queue="escalations-queue",
        priority=Priority.HIGH,
        description="Unhappy customers, service complaints, escalations, negative feedback"
    ),
    "hr": CategoryConfig(
        id="hr",
        name="Human Resources",
        queue="hr-queue",
        priority=Priority.NORMAL,
        description="PTO requests, benefits, workplace concerns, employee matters"
    ),
    "it_helpdesk": CategoryConfig(
        id="it_helpdesk",
        name="IT Help Desk",
        queue="it-helpdesk-queue",
        priority=Priority.NORMAL,
        description="Password resets, software requests, VPN issues, equipment requests"
    ),
    "partnership": CategoryConfig(
        id="partnership",
        name="Partnership/Business Development",
        queue="partnerships-queue",
        priority=Priority.LOW,
        description="Partnership proposals, integration requests, affiliate inquiries, co-marketing"
    ),
    "legal": CategoryConfig(
        id="legal",
        name="Legal/Compliance",
        queue="legal-queue",
        priority=Priority.HIGH,
        description="Contracts, GDPR requests, compliance, legal notices, NDAs"
    ),
    "general": CategoryConfig(
        id="general",
        name="General Inquiry",
        queue="general-queue",
        priority=Priority.LOW,
        description="General questions, documentation requests, getting started help"
    ),
    "spam": CategoryConfig(
        id="spam",
        name="Spam/Marketing",
        queue="spam-queue",
        priority=Priority.LOWEST,
        description="Spam, phishing attempts, unsolicited marketing, scams"
    ),
}


def get_category_by_id(category_id: str) -> CategoryConfig:
    """Get category configuration by ID."""
    return CATEGORIES.get(category_id)


def get_category_by_name(name: str) -> CategoryConfig:
    """Get category configuration by display name."""
    for cat in CATEGORIES.values():
        if cat.name.lower() == name.lower():
            return cat
    return None


def get_all_category_ids() -> List[str]:
    """Get list of all category IDs."""
    return list(CATEGORIES.keys())


def get_all_category_names() -> List[str]:
    """Get list of all category display names."""
    return [cat.name for cat in CATEGORIES.values()]


def get_queue_for_category(category_id: str) -> str:
    """Get the queue name for a category."""
    cat = CATEGORIES.get(category_id)
    return cat.queue if cat else "general-queue"


def get_priority_for_category(category_id: str) -> Priority:
    """Get the priority level for a category."""
    cat = CATEGORIES.get(category_id)
    return cat.priority if cat else Priority.NORMAL


# API Configuration
API_CONFIG = {
    "model": "claude-sonnet-4-20250514",  # Good balance of speed and accuracy
    "max_tokens": 256,
    "temperature": 0.0,  # Deterministic for classification
}

# Rate limiting
RATE_LIMIT = {
    "requests_per_minute": 50,
    "delay_between_requests": 0.1,  # seconds
}

# Airtable Configuration
# Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID in .env file
AIRTABLE_CONFIG = {
    "base_id": "",  # Or set via AIRTABLE_BASE_ID env var
    "table_name": "Email Queue",  # Default table name
    "status_field": "Status",
    "status_options": ["Pending Review", "Approved", "Rejected", "Modified"],
}

# Reply Generation Configuration
REPLY_CONFIG = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "temperature": 0.7,  # Slightly creative for natural replies
}
