# AI Email Router

LLM-powered email classification and routing system that categorizes incoming emails into business queues with AI-generated draft replies.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Claude API](https://img.shields.io/badge/Claude-API-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)

## Live Demo

Try it now: [AI Email Router Dashboard](https://ai-email-router-3vyjxm52rzws36x3z2szqf.streamlit.app/)

## Features

- **Smart Classification**: Categorizes emails into 10 business categories (support, sales, billing, complaints, HR, IT, partnerships, legal, general, spam)
- **AI Draft Replies**: Generates professional response drafts for each email
- **Human-in-the-Loop**: Airtable integration for review and approval workflow
- **Evaluation Metrics**: Precision, recall, F1 scores with confusion matrix
- **Interactive Dashboard**: Streamlit UI for demos and real-time processing

## Architecture

```
Email JSON → Classifier (Claude API) → Router → Queues
                    │
                    ├── AI Reply Generator
                    │
                    └── Airtable (Human Approval)
```

[View Full Architecture Diagram](https://jamal-campbell.github.io/ai-email-router/architecture_diagram.html)

## Quick Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Run classification pipeline
python pipeline.py -i email_corpus.json -o output/

# Launch dashboard
streamlit run dashboard.py
```

## Usage

### Command Line

```bash
# Process all emails
python pipeline.py -i email_corpus.json -o output/

# Quick test with 10 emails
python pipeline.py -i email_corpus.json -o output/ --limit 10

# With Airtable integration
python demo_airtable.py -i email_corpus.json --limit 5

# Generate test corpus
python generate_email_corpus.py -n 300 -o email_corpus.json -s 42
```

### Dashboard

```bash
streamlit run dashboard.py
```

Opens at http://localhost:8501 with:
- Visual classification pipeline
- Real-time progress tracking
- Category distribution charts
- Expandable email results with AI replies

## Airtable Integration

Enable human review workflow:

1. Create an Airtable base with an "Email Queue" table
2. Add your credentials to `.env`:
   ```
   AIRTABLE_API_KEY=pat...
   AIRTABLE_BASE_ID=app...
   ```
3. Run with `--airtable` flag or use `demo_airtable.py`

## Project Structure

```
email/
├── pipeline.py          # Main orchestration
├── classifier.py        # Claude API classification
├── router.py            # Queue routing logic
├── queues.py            # Queue management
├── evaluate.py          # Accuracy metrics
├── reply_generator.py   # AI draft replies
├── airtable_integration.py
├── dashboard.py         # Streamlit UI
└── config.py            # Categories & settings
```

## Output

Results are saved to `output/`:
- `queues/*.json` - Emails sorted by category
- `classification_results.json` - All classifications
- `evaluation_report.json` - Accuracy metrics

## Author

Jamal Campbell - [jamalcampbell.org](https://jamalcampbell.org)
