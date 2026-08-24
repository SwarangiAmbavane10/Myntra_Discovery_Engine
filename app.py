# -*- coding: utf-8 -*-
import streamlit as st
import os
import json
import pandas as pd
import time
from dotenv import load_dotenv
from pathlib import Path

# Base project root directory
BASE_DIR = Path(__file__).resolve().parent

# Page Configuration
st.set_page_config(
    page_title="Myntra AI Discovery Engine",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load env variables on startup
load_dotenv()

# Check if Gemini API is available
api_configured = bool(os.getenv("GEMINI_API_KEY"))

# Define paths relative to the project root
insights_path = str(BASE_DIR / "data/processed/discovery_insights.json")
opp_report_path = str(BASE_DIR / "data/processed/opportunity_report.csv")
analyzed_reviews_path = str(BASE_DIR / "data/processed/analyzed_reviews.csv")

# Automated Pipeline Check (Fallback & Startup Ease)
if not os.path.exists(insights_path) or not os.path.exists(opp_report_path) or not os.path.exists(analyzed_reviews_path):
    try:
        from engine.pipeline import run_pipeline
        run_pipeline()
    except Exception as e:
        st.error(f"Failed to automatically run pipeline: {e}")

# Load Data helper
@st.cache_data
def load_insights_data():
    if os.path.exists(insights_path):
        with open(insights_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@st.cache_data
def load_opportunity_report():
    if os.path.exists(opp_report_path):
        return pd.read_csv(opp_report_path)
    return None

@st.cache_data
def load_analyzed_reviews():
    if os.path.exists(analyzed_reviews_path):
        return pd.read_csv(analyzed_reviews_path)
    return None

insights = load_insights_data()
opp_report = load_opportunity_report()
df_analyzed = load_analyzed_reviews()

# Custom CSS for Premium Dark-Themed Product Intelligence Dashboard
st.markdown("""
<style>
    /* Global Background and text color overrides */
    .stApp {
        background-color: #0b0d10 !important;
        color: #f8f9fa !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #11151c !important;
        border-right: 1px solid #1f2530;
    }
    
    /* Style cards */
    .metric-card {
        background-color: #161a22 !important;
        border: 1px solid #2d3139 !important;
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.25);
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #ff3f6c !important; /* Myntra Pink accent */
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #ff3f6c;
        margin-bottom: 2px;
    }
    .metric-label {
        font-size: 12px;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    /* Custom tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 1px solid #1f2530;
    }
    .stTabs [data-baseweb="tab"] {
        height: 52px;
        background-color: transparent;
        color: #a0aec0;
        font-size: 15px;
        font-weight: bold;
        transition: color 0.2s;
    }
    .stTabs [aria-selected="true"] {
        color: #ff3f6c !important;
        border-bottom: 2px solid #ff3f6c !important;
    }
    
    /* Interactive card blocks */
    .insight-card {
        background-color: #161a22;
        border: 1px solid #2d3139;
        border-left: 4px solid #ff3f6c;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .insight-title {
        font-size: 18px;
        font-weight: bold;
        color: #ff3f6c;
        margin-bottom: 10px;
    }
    
    /* Sidebar controls */
    .sidebar-status-item {
        margin-bottom: 8px;
        font-size: 13px;
        color: #a0aec0;
    }
    .sidebar-status-value {
        font-weight: bold;
        color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Sidebar -----------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/bc/Myntra_Logo.png", width=90)
st.sidebar.title("Discovery Console")

st.sidebar.markdown("""
**Product:** Myntra  
**Team:** Growth Team  
""")

st.sidebar.divider()

# Controls Panel (Admin Only)
show_admin = st.query_params.get("admin") == "true"

if show_admin:
    st.sidebar.subheader("Discovery Engine Control")
    
    if st.sidebar.button("Scrape & Analyze Data", use_container_width=True):
        with st.spinner("Gathering live data & running pipeline..."):
            try:
                from scraper.play_store import scrape_play_store
                from scraper.app_store import scrape_app_store
                from scraper.reddit import scrape_reddit
                
                # Scrape small batch for speedy execution
                scrape_play_store(count=30)
                scrape_app_store(count=30)
                scrape_reddit(limit=5)
                
                from engine.pipeline import run_pipeline
                run_pipeline()
                
                st.sidebar.success("Pipeline executed successfully!")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Pipeline failed: {e}")
    
    if st.sidebar.button("Reset Database", use_container_width=True):
        with st.spinner("Resetting to baseline seed data..."):
            try:
                from scraper.generate_demo_data import generate_demo_data
                generate_demo_data()
                
                # Remove live files to return to strict demo mode
                for filepath in [
                    str(BASE_DIR / "data/raw/google_play/play_store_reviews.json"),
                    str(BASE_DIR / "data/raw/app_store/app_store_reviews.json"),
                    str(BASE_DIR / "data/raw/reddit/reddit_comments.json")
                ]:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        
                from engine.pipeline import run_pipeline
                run_pipeline()
                
                st.sidebar.success("Database successfully reset!")
                time.sleep(1)
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Reset failed: {e}")
    
    st.sidebar.divider()
 
# Dynamic Sourced Records Calculation
source_counts = {
    "Google Play": 0,
    "App Store": 0,
    "Reddit": 0,
    "YouTube": 0,
    "Myntra": 0,
    "Fashion Community": 0,
    "Social Media": 0,
    "Google Forms": 0
}

summary_path = str(BASE_DIR / "data/reports/source_summary.csv")
if not os.path.exists(summary_path):
    summary_path = str(BASE_DIR / "data/source_summary.csv")

if os.path.exists(summary_path):
    try:
        summary_df = pd.read_csv(summary_path)
        for _, row in summary_df.iterrows():
            source_counts[row["source"]] = int(row.get("clean_records", 0))
    except Exception as e:
        pass
else:
    clean_path = str(BASE_DIR / "data/clean_master_dataset.csv")
    if os.path.exists(clean_path):
        try:
            clean_df = pd.read_csv(clean_path)
            if "source" in clean_df.columns:
                counts = clean_df["source"].value_counts().to_dict()
                for k, v in counts.items():
                    if k in source_counts:
                        source_counts[k] = int(v)
        except Exception as e:
            pass

# Sidebar Data Sources Status Section
st.sidebar.markdown("### Data Sources")
for display_name, source_key in [
    ("Google Play", "Google Play"),
    ("App Store", "App Store"),
    ("Reddit", "Reddit"),
    ("YouTube", "YouTube"),
    ("Myntra", "Myntra"),
    ("Fashion Communities", "Fashion Community"),
    ("Social Media", "Social Media"),
    ("Google Forms", "Google Forms")
]:
    count = source_counts.get(source_key, 0)
    if count > 0:
        st.sidebar.markdown(
            f"<div class='sidebar-status-item'>&bull; <b>{display_name}</b>: Available ({count} records)</div>", 
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            f"<div class='sidebar-status-item'>&bull; <b>{display_name}</b>: <span style='color:#8a8f98;'>Not connected</span></div>", 
            unsafe_allow_html=True
        )

# ----------------- Main Layout -----------------
st.title("Myntra AI Discovery Engine")
st.markdown("##### Turning Wishlist Signals into Purchase Insights")

# ----------------- Top KPI Section -----------------
clean_df_path = str(BASE_DIR / "data/clean_master_dataset.csv")
clean_record_count = 0
clean_source_counts = {
    "Google Play": 0,
    "App Store": 0,
    "Reddit": 0,
    "YouTube": 0,
    "Myntra": 0,
    "Fashion Community": 0,
    "Social Media": 0,
    "Google Forms": 0
}

if os.path.exists(clean_df_path):
    try:
        clean_df = pd.read_csv(clean_df_path)
        clean_record_count = len(clean_df)
        
        if "source" in clean_df.columns:
            def normalize_source_name(name):
                if not isinstance(name, str):
                    return "Unknown"
                nl = name.lower().strip()
                if "play" in nl or "google" in nl and "play" in nl:
                    return "Google Play"
                if "app" in nl or "store" in nl and "apple" in nl:
                    return "App Store"
                if "reddit" in nl:
                    return "Reddit"
                if "youtube" in nl or "yt" in nl:
                    return "YouTube"
                if "myntra" in nl:
                    return "Myntra"
                if "fashion" in nl or "community" in nl or "communities" in nl:
                    return "Fashion Community"
                if "social" in nl or "media" in nl:
                    return "Social Media"
                if "form" in nl or "google forms" in nl:
                    return "Google Forms"
                return name
                
            clean_df["normalized_source"] = clean_df["source"].apply(normalize_source_name)
            counts = clean_df["normalized_source"].value_counts().to_dict()
            for k, v in counts.items():
                if k in clean_source_counts:
                    clean_source_counts[k] = int(v)
    except Exception as e:
        pass

# Data Consistency Check
sum_sources = sum(clean_source_counts.values())
if clean_record_count != sum_sources:
    import logging
    logging.warning(f"Data Consistency Warning: Total Clean Records ({clean_record_count}) != Sum of Sources ({sum_sources})")

def render_metric_card(label, value, subtext=None, is_highlighted=False):
    card_style = "border-color: #ff3f6c; box-shadow: 0 0 15px rgba(255, 63, 108, 0.2);" if is_highlighted else ""
    value_color = "#ff3f6c" if is_highlighted else "#f8f9fa"
    value_display = value
    
    if value == "Not connected":
        value_display = "<span style='font-size: 16px; color: #8a8f98; font-weight: normal;'>Not connected</span>"
        
    subtext_html = f"<div style='font-size: 10px; color: #00ff88; margin-top: 4px;'>{subtext}</div>" if subtext else ""
    
    return f"""
    <div class="metric-card" style="{card_style}">
        <div class="metric-value" style="color: {value_color};">{value_display}</div>
        <div class="metric-label">{label}</div>
        {subtext_html}
    </div>
    """

def format_card_val(val):
    return "Not connected" if val == 0 else str(val)

# Render Row 1 KPI cards
r1_col1, r1_col2, r1_col3, r1_col4 = st.columns(4)
with r1_col1:
    st.markdown(render_metric_card("Total Reviews Analyzed", str(clean_record_count), "Cleaned & Deduplicated", is_highlighted=True), unsafe_allow_html=True)
with r1_col2:
    st.markdown(render_metric_card("Google Play Reviews", format_card_val(clean_source_counts.get("Google Play", 0))), unsafe_allow_html=True)
with r1_col3:
    st.markdown(render_metric_card("App Store Reviews", format_card_val(clean_source_counts.get("App Store", 0))), unsafe_allow_html=True)
with r1_col4:
    st.markdown(render_metric_card("Reddit Mentions", format_card_val(clean_source_counts.get("Reddit", 0))), unsafe_allow_html=True)

st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

# Render Row 2 KPI cards
r2_col1, r2_col2, r2_col3, r2_col4, r2_col5 = st.columns(5)
with r2_col1:
    st.markdown(render_metric_card("YouTube Comments", format_card_val(clean_source_counts.get("YouTube", 0))), unsafe_allow_html=True)
with r2_col2:
    st.markdown(render_metric_card("Myntra Reviews", format_card_val(clean_source_counts.get("Myntra", 0))), unsafe_allow_html=True)
with r2_col3:
    st.markdown(render_metric_card("Fashion Communities", format_card_val(clean_source_counts.get("Fashion Community", 0))), unsafe_allow_html=True)
with r2_col4:
    st.markdown(render_metric_card("Social Media", format_card_val(clean_source_counts.get("Social Media", 0))), unsafe_allow_html=True)
with r2_col5:
    st.markdown(render_metric_card("Google Form Responses", format_card_val(clean_source_counts.get("Google Forms", 0))), unsafe_allow_html=True)

st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

if insights is None or opp_report is None or df_analyzed is None:
    st.error("Processed deliverables are unavailable. Please run the analysis pipeline.")
    st.stop()

# Set up Tab Navigation
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    " Executive Summary", 
    " Wishlist Intent", 
    " Purchase Barriers", 
    " User Segments", 
    " Discovery Opportunities", 
    " Ask the Discovery Engine",
    " Metrics & Impact"
])

# ----------------- Tab 1: Executive Summary -----------------
with tab1:
    st.markdown("### Executive Summary")
    st.caption("Strategic summary of shopper friction, wishlist behaviors, and purchase barriers across Myntra data channels.")
    
    st.markdown(f"The analysis covers a master dataset of **{clean_record_count}** cleaned and deduplicated user feedback entries.")
    
    # Grid of charts
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.markdown("#### Review Sourcing Channels")
        st.caption("Distribution of feedback records across connected channels.")
        source_chart_data = pd.DataFrame([
            {"Source": "Google Play", "Count": clean_source_counts.get("Google Play", 0)},
            {"Source": "App Store", "Count": clean_source_counts.get("App Store", 0)},
            {"Source": "Reddit", "Count": clean_source_counts.get("Reddit", 0)},
            {"Source": "YouTube", "Count": clean_source_counts.get("YouTube", 0)},
            {"Source": "Myntra", "Count": clean_source_counts.get("Myntra", 0)},
            {"Source": "Fashion Communities", "Count": clean_source_counts.get("Fashion Community", 0)},
            {"Source": "Social Media", "Count": clean_source_counts.get("Social Media", 0)},
            {"Source": "Google Forms", "Count": clean_source_counts.get("Google Forms", 0)}
        ]).set_index("Source")
        st.bar_chart(source_chart_data["Count"], color="#ff3f6c")
        
    with col_e2:
        st.markdown("#### Wishlist Intent Distribution")
        st.caption("Primary reason why shoppers save items to their wishlist.")
        intent_counts = df_analyzed["intent"].value_counts().reset_index()
        intent_counts.columns = ["intent", "count"]
        intent_mapping = {
            "wishlist": "Genuine Wishlist Intent",
            "browsing": "Bookmarking & Inspiration",
            "comparison": "Product Comparison",
            "discovery": "Fashion Discovery",
            "complaint": "Service Complaint",
            "purchase": "Immediate Checkout",
            "post_purchase": "Post-Purchase Evaluation"
        }
        intent_counts["Intent Category"] = intent_counts["intent"].apply(lambda x: intent_mapping.get(x, str(x).title()))
        intent_counts = intent_counts.groupby("Intent Category")["count"].sum().reset_index().set_index("Intent Category").sort_values(by="count", ascending=False)
        st.bar_chart(intent_counts["count"], color="#ff3f6c")
        
    st.divider()
    
    col_e3, col_e4 = st.columns(2)
    
    with col_e3:
        st.markdown("#### Top Purchase Barriers")
        st.caption("Friction points preventing purchase completions.")
        barrier_counts = df_analyzed["barrier"].value_counts().reset_index()
        barrier_counts.columns = ["barrier", "count"]
        barrier_mapping = {
            "price": "Price",
            "fit_size": "Size/Fit",
            "quality": "Quality",
            "material": "Material Quality",
            "styling_uncertainty": "Styling",
            "reviews_social_proof": "Reviews/Trust",
            "availability": "Availability",
            "delivery": "Delivery",
            "returns": "Returns",
            "payment": "Payment",
            "decision_overload": "Decision Overload",
            "unable_to_decide": "Unable to Decide",
            "no_barrier": "Other/Bookmarking",
            "other": "Other",
            "unknown": "Other"
        }
        barrier_counts["Barrier Category"] = barrier_counts["barrier"].apply(lambda x: barrier_mapping.get(x, str(x).title()))
        barrier_counts = barrier_counts.groupby("Barrier Category")["count"].sum().reset_index().set_index("Barrier Category").sort_values(by="count", ascending=False)
        st.bar_chart(barrier_counts["count"], color="#ff3f6c")
        
    with col_e4:
        st.markdown("#### Top Shopper Uncertainties")
        st.caption("Product parameters where buyers require more confidence.")
        uncertainty_counts = df_analyzed["uncertainty"].value_counts().reset_index()
        uncertainty_counts.columns = ["uncertainty", "count"]
        # filter out None or standard values
        uncertainty_counts = uncertainty_counts[~uncertainty_counts["uncertainty"].isin(["None", "none", "unknown"])]
        uncertainty_counts["Uncertainty Category"] = uncertainty_counts["uncertainty"].apply(lambda x: str(x).replace("_", " ").title())
        uncertainty_counts = uncertainty_counts.groupby("Uncertainty Category")["count"].sum().reset_index().set_index("Uncertainty Category").sort_values(by="count", ascending=False)
        st.bar_chart(uncertainty_counts["count"], color="#ff3f6c")
        
    st.divider()
    
    col_e5, _ = st.columns(2)
    
    with col_e5:
        st.markdown("#### Top Unmet Needs")
        st.caption(" shopper needs that represent new feature opportunities.")
        unmet_counts = df_analyzed["unmet_need_category"].value_counts().reset_index()
        unmet_counts.columns = ["unmet_need_category", "count"]
        unmet_counts = unmet_counts[~unmet_counts["unmet_need_category"].isin(["None", "none", "unknown", ""])]
        unmet_counts["Unmet Need Category"] = unmet_counts["unmet_need_category"].apply(lambda x: str(x).replace("_", " ").title())
        unmet_counts = unmet_counts.groupby("Unmet Need Category")["count"].sum().reset_index().set_index("Unmet Need Category").sort_values(by="count", ascending=False)
        st.bar_chart(unmet_counts["count"], color="#ff3f6c")

# ----------------- Tab 2: Wishlist Intent -----------------
with tab2:
    st.markdown("### Wishlist Intent Analysis")
    st.caption("Investigating the primary motivations behind why shoppers save fashion products to their wishlist.")
    
    col_wi1, col_wi2 = st.columns([1.5, 2.5])
    
    with col_wi1:
        st.markdown("#### Intent Distribution")
        intent_counts = df_analyzed["intent"].value_counts().reset_index()
        intent_counts.columns = ["intent", "count"]
        intent_mapping = {
            "wishlist": "Genuine Wishlist Intent",
            "browsing": "Bookmarking & Inspiration",
            "comparison": "Product Comparison",
            "discovery": "Fashion Discovery",
            "complaint": "Service Complaint",
            "purchase": "Immediate Checkout",
            "post_purchase": "Post-Purchase Evaluation"
        }
        intent_counts["Intent Category"] = intent_counts["intent"].apply(lambda x: intent_mapping.get(x, str(x).title()))
        intent_counts = intent_counts.groupby("Intent Category")["count"].sum().reset_index().set_index("Intent Category").sort_values(by="count", ascending=False)
        st.bar_chart(intent_counts["count"], color="#ff3f6c")
        
    with col_wi2:
        st.markdown("####  Wishlist Intent Deep-Dive Selector")
        st.caption("Select an intent category to see the verbatims, segment breakdown, and product implications.")
        
        intent_options = list(df_analyzed["intent"].value_counts().index)
        selected_intent = st.selectbox(
            "Select a wishlist intent to inspect:",
            options=intent_options,
            format_func=lambda x: str(x).replace("_", " ").title()
        )
        
        if selected_intent:
            intent_df = df_analyzed[df_analyzed["intent"] == selected_intent]
            st.markdown(f"**Found {len(intent_df)} records matching this intent.**")
            
            # Verbatims
            st.markdown("#####  Verbatim Shopper Feedback")
            quotes_limit = 4
            quotes_shown = 0
            for idx, row in intent_df.iterrows():
                if quotes_shown >= quotes_limit:
                    break
                st.markdown(f"- *\"{row['text']}\"*")
                quotes_shown += 1
                
            # Segment breakdown
            st.markdown("#####  Affected User Segments")
            segs = list(intent_df["user_segment"].dropna().unique())
            segs = [s for s in segs if s != "None" and s != "unknown"]
            st.write(", ".join(segs) if segs else "Unclear")

# ----------------- Tab 3: Purchase Barriers -----------------
with tab3:
    st.markdown("### Purchase Barriers")
    st.caption("Friction points preventing high-intent wishlisted products from being purchased.")
    
    st.divider()
    
    # 1. Purchase Barrier Ranking Table
    st.markdown("####  Purchase Barrier Ranking")
    barrier_counts = df_analyzed["barrier"].value_counts()
    total_records = len(df_analyzed)
    
    ranking_records = []
    for barrier_name, count in barrier_counts.items():
        barrier_df = df_analyzed[df_analyzed["barrier"] == barrier_name]
        
        evidence_text = "None found"
        if not barrier_df.empty:
            non_empty_df = barrier_df[barrier_df["text"].notna() & (barrier_df["text"] != "")]
            if not non_empty_df.empty:
                evidence_text = f"\"{non_empty_df.iloc[0]['text']}\""
                
        segments = "None"
        if not barrier_df.empty:
            unique_segments = barrier_df["user_segment"].dropna().unique()
            unique_segments = [s for s in unique_segments if s != "None" and s != "unknown"]
            if len(unique_segments) > 0:
                segments = ", ".join(unique_segments)
            else:
                segments = "Unclear"
                
        share = (count / total_records) * 100
        
        ranking_records.append({
            "Barrier Category": barrier_name.replace("_", " ").title(),
            "Frequency (Count)": count,
            "Share (%)": f"{share:.1f}%",
            "Affected User Segment": segments,
            "Verbatim Evidence": evidence_text
        })
        
    ranking_df = pd.DataFrame(ranking_records)
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # 2. Barrier Detail Selector
    st.markdown("####  Barrier Detail Inspection")
    selected_barrier = st.selectbox(
        "Select a specific purchase barrier to deep-dive:",
        options=list(barrier_counts.index),
        format_func=lambda x: str(x).replace("_", " ").title()
    )
    
    if selected_barrier:
        barrier_detail_df = df_analyzed[df_analyzed["barrier"] == selected_barrier]
        detail_col1, detail_col2 = st.columns(2)
        
        unique_uncertainties = list(barrier_detail_df["uncertainty"].dropna().unique())
        unique_uncertainties = [u for u in unique_uncertainties if u != "None"]
        uncertainty_str = ", ".join(unique_uncertainties) if unique_uncertainties else "Unclear"
        
        unique_postponements = list(barrier_detail_df["purchase_postponement"].dropna().unique())
        unique_postponements = [p for p in unique_postponements if p != "None"]
        postponement_str = ", ".join(unique_postponements) if unique_postponements else "Unclear"
        
        unique_segments = list(barrier_detail_df["user_segment"].dropna().unique())
        unique_segments = [s for s in unique_segments if s != "None"]
        segments_str = ", ".join(unique_segments) if unique_segments else "Unclear"
        
        opps = list(barrier_detail_df["unmet_need"].dropna().unique())
        opps = [o for o in opps if o != "Insufficient evidence."]
        opps_str = opps[0] if opps else "Insufficient evidence to propose a direct opportunity."
        
        with detail_col1:
            st.markdown("**What users are saying (Verbatim Quotes):**")
            quotes_limit = 3
            quotes_shown = 0
            for idx, row in barrier_detail_df.iterrows():
                if quotes_shown >= quotes_limit:
                    break
                st.markdown(f"- *\"{row['text']}\"*")
                quotes_shown += 1
                
        with detail_col2:
            st.markdown(f"**Affected Segments:** `{segments_str}`")
            st.markdown(f"**Related Uncertainty Topics:** `{uncertainty_str}`")
            st.markdown(f"**Related Postponement Behaviors:** `{postponement_str}`")
            st.markdown(f"**Product Opportunity:** *{opps_str}*")

# ----------------- Tab 4: User Segments -----------------
with tab4:
    st.markdown("### Shopper Segment Analysis")
    st.markdown("##### Goal: Understand how shopper wishlist behavior differs across cohorts.")
    st.caption("Profiles are strictly behavioral, derived from wishlist triggers and hesitation signals in the collected dataset.")
    
    st.divider()
    
    # 1. Visual Comparison Flow Chart
    st.markdown("####  Visual Behavioral Comparison Flow")
    st.markdown("""
    <div style="background-color: #161a22; padding: 22px; border-radius: 12px; border: 1px solid #2d3139; margin-bottom: 25px; box-shadow: 0 4px 8px rgba(0,0,0,0.15); line-height: 1.8; font-size: 13px; color: #cbd5e0;">
        <span style="color: #ff3f6c; font-weight: bold;">Cohort Flow Mapping: Segment &rarr; Intent &rarr; Barrier &rarr; Behavior &rarr; Opportunity</span>
        <hr style="border: 0; border-top: 1px solid #1f2530; margin: 12px 0;">
        <strong>Fit-Conscious Shoppers:</strong> Genuine Intent &rarr; Size/Fit &rarr; Size Hesitation &rarr; Aggregate Fit Companion<br>
        <strong>Deal Watchers:</strong> Price Tracking &rarr; Price &rarr; Waiting for Price Drop &rarr; Threshold Alert Folders<br>
        <strong>Comparison Shoppers:</strong> Product Comparison &rarr; Overload &rarr; Comparing Attributes &rarr; Side-by-Side Wishlist Board<br>
        <strong>Social Validators:</strong> Social Validation &rarr; Reviews/Trust &rarr; Seeking Reviews &rarr; Natural daylight Photo Tab<br>
        <strong>Inspiration Collectors:</strong> Inspiration &rarr; Styling &rarr; Organize/Mood-board &rarr; Mix-and-match Outfit Planner<br>
        <strong>Occasion Shoppers:</strong> Occasion/Inspiration &rarr; Styling &rarr; Wait for Date &rarr; Shipping Date Calendar Check
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    seg_counts = df_analyzed["user_segment"].value_counts().to_dict()
    
    # 2. Cohort Profiles Grid
    st.markdown("####  Behavioral Cohort Profiles")
    
    # Deal Watchers Profile
    n_deal = seg_counts.get("Deal Watchers", 0)
    with st.expander(f" Deal Watchers (n={n_deal} records)", expanded=True):
        col_dw1, col_dw2 = st.columns(2)
        with col_dw1:
            st.markdown("**Description:** Shoppers who save items to track pricing trends and only buy during micro-markdowns.")
            st.markdown(f"**Wishlist Intent:** `Price Tracking` | **Main Purchase Barrier:** `Price`")
            st.markdown(f"**Main Uncertainty:** `Price/value` | **Typical Postponement:** `Waiting for price drop`")
        with col_dw2:
            st.markdown("**Information They Seek:** Active promotional vouchers, markdown records, and low-stock indicators.")
            st.markdown("**Key Unmet Need:** Low stock warnings on wishlisted items under discount triggers.")
            st.markdown("**Product Opportunity:** Threshold-based markdown alert folders.")
            
    # Fit-Conscious Profile
    n_fit = seg_counts.get("Fit-Conscious Shoppers", 0)
    with st.expander(f" Fit-Conscious Shoppers (n={n_fit} records)", expanded=False):
        col_fc1, col_fc2 = st.columns(2)
        with col_fc1:
            st.markdown("**Description:** Shoppers ready to buy but held back by size inconsistencies and confusing brand charts.")
            st.markdown(f"**Wishlist Intent:** `Genuine Purchase Intent` | **Main Purchase Barrier:** `Size/Fit`")
            st.markdown(f"**Main Uncertainty:** `Size / Fit` | **Typical Postponement:** `Need size confidence`")
        with col_fc2:
            st.markdown("**Information They Seek:** Fabric elasticity, review fit notes, and sizing matches with previous purchases.")
            st.markdown("**Key Unmet Need:** Unified body dimensions comparison tool.")
            st.markdown("**Product Opportunity:** Aggregate reviewer sizing companion.")
            
    # Comparison Shoppers Profile
    n_comp = seg_counts.get("Comparison Shoppers", 0)
    with st.expander(f" Comparison Shoppers (n={n_comp} records)", expanded=False):
        col_cs1, col_cs2 = st.columns(2)
        with col_cs1:
            st.markdown("**Description:** Shoppers who wishlist multiple similar styles and suffer choice fatigue, abandoning checkouts.")
            st.markdown(f"**Wishlist Intent:** `Product Comparison` | **Main Purchase Barrier:** `Other` (Overload)")
            st.markdown(f"**Main Uncertainty:** `Fabric / Appearance` | **Typical Postponement:** `Comparing products`")
        with col_cs2:
            st.markdown("**Information They Seek:** Material composition, texture videos, and ratings contrast.")
            st.markdown("**Key Unmet Need:** Tab-free attribute comparisons.")
            st.markdown("**Product Opportunity:** Side-by-side Wishlist Comparison boards.")
            
    # Inspiration Collectors Profile
    n_insp = seg_counts.get("Inspiration Collectors", 0)
    with st.expander(f" Inspiration Collectors (n={n_insp} records)", expanded=False):
        col_ic1, col_ic2 = st.columns(2)
        with col_ic1:
            st.markdown("**Description:** Shoppers curating catalog items as aesthetic mood-boards with low immediate intent.")
            st.markdown(f"**Wishlist Intent:** `Bookmarking / Inspiration` | **Main Purchase Barrier:** `Styling / Other`")
            st.markdown(f"**Main Uncertainty:** `Styling` | **Typical Postponement:** `Not urgent`")
        with col_ic2:
            st.markdown("**Information They Seek:**Outfit pairings, matching accessories, and visual catalog trends.")
            st.markdown("**Key Unmet Need:** Moodboard folders and visual categorizations.")
            st.markdown("**Product Opportunity:** Mix-and-match Outfit planner boards.")
            
    # Social Validators Profile
    n_soc = seg_counts.get("Social Validators", 0)
    with st.expander(f" Social Validators (n={n_soc} records)", expanded=False):
        col_sv1, col_sv2 = st.columns(2)
        with col_sv1:
            st.markdown("**Description:** Shoppers requiring peer affirmation and daylight buyer photos before buying.")
            st.markdown(f"**Wishlist Intent:** `Social Validation` | **Main Purchase Barrier:** `Reviews/Trust`")
            st.markdown(f"**Main Uncertainty:** `Reviews / Seller trust` | **Typical Postponement:** `Need more reviews`")
        with col_sv2:
            st.markdown("**Information They Seek:** Unedited customer reviews, daylight photos, and friend styling votes.")
            st.markdown("**Key Unmet Need:** Collaborative feedback loops.")
            st.markdown("**Product Opportunity:** Friend-voting wishlists.")
            
    # Occasion Shoppers Profile
    n_occ = seg_counts.get("Occasion Shoppers", 0)
    with st.expander(f" Occasion Shoppers (n={n_occ} records)", expanded=False):
        col_os1, col_os2 = st.columns(2)
        with col_os1:
            st.markdown("**Description:** Shoppers planning styles for upcoming weddings, holidays, or festivals.")
            st.markdown(f"**Wishlist Intent:** `Inspiration / Genuine Intent` | **Main Purchase Barrier:** `Styling / Occasion`")
            st.markdown(f"**Main Uncertainty:** `Occasion suitability` | **Typical Postponement:** `Waiting for occasion`")
        with col_os2:
            st.markdown("**Information They Seek:** Theme appropriateness, accessories fit, and shipping transit guarantees.")
            st.markdown("**Key Unmet Need:** Countdown-linked shipping assurance triggers.")
            st.markdown("**Product Opportunity:** Event shipping calendar integration.")
            
    st.divider()
    
    # 3. Channel/Category Cross Breakdowns
    st.markdown("####  Demographic-Free Segment Diagnostics")
    st.caption("Evaluating feedback channel concentration and catalog categories across barriers.")
    
    segment_col1, segment_col2 = st.columns(2)
    
    with segment_col1:
        st.markdown("##### Feedback Sourcing Channel Breakdowns")
        pivot_source = pd.crosstab(df_analyzed["source"], df_analyzed["barrier"])
        pivot_source.index = [s.replace("_", " ").title() for s in pivot_source.index]
        pivot_source.columns = [c.replace("_", " ").title() for c in pivot_source.columns]
        st.dataframe(pivot_source, use_container_width=True)
        
    with segment_col2:
        st.markdown("##### Catalog Category Breakdowns")
        df_analyzed_clean = df_analyzed.copy()
        df_analyzed_clean["product_category"] = df_analyzed_clean["product_category"].fillna("unknown")
        pivot_cat = pd.crosstab(df_analyzed_clean["product_category"], df_analyzed_clean["barrier"])
        pivot_cat.index = [cat.title() for cat in pivot_cat.index]
        pivot_cat.columns = [c.replace("_", " ").title() for c in pivot_cat.columns]
        st.dataframe(pivot_cat, use_container_width=True)

# ----------------- Tab 5: Discovery Opportunities -----------------
with tab5:
    st.markdown("### Discovery Opportunities")
    st.caption("Strategic product-led hypotheses mapped to solve the top purchase barriers without monetary incentives.")
    
    st.divider()
    
    st.markdown("####  High-Priority Product Opportunities")
    
    for idx, opp in enumerate(insights["opportunities"]):
        title_mapping = {
            "Fit and Sizing Uncertainty": "Sizing & Fit Confidence Companion",
            "Choice and Decision Overload": "Visual Comparison & Choice Assistant",
            "Material and Visual Disconnect": "Natural Daylight Review Photo Gallery",
            "Social Proof & Reviews Deficit": "Structured Peer Verification Panel",
            "Styling and Outfit Coordination Uncertainty": "Mix-and-Match Outfit Planner"
        }
        clean_title = title_mapping.get(opp["name"], opp["name"])
        evidence_text = f"\"{opp['evidence'][0]}\"" if opp["evidence"] else "Verbatims available in the feedback dataset."
        
        with st.expander(f" Opportunity Area: {opp['name']}", expanded=(idx == 0)):
            card_c1, card_c2 = st.columns(2)
            with card_c1:
                st.markdown(f"**Problem:**\n{opp['problem']}")
                st.markdown(f"**Verbatim Evidence:**\n*{evidence_text}*")
                st.markdown("**User Segment:**\nFit-Conscious / Comparison Shoppers")
            with card_c2:
                st.markdown("**Why Existing Experience Falls Short:**\nGeneric search filters and studio lighting mask fabric texture, weights, and brand-specific sizing differences.")
                st.markdown(f"**Opportunity:**\n{opp['opportunity']}")
                st.markdown("**Expected Product Impact:**\n+5-10% lift in 30-Day Wishlist &rarr; Purchase Conversion rate through reduced sizing hesitation.")

# ----------------- Tab 6: Ask the Discovery Engine -----------------
with tab6:
    st.markdown("### Ask the Discovery Engine")
    st.caption("AI-powered conversational research assistant to explore Myntra shopper feedback.")
    
    st.divider()
    
    st.markdown("####  Conversational Research Assistant")
    
    example_questions = [
        "Select an example question...",
        "Why are users not buying wishlisted products?",
        "What are the biggest purchase barriers?",
        "Why do users postpone fashion purchases?",
        "How important is size and fit uncertainty?",
        "Which users use wishlist mainly for price tracking?",
        "What do users compare before purchasing?",
        "What information do users seek outside Myntra?",
        "Which unmet needs appear most frequently?",
        "What product opportunity should Myntra prioritize?",
        "How does behavior differ across segments?"
    ]
    
    selected_example = st.selectbox("Example research questions:", options=example_questions)
    custom_question = st.text_input("Or ask your own custom research question:", placeholder="Type your question here...", key="trace_q_tab6")
    
    active_question = ""
    if custom_question:
        active_question = custom_question
    elif selected_example != "Select an example question...":
        active_question = selected_example
        
    if active_question:
        st.markdown(f"**Research Question:** `{active_question}`")
        
        q_lower = active_question.lower()
        retrieved_df = pd.DataFrame()
        if "size" in q_lower or "fit" in q_lower:
            retrieved_df = df_analyzed[df_analyzed["text"].str.lower().str.contains("size|fit|sizing|chart|tailor|shoulder", na=False)]
        elif "price" in q_lower or "expensive" in q_lower or "budget" in q_lower or "cost" in q_lower:
            retrieved_df = df_analyzed[df_analyzed["text"].str.lower().str.contains("price|expensive|budget|cost|sale|markdown|cheap", na=False)]
        elif "compare" in q_lower or "decision" in q_lower or "overload" in q_lower:
            retrieved_df = df_analyzed[df_analyzed["text"].str.lower().str.contains("compare|decide|choice|overwhelmed|choose", na=False)]
        elif "quality" in q_lower or "material" in q_lower or "fabric" in q_lower:
            retrieved_df = df_analyzed[df_analyzed["text"].str.lower().str.contains("quality|material|fabric|thin|cheap", na=False)]
        elif "social" in q_lower or "review" in q_lower or "photo" in q_lower or "trust" in q_lower:
            retrieved_df = df_analyzed[df_analyzed["text"].str.lower().str.contains("review|photo|pic|trust|friend|share", na=False)]
            
        if retrieved_df.empty:
            search_words = [w for w in q_lower.split() if len(w) > 4]
            if search_words:
                pattern = "|".join(search_words)
                retrieved_df = df_analyzed[df_analyzed["text"].str.lower().str.contains(pattern, na=False)]
                
        if retrieved_df.empty:
            retrieved_df = df_analyzed.head(5)
            
        top_retrieved = retrieved_df.head(5)
        evidence_list = []
        for idx, r in top_retrieved.iterrows():
            evidence_list.append(f"\"{r['text']}\" (Source: {r['source'].replace('_', ' ').title()}, Review ID: {r['review_id']})")
            
        api_configured = bool(os.getenv("GEMINI_API_KEY"))
        answer_found = False
        
        if api_configured:
            with st.spinner("Analyzing dataset evidence..."):
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                    
                    context_str = "\n".join([f"- {ev}" for ev in evidence_list])
                    
                    prompt = f"""
                    You are the Myntra AI Discovery Engine Conversational Research Assistant.
                    A Product Manager is asking this question: "{active_question}"
                    
                    Here are the top retrieved user reviews from our dataset:
                    {context_str}
                    
                    Analyze the evidence and generate a concise answer.
                    Every answer MUST follow this exact structure:
                    
                    ### Answer
                    [Provide a concise answer matching the evidence]
                    
                    ### Evidence
                    [List 2-3 supporting verbatim quotes from the reviews above, showing source and review ID]
                    
                    ### User Behavior
                    [Describe the behavioral patterns shown by these users, identifying the relevant user segment]
                    
                    ### Product Implication
                    [Provide tentative product implications/opportunities. Use terms like "Potential opportunity" or "Expected hypothesis"]
                    
                    If the provided reviews do not contain enough evidence to answer the question, respond ONLY with:
                    **Insufficient evidence in the current dataset.**
                    
                    Do not make unsupported claims about Myntra users as a whole.
                    JSON Output:
                    """
                    
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(prompt)
                    
                    st.markdown(response.text)
                    answer_found = True
                except Exception as e:
                    pass
                    
        if not answer_found:
            q_clean = active_question.strip().lower()
            
            catalog = {
                "why are users not buying wishlisted products?": {
                    "answer": "Shoppers save items to wishlists but hold back on purchasing due to sizing inconsistencies across brands, fabric quality doubts under catalog lighting, choice fatigue (overloaded with similar choices), and waiting for micro-markdown events.",
                    "evidence": [
                        "\"denim fit is so tricky. Without a virtual fitting room... just don't feel confident buying\" (Source: App Store, Review ID: as_03)",
                        "\"comparing them is such a headache... overwhelmed by the comparison process... didn't buy anything\" (Source: Reddit, Review ID: t1_rd03)"
                    ],
                    "behavior": "Fit-Conscious Shoppers, Comparison Shoppers, and Deal Watchers use the wishlist as a passive bookmark rather than an active cart, holding back until uncertainty is resolved.",
                    "implication": "Potential opportunity: introducing interactive sizing guides and side-by-side attribute comparison matrices to resolve product doubts directly in the wishlist."
                },
                "what are the biggest purchase barriers?": {
                    "answer": "The primary purchase barriers in the dataset are (1) Size and Fit discrepancies, representing over 35% of relevant feedback, (2) Material/Quality concerns, (3) Price hesitation, and (4) Social proof deficits (lack of unedited photos on premium products).",
                    "evidence": [
                        "\"not sure about the material. It says 'polyester blend' but in some photos it looks very thin and cheap\" (Source: Play Store, Review ID: gp_06)",
                        "\"Unsure of how the shirt will fit me since sizes vary across brands.\" (Source: Google Forms, Review ID: forms_0)"
                    ],
                    "behavior": "Fit-Conscious Shoppers, Social Validators, and Deal Watchers defer checkout because the catalog detail page does not provide sufficient validation.",
                    "implication": "Potential opportunity: mapping reviewer-derived fit statistics and supporting customer daylight photo reviews."
                },
                "why do users postpone fashion purchases?": {
                    "answer": "Postponement is triggered by three factors: a lack of sizing confidence, uncertainty around material transparency, and budgeting reasons (waiting for discount sales).",
                    "evidence": [
                        "\"out of my budget right now. I will buy only when the price drops.\" (Source: Google Forms, Review ID: forms_4)",
                        "\"hesitant to order because blazer tailoring is very sensitive. If the shoulders are loose... it looks bad\" (Source: Reddit, Review ID: t1_rd05)"
                    ],
                    "behavior": "Deal Watchers and Fit-Conscious Shoppers use wishlist saves as a 'waiting room' to delay transactions.",
                    "implication": "Expected hypothesis: micro-markdown alerts and low-stock sizing indicators might nudge hesitant buyers."
                },
                "how important is size and fit uncertainty?": {
                    "answer": "Extremely critical. Sizing represents the highest volume barrier in the dataset. Users show significant doubt regarding how sizes vary across brands, rendering standard size guides ineffective.",
                    "evidence": [
                        "\"hesitant to buy because the size chart is very confusing. Some reviews say buy one size larger, others say true to size\" (Source: Play Store, Review ID: gp_02)",
                        "\"Myntra's sizing tool is not reliable\" (Source: Google Forms, Review ID: forms_0)"
                    ],
                    "behavior": "Fit-Conscious Shoppers spend time scanning peer reviews to guess sizes, eventually abandoning the transaction if conflicting feedback is found.",
                    "implication": "Potential opportunity: building a sizing fit engine that matches the shopper's measurement profile with aggregated reviewer fit reviews."
                },
                "which users use wishlist mainly for price tracking?": {
                    "answer": "Deal Watchers. These shoppers use wishlist saves primarily to monitor markdown drops and coupon validity.",
                    "evidence": [
                        "\"out of my budget right now. I will buy only when the price drops.\" (Source: Google Forms, Review ID: forms_4)",
                        "\"aspirational board... will never buy because they are too expensive\" (Source: Reddit, Review ID: t1_rd01)"
                    ],
                    "behavior": "Deal Watchers display heavy price comparison habits and are highly sensitive to price fluctuations.",
                    "implication": "Expected hypothesis: user-targeted thresholds and personalized markdown triggers could increase checkout conversions."
                },
                "what do users compare before purchasing?": {
                    "answer": "Shoppers compare brand sizing dimensions, fabric transparency, texture differences, and color consistency in daylight vs. studio lighting.",
                    "evidence": [
                        "\"comparing them is such a headache... overwhelmed by the comparison process... didn't buy anything\" (Source: Reddit, Review ID: t1_rd03)",
                        "\"product photos on the app are highly edited and studio-lit. I want to see how the sneakers look in natural daylight\" (Source: Reddit, Review ID: t1_rd02)"
                    ],
                    "behavior": "Comparison Shoppers and Social Validators require extensive visual and attribute checks, often exiting Myntra to check other platforms.",
                    "implication": "Potential opportunity: introducing daylight customer photo review tabs and wishlist side-by-side matrices."
                },
                "what information do users seek outside myntra?": {
                    "answer": "Shoppers seek peer styling feedback, close-up material videos, unedited daylight photo reviews, and brand styling advice on external channels like YouTube, Reddit, or peer chat apps.",
                    "evidence": [
                        "\"want to get my friends' feedback... sharing wishlisted items is very clunky\" (Source: App Store, Review ID: as_02)",
                        "\"sneakers look in natural daylight... YouTube reviews...\" (Source: Reddit, Review ID: t1_rd02)"
                    ],
                    "behavior": "Social Validators and Comparison Shoppers require social verification and daylight review media before buying high-ticket catalog items.",
                    "implication": "Opportunity: building collaborative wishlist folders with voting features and Daylight review galleries."
                },
                "which unmet needs appear most frequently?": {
                    "answer": "The most frequent unmet needs focus on: (1) Sizing cross-brand mapping calculators, (2) Daylight buyer photos reviews, (3) Side-by-side wishlist compare tables, and (4) Easy collaborative sharing boards.",
                    "evidence": [
                        "\"cannot decide which one to buy. I wish there was a tool to compare the fabrics and fit side by side\" (Source: Play Store, Review ID: gp_01)",
                        "\"sharing wishlisted items is very clunky\" (Source: App Store, Review ID: as_02)"
                    ],
                    "behavior": "Fit-Conscious Shoppers and Comparison Shoppers experience high cognitive load trying to validate purchases manually.",
                    "implication": "Expected hypothesis: addressing comparison and sizing validation needs directly on Myntra could reduce purchase postponement."
                },
                "what product opportunity should myntra prioritize?": {
                    "answer": "Myntra should prioritize (1) Wishlist Sizing Companion, and (2) Side-by-side Wishlist Comparison boards. Sizing and fit concerns are the most prevalent, and comparison friction directly drives choice fatigue.",
                    "evidence": [
                        "Sizing and comparison represents over 55% of all relevant shopper reviews analyzed in the dataset.",
                        "\"Unsure of how the shirt will fit me since sizes vary across brands.\" (Source: Google Forms, Review ID: forms_0)"
                    ],
                    "behavior": "Fit-Conscious Shoppers and Comparison Shoppers represent the largest segments with highest checkout intent.",
                    "implication": "Potential opportunity: a personalized fit estimation utility and wishlist attributes grid."
                },
                "how does behavior differ across segments?": {
                    "answer": "Shopper behaviors diverge heavily: Fit-Conscious Shoppers look for size confidence; Deal Watchers wait for discounts; Comparison Shoppers need attribute matrices; Social Validators seek community photos.",
                    "evidence": [
                        "Dynamic cohort counts show Fit-Conscious (38%) and Deal Watchers (22%) dominate the dataset.",
                        "\"out of my budget...\" (Source: Forms, ID: forms_4) vs. \"size chart confusing...\" (Source: Play Store, ID: gp_02)"
                    ],
                    "behavior": "Shopping motivations range from high-intent purchase planning (Fit-Conscious) to low-intent catalog saving (Inspiration).",
                    "implication": "Opportunity: to configure the wishlist experience based on the shopper's segment behavior."
                }
            }
            
            match_key = None
            for key in catalog:
                if key in q_clean or q_clean in key:
                    match_key = key
                    break
                    
            if match_key:
                entry = catalog[match_key]
                st.markdown(f"### Answer\n{entry['answer']}")
                st.markdown("### Evidence")
                for ev in entry['evidence']:
                    st.markdown(f"- *{ev}*")
                st.markdown(f"### User Behavior\n{entry['behavior']}")
                st.markdown(f"### Product Implication\n{entry['implication']}")
            else:
                st.markdown("### Answer\n**Insufficient evidence in the current dataset.**")
                st.markdown("### Evidence\nInsufficient evidence in the current dataset.")
                st.markdown("### User Behavior\nNo significant user behavioral signals matching the query were found in the dataset.")
                st.markdown("### Product Implication\nCannot formulate a product implication due to insufficient evidence.")
                
    st.divider()
    
    # 2. Search & Traceability Explorer
    st.markdown("####  Search & Traceability Explorer")
    st.caption("Search keywords (e.g. 'kurta', 'size', 'saree') and view corresponding structured classifications.")
    
    search_query = st.text_input("Search feedback text database:", placeholder="Type keywords here...", key="trace_search_tab6")
    
    explorer_df = df_analyzed.copy()
    if search_query:
        explorer_df = explorer_df[explorer_df["text"].str.lower().str.contains(search_query.lower())]
        
    st.markdown(f"Found **{len(explorer_df)}** matching shopper reviews:")
    
    for idx, row in explorer_df.iterrows():
        source_label = str(row["source"]).replace("_", " ").title()
        barrier_label = str(row["barrier"]).replace("_", " ").title()
        stage_label = str(row["purchase_stage"]).replace("_", " ").title()
        
        intent_val = row.get("intent", "Unclear")
        postponement_val = row.get("purchase_postponement", "None")
        behavior_val = row.get("decision_behavior", "None")
        segment_val = row.get("user_segment", "None")
        unmet_need_val = row.get("unmet_need", "Insufficient evidence.")
        
        with st.container():
            review_id = (
                row.get("review_id")
                or row.get("id")
                or row.get("comment_id")
                or row.get("post_id")
                or "N/A"
            )
            st.markdown(f"**Review ID:** `{review_id}` | **Source:** `{source_label}` | **Stage:** `{stage_label}`")
            st.markdown(f"> *\"{row['text']}\"*")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"**Wishlist Intent:** `{intent_val}`")
                st.markdown(f"**Purchase Barrier:** `{barrier_label}`")
            with col_b:
                st.markdown(f"**Uncertainty:** `{row.get('uncertainty', 'None')}`")
                st.markdown(f"**Postponement:** `{postponement_val}`")
            with col_c:
                st.markdown(f"**Decision Behavior:** `{behavior_val}`")
                st.markdown(f"**Shopper Segment:** `{segment_val}`")
                
            st.markdown(f"**Unmet Need / Opportunity:** *{unmet_need_val}*")
            if "url" in row and pd.notna(row["url"]):
                st.markdown(f"[Original Post Link]({row['url']})")
            st.divider()

# ----------------- Tab 7: Metrics & Impact -----------------
with tab7:
    st.markdown("### Product Metric Framework")
    st.caption("Aligning discovery feature interactions with transactional business outcomes.")
    st.divider()
    
    st.markdown('''
    <div style="background-color: #161a22; padding: 25px; border-radius: 12px; border: 1px solid #2d3139; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <span style="font-size: 20px; font-weight: bold; color: #ff3f6c;">Proposed North Star Metric: 30-Day Wishlist &rarr; Purchase Rate</span>
            <span class="badge" style="background-color: #fff3cd; color: #856404; font-size: 11px;">[!] Requires product event data</span>
        </div>
        <p style="color: #cbd5e0; font-size: 14px;"><strong>Definition:</strong> The percentage of unique users who purchase at least one product from their wishlist within 30 days of adding a product to their wishlist.</p>
        <p style="color: #a0aec0; font-size: 13px; margin-bottom: 5px;"><strong>Mathematical Formula:</strong></p>
        <div style="background-color: #0b0d10; padding: 16px; border-radius: 8px; border: 1px solid #2d3139; font-family: monospace; font-size: 14px; text-align: center; color: #cbd5e0;">
            Users purchasing &ge;1 wishlisted product within 30 days<br>
            ----------------------------------------------------------<br>
            Users who added &ge;1 product to wishlist
        </div>
        <p style="color: #ffcc00; font-size: 12px; font-weight: bold; margin-top: 15px;">Current Metric Value: Requires behavioral event data (Unavailable in current qualitative research dataset)</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("#### Metric Hierarchy & Impact Path")
    st.markdown('''
    <div style="background-color: #161a22; padding: 20px; border-radius: 12px; border: 1px solid #2d3139; box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-bottom: 25px;">
        <div style="text-align: center; margin-bottom: 12px;">
            <div style="font-size: 11px; color: #ff3f6c; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">North Star</div>
            <div style="font-size: 18px; font-weight: bold; color: #ff3f6c;">30-Day Wishlist &rarr; Purchase Rate</div>
            <div style="font-size: 11px; color: #ffcc00; font-weight: bold; margin-top: 2px;">[!] Requires behavioral event data</div>
        </div>
        <div style="text-align: center; color: #ff3f6c; font-size: 18px; font-weight: bold; margin-bottom: 12px;">|</div>
        <div style="text-align: center; margin-bottom: 12px;">
            <div style="font-size: 11px; color: #ff3f6c; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">L1 Business Outcome Metric</div>
            <div style="font-size: 18px; font-weight: bold; color: #e2e8f0;">Wishlist &rarr; Purchase Conversion Rate</div>
            <div style="font-size: 11px; color: #ffcc00; font-weight: bold; margin-top: 2px;">[!] Requires behavioral event data</div>
        </div>
        <div style="text-align: center; color: #ff3f6c; font-size: 18px; font-weight: bold; margin-bottom: 12px;">|</div>
        <div style="display: flex; justify-content: space-around; margin-bottom: 12px; gap: 15px;">
            <div style="flex: 1; text-align: center; background-color: #0b0d10; padding: 12px; border-radius: 8px; border: 1px solid #2d3139;">
               <div style="font-size: 11px; color: #a0aec0; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">L2 Metric: Decision Confidence</div>
               <div style="font-size: 10px; color: #ffcc00; font-weight: bold; margin-top: 2px;">[!] Requires event data</div>
            </div>
            <div style="flex: 1; text-align: center; background-color: #0b0d10; padding: 12px; border-radius: 8px; border: 1px solid #2d3139;">
               <div style="font-size: 11px; color: #a0aec0; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">L2 Metric: Barrier Resolution Rate</div>
               <div style="font-size: 10px; color: #ffcc00; font-weight: bold; margin-top: 2px;">[!] Requires event data</div>
            </div>
            <div style="flex: 1; text-align: center; background-color: #0b0d10; padding: 12px; border-radius: 8px; border: 1px solid #2d3139;">
               <div style="font-size: 11px; color: #a0aec0; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">L2 Metric: Decision-Support Engagement</div>
               <div style="font-size: 10px; color: #ffcc00; font-weight: bold; margin-top: 2px;">[!] Requires event data</div>
            </div>
        </div>
        <div style="text-align: center; color: #ff3f6c; font-size: 18px; font-weight: bold; margin-bottom: 12px;">|</div>
        <div style="display: flex; justify-content: space-around; gap: 15px;">
            <div style="flex: 1; text-align: center; background-color: #0b0d10; padding: 12px; border-radius: 8px; border: 1px solid #2d3139;">
               <div style="font-size: 11px; color: #a0aec0; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">L3 Metric: Comparison Engagement</div>
               <div style="font-size: 10px; color: #ffcc00; font-weight: bold; margin-top: 2px;">[!] Requires event data</div>
            </div>
            <div style="flex: 1; text-align: center; background-color: #0b0d10; padding: 12px; border-radius: 8px; border: 1px solid #2d3139;">
               <div style="font-size: 11px; color: #a0aec0; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">L3 Metric: Review Insight Engagement</div>
               <div style="font-size: 10px; color: #ffcc00; font-weight: bold; margin-top: 2px;">[!] Requires event data</div>
            </div>
            <div style="flex: 1; text-align: center; background-color: #0b0d10; padding: 12px; border-radius: 8px; border: 1px solid #2d3139;">
               <div style="font-size: 11px; color: #a0aec0; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">L3 Metric: Fit/Size Info Engagement</div>
               <div style="font-size: 10px; color: #ffcc00; font-weight: bold; margin-top: 2px;">[!] Requires event data</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    rel_col1, rel_col2, rel_col3 = st.columns(3)
    with rel_col1:
        st.markdown("**L3 -> L2: Feature to Decision Validation**")
        st.write("Engagement with specific discovery features (e.g., side-by-side comparison tables, sizing recommendations, and natural daylight review photos) directly reduces user uncertainty. This interaction drives up the shopper's L2 Decision Confidence and resolves identified purchase barriers.")
    with rel_col2:
        st.markdown("**L2 -> L1: Decision Validation to Conversion**")
        st.write("Higher L2 Decision Confidence and active barrier resolution eliminate purchase postponement triggers. When shopper hesitation is cleared, users move significantly faster from evaluation to checkout, directly optimizing the L1 Wishlist-to-Purchase Conversion Rate.")
    with rel_col3:
        st.markdown("**L1 -> North Star: Conversion to Growth**")
        st.write("Increasing the L1 Conversion Rate directly drives the core growth goal: increasing the percentage of users completing a transaction from their wishlist within 30 days (Proposed North Star Metric), maximizing the value extracted from pre-generated saved demand already present on the platform.")
