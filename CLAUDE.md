# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM-based email classification and routing system using Claude API. Classifies incoming emails into 10 business categories and routes them to appropriate queues.

## Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run classification pipeline
python pipeline.py -i email_corpus.json -o output/

# Quick test with limited emails
python pipeline.py -i email_corpus.json -o output/ --limit 10

# Skip evaluation (no ground truth comparison)
python pipeline.py -i email_corpus.json -o output/ --no-eval

# Generate new test corpus
python generate_email_corpus.py -n 300 -o email_corpus.json -s 42
```

## Architecture

```
Email JSON → Classifier (Claude API) → Router → Queues (JSON files)
                    ↓
               Evaluator → Metrics Report
```

**Data Flow:**
1. `pipeline.py` orchestrates the workflow
2. `classifier.py` sends emails to Claude API, parses JSON responses into `ClassificationResult`
3. `router.py` maps categories to queues via `config.py` mappings, creates `QueuedEmail` objects
4. `queues.py` stores emails in memory and persists to `output/queues/*.json`
5. `evaluate.py` compares predictions to ground truth labels (`category_id` field in corpus)

**Key Classes:**
- `EmailClassifier` - Builds prompts, calls API, parses responses with rate limiting
- `EmailRouter` - Routes `ClassificationResult` to queues using `QueueManager`
- `QueueManager` - In-memory queue storage with JSON persistence
- `Evaluator` - Calculates accuracy, precision, recall, F1, confusion matrix

## Detailed Workflow

### Step 1: Load Corpus
- `pipeline.py` calls `load_corpus()` to read input JSON
- Accepts either `[{email}, ...]` or `{"emails": [{email}, ...]}`
- Optionally limits to N emails with `--limit` flag

### Step 2: Classify Emails
- `EmailClassifier` is initialized with API key from `.env`
- For each email, `classify()` method:
  1. Enforces rate limiting (default 0.1s between requests)
  2. Builds system prompt with category definitions from `config.py`
  3. Builds user prompt with email subject/body
  4. Calls Claude API (model: claude-sonnet-4-20250514)
  5. Parses JSON response → `ClassificationResult(email_id, predicted_category, confidence, reasoning, is_urgent, suggested_priority)`
- Progress bar updates after each classification

### Step 3: Route to Queues
- `EmailRouter.route_batch()` processes each `ClassificationResult`
- Looks up queue name from `config.py` category→queue mapping
- Creates `QueuedEmail` object with original email + classification metadata
- `QueueManager.enqueue()` adds to in-memory queue dict

### Step 4: Evaluate Accuracy
- `Evaluator.add_batch_results()` compares `predicted_category` vs `category_id` (ground truth)
- Calculates per-category metrics: precision, recall, F1, support
- Generates confusion matrix
- Identifies misclassified emails for review

### Step 5: Save Outputs
- `QueueManager.save_to_files()` → `output/queues/{queue-name}.json`
- Classification results → `output/classification_results.json`
- Routing report → `output/routing_report.json`
- Evaluation report → `output/evaluation_report.json`

## Categories

Defined in `config.py` as `CATEGORIES` dict. Each category has: `id`, `name`, `queue`, `priority`, `description`. Categories: support, sales, billing, complaint, hr, it_helpdesk, partnership, legal, general, spam.

## Configuration

- API settings in `config.py`: `API_CONFIG` (model, max_tokens, temperature), `RATE_LIMIT`
- API key via `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`

## Email Corpus Format

Input JSON must be either a list of emails or `{"emails": [...]}`. Each email needs: `id`, `from`, `from_name`, `to`, `subject`, `body`, `category_id` (for evaluation).

## Airtable Integration (Human Approval Workflow)

### Architecture with Airtable

```
Email → Classify → Generate AI Reply → Push to Airtable
                                            ↓
                              Human reviews in Airtable UI
                              (edit draft if needed)
                                            ↓
                              Change Status → "Approved"
                                            ↓
                              Airtable Automation triggers
```

### Airtable Setup (5 minutes)

1. **Create Airtable Account** (free tier works)
   - Go to https://airtable.com and sign up

2. **Create a New Base**
   - Click "Add a base" → "Start from scratch"
   - Name it "Email Routing Demo"

3. **Create Table with Fields**
   Create a table named "Email Queue" with these fields:

   | Field Name | Type | Notes |
   |------------|------|-------|
   | Email ID | Single line text | Primary field |
   | From | Single line text | |
   | Subject | Single line text | |
   | Body | Long text | |
   | Queue | Single select | Options: support-queue, sales-queue, billing-queue, etc. |
   | Category | Single line text | |
   | Confidence | Number (decimal) | |
   | Priority | Single select | Options: lowest, low, normal, high, urgent |
   | Is Urgent | Checkbox | |
   | AI Reasoning | Long text | |
   | AI Draft Reply | Long text | The generated reply |
   | Status | Single select | Options: Pending Review, Approved, Rejected, Modified |
   | Modified Reply | Long text | Human-edited version |
   | Reviewer Notes | Long text | |
   | Created At | Single line text | |
   | Approved At | Single line text | |

4. **Get API Credentials**
   - Go to https://airtable.com/create/tokens
   - Create a new token with these scopes:
     - `data.records:read`
     - `data.records:write`
   - Add your base to the token's access list
   - Copy the token (starts with `pat...`)

5. **Get Base ID**
   - Open your base in Airtable
   - The URL will be: `https://airtable.com/appXXXXXXXXXXXXXX/...`
   - Copy the part starting with `app` - that's your Base ID

6. **Add to .env file**
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   AIRTABLE_API_KEY=pat...
   AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
   ```

### Running with Airtable

```bash
# Run the demo pipeline with Airtable integration
python demo_airtable.py -i email_corpus.json --limit 5

# Or integrate into existing pipeline
python pipeline.py -i email_corpus.json -o output/ --airtable
```

### New Modules

- `airtable_integration.py` - AirtableClient, AirtableRouter, push/fetch records
- `reply_generator.py` - ReplyGenerator for AI draft replies

### Setting Up Airtable Automations (Optional)

To trigger actions when emails are approved:

1. In Airtable, click "Automations" tab
2. Create new automation with trigger: "When record matches conditions"
3. Condition: Status = "Approved"
4. Action: Send email, Slack notification, webhook, etc.

## Streamlit Dashboard (Demo UI)

A professional web dashboard for demos with prospective clients.

### Running the Dashboard

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Launch the dashboard
streamlit run dashboard.py
```

Opens at http://localhost:8501

### Dashboard Features

- **Visual Pipeline**: Click "Run Classification Pipeline" to process emails
- **Real-time Progress**: Watch emails being classified live
- **Category Charts**: Pie chart of distribution, confidence histogram
- **Expandable Results**: Click any email to see original + AI reply side-by-side
- **Airtable Integration**: Direct link to approval queue
- **Export**: Download results as JSON

### Deploying for Remote Demos

Free hosting on Streamlit Cloud:

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo and deploy
4. Add secrets (ANTHROPIC_API_KEY, AIRTABLE_API_KEY, AIRTABLE_BASE_ID)
5. Share the URL with clients

### Files

- `dashboard.py` - Streamlit dashboard application
- `demo_airtable.py` - CLI version for quick testing
