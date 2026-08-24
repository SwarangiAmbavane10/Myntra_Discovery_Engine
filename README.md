# Myntra AI Discovery Engine (IN DEVELOPMENT)

> **Status:** ⚠️ IN DEVELOPMENT. This project is in its initiation phase. Future execution phases are planned but not yet implemented.

---

## 1. Project Purpose & Context
This project represents a growth initiative for **Myntra**, a leading fashion and lifestyle e-commerce platform. 

### The Core Challenge
Millions of users browse fashion products, save items they like, and add products to their wishlists daily. Wishlisting represents explicit user interest and purchase intent. However, only a small proportion of these wishlisted products eventually translate into purchases. 

### Business Goal & Value
* **Primary Business Goal:** Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it.
* **Business Value:** Improving this conversion rate will increase purchase frequency, improve monetization from existing users, and extract greater value from the high-intent demand already present on the platform.

### Critical Constraints & Discovery Principles
1. **No Monetary Incentives:** We cannot offer discounts, coupons, cashback, or price drops to drive conversion. Solutions must be product-led or experience-led.
2. **The Problem is UNKNOWN:** We do not assume why users postpone or fail to complete purchases (e.g., price, fit, styling, social proof, etc.). All assumptions are treated as hypotheses to be evaluated through research.

---

## 2. Discovery Objective
To discover, validate, and define the underlying user problems and purchase barriers that prevent wishlist conversion. We will achieve this through secondary research, AI-powered feedback analysis at scale, and qualitative primary research (5–6 user interviews).

---

## 3. Project Documentation Links
The project's strategy, context, and plan are detailed in the following root files:
* 📄 **[context.md](file:///c:/Users/91911/OneDrive/Desktop/Myntra_Discovery_engine/context.md):** Business context, constraints, and discovery questions.
* 📄 **[problemStatement.md](file:///c:/Users/91911/OneDrive/Desktop/Myntra_Discovery_engine/problemStatement.md):** Formal breakdown of Knowns, Unknowns, and research objectives.
* 📄 **[architecture.md](file:///c:/Users/91911/OneDrive/Desktop/Myntra_Discovery_engine/architecture.md):** System architecture, data collection pipeline, and component status matrix.
* 📄 **[implementation-plan.md](file:///c:/Users/91911/OneDrive/Desktop/Myntra_Discovery_engine/implementation-plan.md):** Phase-by-phase execution plan (Phases 0 to 13) with inputs, outputs, and completion criteria.
* 📄 **[edge-case.md](file:///c:/Users/91911/OneDrive/Desktop/Myntra_Discovery_engine/edge-case.md):** Analysis of data quality risks, sampling biases, LLM limitations, and mitigation strategies.

---

## 4. Planned Architecture
The AI Discovery Engine is structured as a multi-step data processing pipeline:
```
Public User Feedback (Play Store, App Store, Reddit, Forums)
   ├──> Data Collection (Scrapers)
   ├──> Raw Dataset Storage (data/raw/)
   ├──> Data Cleaning & Deduplication (data/cleaned/)
   ├──> Discovery-Relevant Filtering
   ├──> AI Analysis (Theme/Pain Point Tagging & Quantification)
   └──> LLM Synthesis & Evidence Retrieval (data/processed/ -> PM Insights)
```

---

## 5. Project Phases Outline
* **Phase 0:** Project setup and documentation (Current Status: **COMPLETED**)
* **Phase 1:** Data collection
* **Phase 2:** Data cleaning
* **Phase 3:** Discovery filtering
* **Phase 4:** AI analysis
* **Phase 5:** Opportunity identification and comparison
* **Phase 6:** Metric decomposition
* **Phase 7:** User research (Primary Research)
* **Phase 8:** Final problem definition
* **Phase 9:** MVP (Minimum Viable Product)
* **Phase 10:** MVP deployment
* **Phase 11:** Success metrics
* **Phase 12:** Risks and mitigation
* **Phase 13:** Final evaluation/documentation

---

## 6. How to Set Up & Run
Install python dependencies:
```bash
pip install -r requirements.txt
```
Configure your Gemini API key in a local `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
Run the complete data pipeline (ingestion, cleaning, relevance filtering, AI analysis, clustering, opportunity scoring):
```bash
python -m engine.pipeline
```
To run the Streamlit dashboard:
```bash
streamlit run app.py
```

---

## 7. Manual CSV/Excel Import Pipeline
For platforms without direct automated scrapers (YouTube, Myntra reviews, Fashion Communities, Social Media), you can manually place CSV/Excel (`.csv` or `.xlsx`) or JSON (`.json`) exports in their corresponding subdirectories:
* `data/raw/youtube/`
* `data/raw/myntra/`
* `data/raw/fashion_communities/`
* `data/raw/social_media/`

### CSV/Excel Formatting Templates
To ensure records map successfully, include the following columns in your CSV or Excel files:
* **YouTube**: `id`, `text`, `date`, `author`, `video_title` (or `title`), `likes` (or `engagement`), `url`
* **Myntra**: `id`, `text`, `date`, `author`, `title` (or `review_title`), `rating` (or `score`), `product`, `product_id`, `category`, `brand`, `helpful` (or `engagement`)
* **Fashion Communities**: `id`, `text`, `date`, `author`, `title`, `category` (or `community`), `engagement` (or `likes`)
* **Social Media**: `id`, `text`, `date`, `author`, `url`, `engagement` (or `likes`)

If any field is missing, the ingestion pipeline leaves it NULL. Do NOT invent data.
