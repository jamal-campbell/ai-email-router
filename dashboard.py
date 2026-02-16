#!/usr/bin/env python3
"""
Streamlit Dashboard for AI Email Classification & Routing Demo
Professional demo interface for prospective business clients.
"""

import streamlit as st
import json
import time
import os
import random
import base64
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import project modules
from classifier import EmailClassifier, ClassificationResult
from reply_generator import ReplyGenerator
from queues import create_queued_email
from airtable_integration import AirtableClient, create_airtable_record
from config import CATEGORIES, AIRTABLE_CONFIG

# Page config
st.set_page_config(
    page_title="AI Email Router",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .status-pending { color: #f59e0b; font-weight: 600; }
    .status-success { color: #10b981; font-weight: 600; }
    .status-error { color: #ef4444; font-weight: 600; }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def load_corpus(filepath: str) -> list:
    """Load email corpus from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "emails" in data:
        return data["emails"]
    return []


def get_category_color(category: str) -> str:
    """Get color for category visualization."""
    colors = {
        "support": "#3b82f6",
        "sales": "#10b981",
        "billing": "#f59e0b",
        "complaint": "#ef4444",
        "hr": "#8b5cf6",
        "it_helpdesk": "#06b6d4",
        "partnership": "#ec4899",
        "legal": "#6366f1",
        "general": "#6b7280",
        "spam": "#9ca3af"
    }
    return colors.get(category, "#6b7280")


def initialize_session_state():
    """Initialize session state variables."""
    if 'processed_emails' not in st.session_state:
        st.session_state.processed_emails = []
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    if 'airtable_connected' not in st.session_state:
        st.session_state.airtable_connected = False
    if 'total_processed' not in st.session_state:
        st.session_state.total_processed = 0
    if 'data_source' not in st.session_state:
        st.session_state.data_source = None
    if 'loaded_emails' not in st.session_state:
        st.session_state.loaded_emails = []


def check_airtable_connection():
    """Check if Airtable is configured and accessible."""
    try:
        api_key = os.getenv("AIRTABLE_API_KEY")
        base_id = os.getenv("AIRTABLE_BASE_ID")
        if api_key and base_id:
            client = AirtableClient()
            st.session_state.airtable_connected = True
            return client
    except Exception:
        pass
    st.session_state.airtable_connected = False
    return None


def render_metrics(results: list):
    """Render metric cards."""
    col1, col2, col3, col4 = st.columns(4)

    total = len(results)
    if total == 0:
        return

    # Calculate metrics
    avg_confidence = sum(r.get('confidence', 0) for r in results) / total
    urgent_count = sum(1 for r in results if r.get('priority') == 'urgent')
    categories = {}
    for r in results:
        cat = r.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    top_category = max(categories, key=categories.get) if categories else "N/A"

    with col1:
        st.metric("Emails Processed", total)
    with col2:
        st.metric("Avg Confidence", f"{avg_confidence:.0%}")
    with col3:
        st.metric("Urgent Items", urgent_count)
    with col4:
        st.metric("Top Category", CATEGORIES.get(top_category, {}).name if hasattr(CATEGORIES.get(top_category, {}), 'name') else top_category.title())


def render_charts(results: list):
    """Render visualization charts."""
    if not results:
        return

    col1, col2 = st.columns(2)

    # Category distribution
    with col1:
        categories = {}
        for r in results:
            cat = r.get('category', 'unknown')
            cat_name = CATEGORIES[cat].name if cat in CATEGORIES else cat
            categories[cat_name] = categories.get(cat_name, 0) + 1

        fig = px.pie(
            values=list(categories.values()),
            names=list(categories.keys()),
            title="Category Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    # Confidence distribution
    with col2:
        confidences = [r.get('confidence', 0) for r in results]
        fig = go.Figure(data=[go.Histogram(
            x=confidences,
            nbinsx=10,
            marker_color='#667eea'
        )])
        fig.update_layout(
            title="Confidence Distribution",
            xaxis_title="Confidence Score",
            yaxis_title="Count",
            margin=dict(t=40, b=40, l=40, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)


def render_results_table(results: list):
    """Render expandable results table."""
    if not results:
        return

    st.markdown("### 📋 Processed Emails")

    for i, result in enumerate(results):
        cat = result.get('category', 'unknown')
        cat_config = CATEGORIES.get(cat)
        cat_name = cat_config.name if cat_config else cat
        confidence = result.get('confidence', 0)
        priority = result.get('priority', 'normal')

        # Priority emoji
        priority_emoji = {"urgent": "🔴", "high": "🟠", "normal": "🟢", "low": "🔵", "lowest": "⚪"}.get(priority, "⚪")

        with st.expander(f"{priority_emoji} **{result.get('subject', 'No subject')[:60]}** — {cat_name} ({confidence:.0%})"):
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**Original Email**")
                st.text(f"From: {result.get('from_name', '')} <{result.get('from', '')}>")
                st.text(f"Subject: {result.get('subject', '')}")
                st.markdown("---")
                st.text_area("Body", result.get('body', ''), height=150, disabled=True, key=f"body_{i}")

            with col2:
                st.markdown("**AI Analysis**")
                st.text(f"Category: {cat_name}")
                st.text(f"Confidence: {confidence:.0%}")
                st.text(f"Priority: {priority}")
                st.text(f"Queue: {cat_config.queue if cat_config else 'general-queue'}")
                st.markdown("---")
                if result.get('ai_reply'):
                    st.text_area("AI Draft Reply", result.get('ai_reply', ''), height=150, disabled=True, key=f"reply_{i}")

            st.caption(f"Reasoning: {result.get('reasoning', 'N/A')}")


def process_emails(emails: list, generate_replies: bool, push_to_airtable: bool):
    """Process emails through the classification pipeline."""
    results = []

    # Initialize components
    classifier = EmailClassifier()
    reply_generator = ReplyGenerator() if generate_replies else None
    airtable_client = check_airtable_connection() if push_to_airtable else None

    # Progress UI
    progress_bar = st.progress(0)
    status_text = st.empty()
    current_email = st.empty()

    total = len(emails)

    for i, email in enumerate(emails):
        email_id = email.get('id', f'email_{i}')
        subject = email.get('subject', '(no subject)')

        # Update progress
        progress = (i + 1) / total
        progress_bar.progress(progress)
        status_text.markdown(f"**Processing:** {i + 1} of {total} emails ({progress:.0%})")
        current_email.info(f"📧 {subject[:50]}...")

        # Step 1: Classify
        classification = classifier.classify(email)

        # Step 2: Generate reply
        ai_reply = ""
        if reply_generator:
            ai_reply = reply_generator.generate_reply(
                subject=email.get('subject', ''),
                body=email.get('body', ''),
                category=classification.predicted_category,
                from_name=email.get('from_name', '')
            )

        # Step 3: Push to Airtable
        airtable_status = "skipped"
        if airtable_client:
            try:
                queued_email = create_queued_email(
                    email_data=email,
                    predicted_category=classification.predicted_category,
                    confidence=classification.confidence,
                    priority=classification.suggested_priority,
                    reasoning=classification.reasoning
                )
                record = create_airtable_record(queued_email, ai_reply)
                airtable_client.push_email(record)
                airtable_status = "sent"
            except Exception as e:
                airtable_status = f"error: {e}"

        # Store result
        results.append({
            'email_id': email_id,
            'from': email.get('from', ''),
            'from_name': email.get('from_name', ''),
            'subject': subject,
            'body': email.get('body', ''),
            'category': classification.predicted_category,
            'confidence': classification.confidence,
            'priority': classification.suggested_priority,
            'reasoning': classification.reasoning,
            'ai_reply': ai_reply,
            'airtable_status': airtable_status
        })

        # Small delay for visual effect
        time.sleep(0.1)

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    current_email.empty()

    return results


def render_hero_section():
    """Render the hero/intro section explaining the tool."""
    st.markdown("---")
    st.markdown("### How It Works")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### 1️⃣ Ingest")
        st.markdown("Upload or connect email sources (JSON, API, mailbox)")
    with col2:
        st.markdown("#### 2️⃣ Classify")
        st.markdown("AI analyzes and categorizes each email automatically")
    with col3:
        st.markdown("#### 3️⃣ Draft Reply")
        st.markdown("AI generates contextual reply drafts for review")
    with col4:
        st.markdown("#### 4️⃣ Approve")
        st.markdown("Human reviews in Airtable, approves or edits, then sends")


def render_categories_section():
    """Render the categories overview section."""
    st.markdown("---")
    st.markdown("### 📂 Classification Categories")
    st.markdown("Emails are automatically sorted into these business categories:")

    # First row - 5 categories
    cols = st.columns(5)
    categories_list = list(CATEGORIES.items())
    for i, (cat_id, cat) in enumerate(categories_list[:5]):
        with cols[i]:
            color = get_category_color(cat_id)
            st.markdown(f"**{cat.name}**")
            st.caption(cat.description[:60] + "..." if len(cat.description) > 60 else cat.description)

    # Second row - remaining 5 categories
    cols = st.columns(5)
    for i, (cat_id, cat) in enumerate(categories_list[5:]):
        with cols[i]:
            color = get_category_color(cat_id)
            st.markdown(f"**{cat.name}**")
            st.caption(cat.description[:60] + "..." if len(cat.description) > 60 else cat.description)


def render_data_source_section():
    """Render the data source selection section."""
    st.markdown("---")
    st.markdown("### 📁 Select Data Source")
    st.markdown("Choose sample data to see the system in action, or upload your own emails.")

    col1, col2 = st.columns(2)

    emails = []

    with col1:
        st.markdown("#### Option 1: Sample Data")
        if os.path.exists("email_corpus.json"):
            sample_emails = load_corpus("email_corpus.json")
            st.success(f"✅ {len(sample_emails)} sample emails available")
            use_sample = st.button("📧 Use Sample Data", use_container_width=True)
            if use_sample:
                st.session_state.data_source = "sample"
                st.session_state.loaded_emails = sample_emails
        else:
            st.warning("No sample data found (email_corpus.json)")

    with col2:
        st.markdown("#### Option 2: Upload Your Own")
        st.file_uploader("Upload JSON file", type=["json"], label_visibility="collapsed", disabled=True)
        st.caption("📋 Custom upload available in production deployment")

    return st.session_state.get('loaded_emails', [])


def render_launch_section(emails: list, generate_replies: bool, push_to_airtable: bool):
    """Render the launch/control section."""
    st.markdown("---")
    st.markdown("### 🚀 Run Pipeline")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        num_emails = st.slider(
            "Emails to process",
            min_value=1,
            max_value=min(50, len(emails)) if emails else 10,
            value=min(5, len(emails)) if emails else 5
        )

    with col2:
        st.markdown("")  # Spacer
        st.markdown("")
        data_source = st.session_state.get('data_source', 'none')
        source_label = "sample data" if data_source == "sample" else "uploaded file"

        if emails:
            st.info(f"Ready to process **{num_emails}** randomly selected emails from {source_label} ({len(emails)} available)")
        else:
            st.warning("👆 Select a data source above to continue")

    with col3:
        generate_replies = st.checkbox("Generate AI Replies", value=True)
        push_to_airtable = st.checkbox("Push to Airtable", value=st.session_state.airtable_connected)

    # Launch button
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        launch_disabled = not emails
        if st.button(
            "🚀 Run Classification Pipeline",
            type="primary",
            use_container_width=True,
            disabled=launch_disabled
        ):
            # Randomly sample emails for variety in each run
            sampled_emails = random.sample(emails, min(num_emails, len(emails)))
            return sampled_emails, generate_replies, push_to_airtable

    return None, generate_replies, push_to_airtable


def main():
    """Main dashboard application."""
    initialize_session_state()
    check_airtable_connection()

    # Header
    st.markdown('<p class="main-header">📧 AI Email Classification & Routing</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent email triage powered by Claude AI with human-in-the-loop approval</p>', unsafe_allow_html=True)

    # Connection status in sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/email-open.png", width=60)
        st.markdown("## System Status")
        st.markdown("---")

        # Claude API
        if os.getenv("ANTHROPIC_API_KEY"):
            st.markdown("✅ Claude API Connected")
        else:
            st.markdown("❌ Claude API (set ANTHROPIC_API_KEY)")

        # Airtable
        if st.session_state.airtable_connected:
            st.markdown("✅ Airtable Connected")
            base_id = os.getenv("AIRTABLE_BASE_ID", "")
            st.caption(f"Base: {base_id[:15]}...")
            st.markdown(f"[Open Airtable →](https://airtable.com/{base_id})")
        else:
            st.markdown("⚠️ Airtable (optional)")
            st.caption("Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID in .env")

        st.markdown("---")
        st.markdown("### About")
        st.caption(
            "This demo showcases an AI-powered email classification system. "
            "Emails are automatically categorized, draft replies are generated, "
            "and everything is routed to Airtable for human review and approval."
        )

        # Clear results button in sidebar
        if st.session_state.processed_emails:
            st.markdown("---")
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state.processed_emails = []
                st.rerun()

        # Autorithm branding
        st.markdown("---")
        logo_bytes = None
        # Try local file first (development), then Streamlit secrets (production)
        if os.path.exists("autorithm_White-Main.jpg"):
            with open("autorithm_White-Main.jpg", "rb") as img_file:
                logo_bytes = img_file.read()
        elif hasattr(st, 'secrets') and 'LOGO_BASE64' in st.secrets:
            logo_bytes = base64.b64decode(st.secrets['LOGO_BASE64'])

        if logo_bytes:
            st.caption("Developed by")
            st.image(logo_bytes, width=120)
        else:
            st.markdown(
                '<div style="text-align: center; font-size: 11px; color: #9ca3af;">Developed by Autorithm</div>',
                unsafe_allow_html=True
            )

    # Create tabs
    results_count = len(st.session_state.processed_emails)
    results_label = f"📊 Results ({results_count})" if results_count > 0 else "📊 Results"

    tab1, tab2 = st.tabs(["⚙️ Configure & Run", results_label])

    # Tab 1: Configure & Run
    with tab1:
        render_hero_section()
        render_categories_section()

        # Data source selection
        emails = render_data_source_section()

        # Launch section
        emails_to_process, generate_replies, push_to_airtable = render_launch_section(
            emails,
            generate_replies=True,
            push_to_airtable=st.session_state.airtable_connected
        )

        # Process if launch button was clicked
        if emails_to_process:
            st.markdown("---")
            st.markdown("### ⏳ Processing...")

            results = process_emails(emails_to_process, generate_replies, push_to_airtable)

            st.session_state.processed_emails = results
            st.session_state.total_processed += len(results)

            st.success(f"✅ Successfully processed {len(results)} emails!")

            if push_to_airtable and st.session_state.airtable_connected:
                base_id = os.getenv("AIRTABLE_BASE_ID", "")
                st.markdown(f"[📊 View in Airtable →](https://airtable.com/{base_id})")

            st.info("👆 Click the **Results** tab above to view detailed results")

    # Tab 2: Results
    with tab2:
        if st.session_state.processed_emails:
            # Action bar at top
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{len(st.session_state.processed_emails)} emails processed** • Total all-time: {st.session_state.total_processed}")
            with col2:
                if st.session_state.airtable_connected:
                    base_id = os.getenv("AIRTABLE_BASE_ID", "")
                    st.markdown(f"[📊 Open Airtable →](https://airtable.com/{base_id})")
            with col3:
                export_data = json.dumps(st.session_state.processed_emails, indent=2)
                st.download_button(
                    "📥 Download JSON",
                    export_data,
                    file_name=f"classification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            st.markdown("---")

            # Metrics
            render_metrics(st.session_state.processed_emails)

            st.markdown("---")

            # Charts
            render_charts(st.session_state.processed_emails)

            st.markdown("---")

            # Results table
            render_results_table(st.session_state.processed_emails)

        else:
            st.info("No results yet. Go to **Configure & Run** tab to process some emails.")


if __name__ == "__main__":
    main()
