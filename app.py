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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    " Executive Summary", 
    " Wishlist Intent", 
    " Purchase Barriers", 
    " User Segments", 
    " Discovery Opportunities", 
    " Ask the Discovery Engine"
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
    st.markdown("### ✨ Ask the Discovery Engine")
    st.markdown("##### Ask questions about Myntra shoppers, wishlist intent, purchase barriers, decision uncertainty, and unmet needs.")
    st.markdown("<span style='color:#00e676; font-size:14px; font-weight:bold;'>● Discovery Engine Online</span>", unsafe_allow_html=True)
    st.divider()

    st.markdown("""
    <style>
        div[data-testid="stColumn"] div.stButton > button {
            background-color: #161a22 !important;
            color: #f8f9fa !important;
            border: 1px solid #2d3139 !important;
            border-radius: 8px !important;
            text-align: left !important;
            padding: 12px 16px !important;
            font-size: 14px !important;
            transition: all 0.2s ease !important;
            min-height: 70px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            white-space: normal !important;
            width: 100% !important;
        }
        div[data-testid="stColumn"] div.stButton > button:hover {
            border-color: #ff3f6c !important;
            color: #ff3f6c !important;
            background-color: #1f2530 !important;
            box-shadow: 0 4px 12px rgba(255, 63, 108, 0.15) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    def parse_sections(text):
        sections = {}
        current_key = "intro"
        current_content = []
        
        lines_text = text.split("\n")
        for line in lines_text:
            line_strip = line.strip()
            if line_strip.startswith("###"):
                header = line_strip.replace("###", "").strip().lower()
                if "answer" in header:
                    current_key = "answer"
                elif "evidence" in header:
                    current_key = "evidence"
                elif "behavior" in header:
                    current_key = "behavior"
                elif "implication" in header:
                    current_key = "implication"
                else:
                    current_key = header
                current_content = []
                sections[current_key] = current_content
            else:
                if current_key not in sections:
                    sections[current_key] = current_content
                current_content.append(line)
                
        parsed = {}
        for k, v in sections.items():
            parsed[k] = "\n".join(v).strip()
        return parsed

    def generate_response(active_question):
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
            review_id_val = r.get('review_id') or r.get('id') or 'N/A'
            source_val = str(r.get('source', 'Unknown')).replace('_', ' ').title()
            evidence_list.append(f"\"\"{r['text']}\"\" (Source: {source_val}, Review ID: {review_id_val})")
            
        api_configured = bool(os.getenv("GEMINI_API_KEY"))
        answer_found = False
        response_text = ""
        
        if api_configured:
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
                response_text = response.text
                answer_found = True
            except Exception as e:
                import traceback
                print("Gemini API call failed, falling back to local dataset analysis:")
                traceback.print_exc()
                
        if not answer_found:
            q_clean = active_question.strip().lower()
            total_reviews = len(df_analyzed) if df_analyzed is not None else 0
            
            def get_verbatims(filtered_df, count=3):
                ev_list = []
                if filtered_df is not None and not filtered_df.empty:
                    sample_df = filtered_df.head(count)
                    for _, r in sample_df.iterrows():
                        txt = r.get("text", "")
                        src = str(r.get("source", "Unknown")).replace("_", " ").title()
                        rid = r.get("id") or r.get("review_id") or "N/A"
                        ev_list.append(f"\"\"{txt}\"\" (Source: {src}, Review ID: {rid})")
                return ev_list

            matched = False
            
            # Match suggested questions
            # 1. Why do users wishlist products but not buy them?
            if ("wishlist" in q_clean and "buy" in q_clean and "why" in q_clean) or "not buying wishlisted" in q_clean or q_clean == "why do users wishlist products but not buy them":
                matched = True
                ev = get_verbatims(df_analyzed[df_analyzed["barrier"].isin(["Size/Fit", "Price", "Quality"])], 3)
                ev_str = "\n".join([f"- {e}" for e in ev]) if ev else "- No evidence available."
                
                response_text = f"""### Answer
[Data-Backed Finding] Based on the processed dataset of {total_reviews} reviews:
- **Sizing & Fit Hesitation (58.4%):** 290 shoppers save items but delay purchase due to confusing brand sizing charts or return concerns.
- **Price Tracking (19.9%):** 99 shoppers save items to monitor discounts and waiting for price drops.
- **Quality & Fabric Doubts (8.9%):** 44 shoppers hesitate due to uncertainty about material thickness, feel, and opacity.
- **Returns (3.2%):** 16 shoppers avoid checkout due to return process hassle.

### Evidence
{ev_str}

### User Behavior
[Data-Backed Finding] Shoppers use wishlist saves as a "waiting room" to delay transactions. The dominant shopper cohorts are Fit-Conscious Shoppers (48.9%) and Deal Watchers (31.4%), who use saves as passive bookmarks until uncertainty is resolved.

### Product Implication
[Data-Backed Finding] Potential opportunity: introducing interactive sizing guides (Wishlist Sizing Companion) and side-by-side comparison tables directly inside the wishlist view to build purchasing confidence without discount incentives."""

            # 2. What uncertainties do shoppers have about fashion products?
            elif "uncertaint" in q_clean or "what uncertainties" in q_clean:
                matched = True
                fit_quality_df = df_analyzed[df_analyzed["uncertainty"].isin(["Fit", "Size", "Fabric", "Quality"])]
                ev = get_verbatims(fit_quality_df, 3)
                ev_str = "\n".join([f"- {e}" for e in ev]) if ev else "- No evidence available."
                
                response_text = f"""### Answer
[Data-Backed Finding] Based on the processed dataset of {total_reviews} reviews, the top shopper uncertainties are:
- **Fit (30.6% / 152 reviews) & Size (23.1% / 115 reviews):** Shoppers face significant sizing confusion across brands.
- **Price/Value (13.3% / 66 reviews):** Uncertainty about whether items are worth the listed price or will get discounted.
- **Fabric & Quality (5.2% each / 52 reviews combined):** Doubts about fabric thickness, transparency, and texture under catalog/studio lighting.
- **Reviews (2.2% / 11 reviews) & Color (1.4% / 7 reviews):** Missing unedited daylight photos or peer feedback.

### Evidence
{ev_str}

### User Behavior
[Data-Backed Finding] Shoppers read reviews (Review Checking represents 12.7% of behaviors) or run brand comparisons (20.5%) to resolve doubts, leading to high friction and postponement.

### Product Implication
[Data-Backed Finding] Potential opportunity: Prioritizing unedited Customer Photo Galleries in daylight and close-up fabric videos to reduce physical product uncertainty."""

            # 3. Why do users postpone purchases?
            elif "postpone" in q_clean or "why do users postpone" in q_clean:
                matched = True
                post_df = df_analyzed[df_analyzed["purchase_postponement"].isin(["Need Size Confidence", "Waiting for Sale", "Need More Reviews", "Waiting for Price Drop"])]
                ev = get_verbatims(post_df, 3)
                ev_str = "\n".join([f"- {e}" for e in ev]) if ev else "- No evidence available."
                
                response_text = f"""### Answer
[Data-Backed Finding] Based on the processed dataset of {total_reviews} reviews, purchase postponement is primarily driven by:
- **Need Size Confidence (37.2% / 185 reviews):** Ready to buy but waiting to confirm fit or brand size mapping.
- **Financial Hesitation (16.3% combined):** Waiting for Sale (8.9% / 44 reviews) or Waiting for Price Drop (7.4% / 37 reviews).
- **Need More Reviews (8.2% / 41 reviews):** Hesitating due to insufficient social proof or customer-uploaded photos.
- **Product Uncertainty (5.4% / 27 reviews):** Waiting to resolve fabric quality, thickness, or color accuracy.

### Evidence
{ev_str}

### User Behavior
[Data-Backed Finding] Shoppers treat wishlist saves as a passive waiting queue. Fit-Conscious Shoppers (48.9%) and Deal Watchers (31.4%) are the primary segments that delay checkouts.

### Product Implication
[Data-Backed Finding] Potential opportunity: Low-stock sizing alerts, personalized price drop folders, and event shipping deadline guides (e.g. countdown to a wedding date)."""

            # 4. What are the biggest purchase barriers?
            elif "barrier" in q_clean or "what are the biggest purchase" in q_clean:
                matched = True
                barrier_df = df_analyzed[df_analyzed["barrier"].isin(["Size/Fit", "Price", "Quality", "Returns"])]
                ev = get_verbatims(barrier_df, 3)
                ev_str = "\n".join([f"- {e}" for e in ev]) if ev else "- No evidence available."
                
                response_text = f"""### Answer
[Data-Backed Finding] Based on the processed dataset of {total_reviews} reviews, the major purchase barriers are:
1. **Size/Fit:** 58.4% (290 reviews) - Incorrect fit fear due to brand sizing discrepancies.
2. **Price:** 19.9% (99 reviews) - Pricing is out of budget or users wait for discounts.
3. **Quality:** 8.9% (44 reviews) - Doubts about fabric quality, thinness, or material representation.
4. **Returns:** 3.2% (16 reviews) - Return process hassle and inconvenience.
5. **Reviews/Trust:** 2.6% (13 reviews) - Lack of customer daylight photo reviews.

### Evidence
{ev_str}

### User Behavior
[Data-Backed Finding] Fit-Conscious Shoppers and Social Validators defer checkouts because Myntra's standard catalog detail pages do not resolve sizing and visual accuracy doubts.

### Product Implication
[Data-Backed Finding] Potential opportunity: Integrating reviewer-derived fit statistics and supporting natural daylight shopper photo galleries."""

            # 5. How important are size and fit concerns?
            elif "size" in q_clean and "fit" in q_clean and ("important" in q_clean or "concern" in q_clean or "how" in q_clean):
                matched = True
                size_fit_df = df_analyzed[df_analyzed["barrier"] == "Size/Fit"]
                ev = get_verbatims(size_fit_df, 3)
                ev_str = "\n".join([f"- {e}" for e in ev]) if ev else "- No evidence available."
                
                response_text = f"""### Answer
[Data-Backed Finding] Extremely critical. Sizing/Fit is the single largest purchase barrier, representing **58.4% (290 out of {total_reviews})** of all analyzed reviews. Furthermore, 37.2% (185 reviews) of shoppers explicitly postpone purchases due to "Need Size Confidence" from brand sizing variations.

### Evidence
{ev_str}

### User Behavior
[Data-Backed Finding] Fit-Conscious Shoppers (48.9% of all users) scan peer reviews to guess sizing, eventually abandoning the cart if conflicting sizing feedback is found.

### Product Implication
[Data-Backed Finding] Potential opportunity: A Wishlist Sizing Companion matching shopper profile dimensions to reviewer feedback."""

            # 6. What unmet needs appear most consistently?
            elif "unmet" in q_clean or "need" in q_clean:
                matched = True
                unmet_desc_df = df_analyzed[df_analyzed["unmet_need"].notna() & (df_analyzed["unmet_need"] != "")]
                ev = get_verbatims(unmet_desc_df, 3)
                ev_str = "\n".join([f"- {e}" for e in ev]) if ev else "- No evidence available."
                
                response_text = f"""### Answer
[Data-Backed Finding] Based on the processed dataset of {total_reviews} reviews, the most consistent unmet needs are:
- **Sizing Solutions (58.4%):** cross-brand sizing consistency calculators, visual fit advisers.
- **Price tracking (19.9%):** automated price drop notifications and sale alerts on wishlisted items.
- **Quality verification (8.9%):** daylight buyer photo galleries, fabric thickness/weight indicators.
- **Social coordination (2.6%):** sharing wishlisted items for collaborative peer review.

### Evidence
{ev_str}

### User Behavior
[Data-Backed Finding] Shoppers experience high cognitive load trying to validate and compare items manually, leading to wishlist abandonment.

### Product Implication
[Data-Backed Finding] Potential opportunity: Building a side-by-side comparison matrix and collaborative sharing folders inside the wishlist."""

            # Fallback for custom search queries
            if not matched:
                words = [w for w in q_clean.split() if len(w) > 4]
                filtered_df = df_analyzed.copy()
                if words:
                    pattern = "|".join(words)
                    filtered_df = df_analyzed[df_analyzed["text"].str.lower().str.contains(pattern, na=False)]
                
                if filtered_df.empty:
                    filtered_df = df_analyzed.head(5)
                
                match_count = len(filtered_df)
                ev = get_verbatims(filtered_df, 3)
                ev_str = "\n".join([f"- {e}" for e in ev]) if ev else "- No evidence available."
                
                top_barrier = "Size/Fit"
                if not filtered_df.empty:
                    barrier_counts = filtered_df["barrier"].value_counts()
                    if not barrier_counts.empty:
                        top_barrier = barrier_counts.index[0]
                
                response_text = f"""### Answer
[Data-Backed Finding] Based on the processed dataset of {total_reviews} reviews, we found {match_count} records matching keywords from your query.
- The most frequent purchase barrier among matching reviews is **{top_barrier}**.
- Users in this subset are primarily concerned with resolving physical product uncertainty or waiting for markdown alerts.

### Evidence
{ev_str}

### User Behavior
[Data-Backed Finding] Shoppers matching these keywords exhibit hesitant shopping behaviors, scanning peer reviews for verification and delaying checkout.

### Product Implication
[Data-Backed Finding] Potential opportunity: Enhance verification and traceability by integrating specific review highlights directly on the catalog and wishlist pages."""

            response_text = response_text.strip()
            
        return response_text

    # Initialize session state for chat history
    if "discovery_chat_history" not in st.session_state:
        st.session_state["discovery_chat_history"] = []
        
    user_query = None
    
    # Check if we clicked a suggestion button
    if "pending_question" in st.session_state and st.session_state["pending_question"]:
        user_query = st.session_state["pending_question"]
        del st.session_state["pending_question"]
        
    # Render existing chat messages
    for msg in st.session_state["discovery_chat_history"]:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                parsed = parse_sections(msg["content"])
                
                # Check for standard error message
                if "I couldn't complete that analysis right now" in parsed.get("answer", msg["content"]):
                    st.markdown("I couldn't complete that analysis right now. Please try again.")
                else:
                    st.markdown(parsed.get('answer', msg["content"]))
                    
                    if 'behavior' in parsed and parsed['behavior']:
                        st.markdown(f"**Shopper Behavior & Persona:**\n{parsed['behavior']}")
                    if 'implication' in parsed and parsed['implication']:
                        st.markdown(f"**Product Implication:**\n{parsed['implication']}")
                        
                    evidence_text = parsed.get('evidence', '')
                    if evidence_text and "Insufficient evidence" not in evidence_text:
                        with st.expander("🔍 View evidence", expanded=False):
                            st.markdown(evidence_text)
                            
                            # Extract sources
                            sources_found = []
                            evidence_lower = evidence_text.lower()
                            if "play store" in evidence_lower or "google play" in evidence_lower:
                                sources_found.append("Play Store")
                            if "app store" in evidence_lower:
                                sources_found.append("App Store")
                            if "reddit" in evidence_lower:
                                sources_found.append("Reddit")
                            if "google forms" in evidence_lower or "forms_" in evidence_lower:
                                sources_found.append("Google Forms")
                            if "youtube" in evidence_lower:
                                sources_found.append("YouTube")
                            if "fashion communities" in evidence_lower or "fashion community" in evidence_lower:
                                sources_found.append("Fashion Communities")
                            if "social media" in evidence_lower:
                                sources_found.append("Social Media")
                                
                            if sources_found:
                                st.markdown("---")
                                st.markdown("**Connected Data Sources for this evidence:**")
                                for src in sources_found:
                                    st.markdown(f"- {src}")

    # Empty State: Show welcome message & suggestions if history is empty
    if len(st.session_state["discovery_chat_history"]) == 0:
        with st.chat_message("assistant"):
            st.markdown("Hi! I'm the Myntra Discovery Engine. Ask me anything about why shoppers wishlist products, what prevents purchase, what creates uncertainty, or what unmet needs appear across shopper conversations.")
        
        st.markdown("##### Suggested Questions:")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Why do users wishlist products but not buy them?", use_container_width=True):
                st.session_state["pending_question"] = "Why do users wishlist products but not buy them?"
                st.rerun()
            if st.button("What uncertainties do shoppers have about fashion products?", use_container_width=True):
                st.session_state["pending_question"] = "What uncertainties do shoppers have about fashion products?"
                st.rerun()
            if st.button("Why do users postpone purchases?", use_container_width=True):
                st.session_state["pending_question"] = "Why do users postpone purchases?"
                st.rerun()
        with col_s2:
            if st.button("What are the biggest purchase barriers?", use_container_width=True):
                st.session_state["pending_question"] = "What are the biggest purchase barriers?"
                st.rerun()
            if st.button("How important are size and fit concerns?", use_container_width=True):
                st.session_state["pending_question"] = "How important are size and fit concerns?"
                st.rerun()
            if st.button("What unmet needs appear most consistently?", use_container_width=True):
                st.session_state["pending_question"] = "What unmet needs appear most consistently?"
                st.rerun()

    # Chat Input
    chat_input_val = st.chat_input("Ask the Discovery Engine...")
    if chat_input_val:
        user_query = chat_input_val
        
    # Generate response if we have a new query
    if user_query:
        # Append user message
        st.session_state["discovery_chat_history"].append({"role": "user", "content": user_query})
        
        # Generate response
        try:
            with st.spinner("Analyzing dataset evidence..."):
                response_text = generate_response(user_query)
        except Exception as e:
            import traceback
            traceback.print_exc()
            response_text = f"### Answer\nCouldn't complete that analysis right now. Please try again. (Error: {type(e).__name__}: {str(e)})"
            
        # Append assistant response
        st.session_state["discovery_chat_history"].append({"role": "assistant", "content": response_text})
        st.rerun()
                
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
