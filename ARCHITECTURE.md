# AI Email Routing Framework - Architecture Guide

> A modular, tool-agnostic framework for AI-powered email classification and routing with human-in-the-loop approval.

---

## Executive Summary

This framework demonstrates a production-ready pattern for AI workflow automation. Each component is **abstracted** and **swappable**, allowing organizations to adapt to changing requirements, vendor preferences, or cost constraints without rebuilding from scratch.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                              │
│                                                                              │
│    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│    │  Streamlit   │     │    Gradio    │     │  React/Vue   │              │
│    │  Dashboard   │     │  Interface   │     │    SPA       │              │
│    └──────────────┘     └──────────────┘     └──────────────┘              │
│           │                    │                    │                       │
└───────────┼────────────────────┼────────────────────┼───────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ORCHESTRATION LAYER                               │
│                                                                              │
│                         ┌──────────────────┐                                │
│                         │   pipeline.py    │                                │
│                         │                  │                                │
│                         │  • Load data     │                                │
│                         │  • Coordinate    │                                │
│                         │  • Error handle  │                                │
│                         └──────────────────┘                                │
│                                  │                                          │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLASSIFY      │    │   GENERATE      │    │   ROUTE         │
│                 │    │                 │    │                 │
│  classifier.py  │    │ reply_gen.py    │    │  router.py      │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │ LLM API   │  │    │  │ LLM API   │  │    │  │ Dest API  │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INTEGRATION LAYER                                  │
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│   │  Claude     │    │  Airtable   │    │   Slack     │    │  Database   │ │
│   │  API        │    │  API        │    │   API       │    │  (any)      │ │
│   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Presentation Layer (User Interface)

**Purpose:** Provides the user-facing interface for triggering pipelines and viewing results.

| Currently Using | Alternatives | When to Consider |
|-----------------|--------------|------------------|
| **Streamlit** | Gradio | Faster prototyping, ML-focused demos |
| | React + FastAPI | Full custom UI, complex interactions |
| | Retool / Appsmith | Low-code internal tools |
| | Slack Bot | Chat-based interface for teams |
| | CLI only | Developer/automation workflows |

**Abstraction Point:** `dashboard.py` is completely decoupled from business logic. Swap UI frameworks without touching classification or routing code.

---

### 2. Orchestration Layer (Pipeline Coordination)

**Purpose:** Coordinates the workflow, handles errors, manages state, and sequences operations.

| Currently Using | Alternatives | When to Consider |
|-----------------|--------------|------------------|
| **Python scripts** | Apache Airflow | Complex DAGs, scheduling, monitoring |
| | Prefect | Modern Python-native orchestration |
| | Temporal | Long-running workflows, reliability |
| | AWS Step Functions | Serverless, AWS-native |
| | n8n / Make | No-code workflow automation |

**Abstraction Point:** `pipeline.py` defines the workflow sequence. Each step (classify, generate, route) is a function call that can be wrapped in any orchestration framework.

---

### 3. AI/LLM Layer (Intelligence)

**Purpose:** Provides the AI capabilities for classification and content generation.

| Currently Using | Alternatives | When to Consider |
|-----------------|--------------|------------------|
| **Claude (Anthropic)** | GPT-4 (OpenAI) | Different capabilities, pricing |
| | Gemini (Google) | Google ecosystem integration |
| | Llama (Meta) | Self-hosted, data privacy |
| | Mistral | European data residency, cost |
| | AWS Bedrock | Multi-model, enterprise AWS |

**Abstraction Point:** `classifier.py` and `reply_generator.py` wrap LLM calls behind simple interfaces:
```python
def classify(email: dict) -> ClassificationResult
def generate_reply(subject, body, category) -> str
```
Swap LLM providers by changing the API client initialization—business logic remains unchanged.

---

### 4. Human-in-the-Loop Layer (Approval Workflow)

**Purpose:** Enables human review, editing, and approval before actions are taken.

| Currently Using | Alternatives | When to Consider |
|-----------------|--------------|------------------|
| **Airtable** | Notion | Team already uses Notion |
| | Google Sheets | Simplest, most familiar |
| | Monday.com | Project management integration |
| | Jira | Engineering team workflows |
| | Custom web app | Full control, specific requirements |
| | Slack (with buttons) | Quick approvals, chat-based teams |

**Abstraction Point:** `airtable_integration.py` implements a simple interface:
```python
def push_email(record: AirtableRecord) -> dict
def get_pending_reviews() -> list
def mark_approved(record_id: str) -> dict
```
Create a new `slack_integration.py` or `notion_integration.py` with the same interface to swap destinations.

---

### 5. Data Layer (Storage & Persistence)

**Purpose:** Stores emails, results, and audit trails.

| Currently Using | Alternatives | When to Consider |
|-----------------|--------------|------------------|
| **JSON files** | PostgreSQL | Production, querying, scale |
| | MongoDB | Document storage, flexibility |
| | SQLite | Simple local persistence |
| | S3 + Athena | Large scale, analytics |
| | Supabase | Quick backend with auth |

**Abstraction Point:** `queues.py` manages storage through `QueueManager`:
```python
def enqueue(queue_name: str, email: QueuedEmail)
def save_to_files() -> dict
def load_from_file(filepath: str)
```

---

## Swappability Matrix

| Component | Swap Difficulty | Files to Modify | LOC to Change |
|-----------|-----------------|-----------------|---------------|
| LLM Provider | 🟢 Easy | `classifier.py`, `reply_generator.py` | ~20 lines |
| Approval Destination | 🟢 Easy | Create new `*_integration.py` | ~100 lines |
| UI Framework | 🟡 Medium | Replace `dashboard.py` | ~400 lines |
| Orchestration | 🟡 Medium | Wrap `pipeline.py` functions | ~50 lines |
| Database | 🟢 Easy | Modify `queues.py` | ~50 lines |

---

## Configuration Philosophy

All external dependencies are configured via environment variables and `config.py`:

```bash
# .env file - secrets and connections
ANTHROPIC_API_KEY=sk-ant-...      # LLM provider
AIRTABLE_API_KEY=pat...            # Approval workflow
AIRTABLE_BASE_ID=app...            # Approval workflow

# Swap to OpenAI? Change one line:
# OPENAI_API_KEY=sk-...
```

```python
# config.py - behavior tuning
API_CONFIG = {
    "model": "claude-sonnet-4-20250514",  # Change model here
    "max_tokens": 256,
    "temperature": 0.0,
}
```

---

## Extension Patterns

### Adding a New Integration

1. Create `new_integration.py` following the pattern:
```python
class NewServiceClient:
    def __init__(self, api_key: str = None):
        # Initialize connection

    def push_email(self, record) -> dict:
        # Send to service

    def get_status(self, record_id: str) -> str:
        # Check status
```

2. Add config to `config.py`
3. Import and use in `pipeline.py` or `dashboard.py`

### Adding a New Category

1. Add to `CATEGORIES` dict in `config.py`:
```python
"new_category": CategoryConfig(
    id="new_category",
    name="Display Name",
    queue="new-queue",
    priority=Priority.NORMAL,
    description="When to use this category"
)
```

2. The classifier will automatically include it (prompt is generated from config)

### Customizing AI Behavior

Modify prompts in `classifier.py` and `reply_generator.py`:
- `_build_system_prompt()` - Classification rules
- `_build_user_prompt()` - Input formatting

---

## Deployment Options

| Environment | Recommended Stack | Notes |
|-------------|-------------------|-------|
| **Demo/POC** | Streamlit Cloud (free) | Quick sharing, no infra |
| **Internal Tool** | Docker + any VM | Simple, self-contained |
| **Production** | Kubernetes + managed DB | Scale, reliability |
| **Serverless** | AWS Lambda + Step Functions | Pay-per-use, auto-scale |

---

## Cost Considerations

| Component | Cost Driver | Optimization |
|-----------|-------------|--------------|
| LLM (Claude) | Tokens processed | Batch requests, cache common responses |
| Airtable | Records/month | Archive old records, use free tier limits |
| Streamlit Cloud | Private apps | Use free public tier for demos |
| Compute | Always-on vs. serverless | Serverless for bursty workloads |

**Typical Demo Costs:** < $5/month (LLM API calls on small batches)
**Production Estimate:** $50-500/month depending on volume

---

## Summary

This framework demonstrates that **AI workflow automation doesn't require vendor lock-in**. By maintaining clear abstractions at each layer:

1. **Swap LLMs** as pricing and capabilities evolve
2. **Change approval tools** based on team preferences
3. **Scale infrastructure** from demo to production
4. **Customize behavior** without rewriting core logic

The investment is in the **pattern**, not the specific tools.

---

*Generated for client discussions. Adapt as needed for specific opportunities.*
