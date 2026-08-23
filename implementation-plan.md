# Implementation Plan: Myntra AI Discovery Engine

This document outlines the detailed roadmap for the Myntra AI Discovery Engine project from initiation to final evaluation.

---

## Phase 0: Project Setup and Documentation
* **Objective:** Establish the foundation of the project by setting up the directory structure, initial project documents, environment configurations, and dependency definitions.
* **Inputs:** Product requirements, business context, architectural guidelines.
* **Outputs:** Initial project structure, configuration files, and core markdown documents defining goals, problem statements, architectures, and edge cases.
* **Files Expected:** 
  * `context.md`
  * `problemStatement.md`
  * `architecture.md`
  * `implementation-plan.md` (this file)
  * `edge-case.md`
  * `README.md`
  * `.gitignore`, `.env.example`, `requirements.txt`, `app.py`
  * Empty data directories (`data/raw/`, `data/cleaned/`, `data/processed/`) and module folders (`scraper/`, `analysis/`, `engine/`, `research/`, `mvp/`)
* **Completion Criteria:** All core setup files and directories are created, documentation contains zero assumed root causes or invented user feedback, and the repo status is marked "In Development" with all components designated "Planned".

---

## Phase 1: Data Collection
* **Objective:** Develop and run scraper tools to pull user reviews and conversations from public websites, forums, and app stores.
* **Inputs:** List of target sources (App Store, Play Store, Reddit subreddits, YouTube comments, shopping communities), API keys (Reddit client ID/secret, Google API keys if needed).
* **Outputs:** Raw dataset containing raw user text, source identifiers, dates, and ratings.
* **Files Expected:** 
  * `scraper/play_store.py`
  * `scraper/app_store.py`
  * `scraper/reddit.py`
  * `scraper/youtube.py` (optional/future)
  * `data/raw/play_store_raw.jsonl`
  * `data/raw/app_store_raw.jsonl`
  * `data/raw/reddit_raw.jsonl`
* **Completion Criteria:** Successful execution of scraping scripts yielding at least 1,000 combined raw user feedback entries saved locally in JSONL format, containing text content and source metadata, without API blocks or rate limit crashes.

---

## Phase 2: Data Cleaning
* **Objective:** Clean the collected text feedback by removing noise, duplicates, and irrelevant content to improve AI analysis quality.
* **Inputs:** Raw data files in `data/raw/`.
* **Outputs:** Cleaned text dataset containing unique, filtered, and properly formatted feedback records.
* **Files Expected:** 
  * `analysis/clean_data.py`
  * `data/cleaned/play_store_cleaned.jsonl`
  * `data/cleaned/app_store_cleaned.jsonl`
  * `data/cleaned/reddit_cleaned.jsonl`
* **Completion Criteria:** Script successfully deduplicates text within and across sources, removes reviews under 3 words or containing only gibberish, standardizes character encodings, and exports clean data files to `data/cleaned/`.

---

## Phase 3: Discovery Filtering
* **Objective:** Filter the cleaned dataset to isolate feedback relevant to shortlisting, wishlist behaviors, decision friction, purchase postponement, and general e-commerce conversion issues.
* **Inputs:** Cleaned datasets in `data/cleaned/`.
* **Outputs:** Datasets filtered for discovery-relevant conversations and reviews.
* **Files Expected:** 
  * `analysis/filter_relevant.py`
  * `data/cleaned/discovery_relevant_feedback.jsonl`
* **Completion Criteria:** A rule-based or embeddings-based filter is implemented that successfully identifies and separates wishlist/decision-relevant feedback from pure technical app complaints (e.g., payment failures, app crashes, refund delays).

---

## Phase 4: AI Analysis
* **Objective:** Run LLM classification and semantic processing on the discovery dataset to identify underlying user themes and friction points.
* **Inputs:** `data/cleaned/discovery_relevant_feedback.jsonl`, Gemini API access key.
* **Outputs:** Categorized feedback records containing identified themes, sentiment scores, and confidence scores.
* **Files Expected:** 
  * `engine/classifier.py`
  * `engine/prompts.py`
  * `data/processed/analyzed_feedback.jsonl`
* **Completion Criteria:** Every record in the discovery-relevant dataset is tagged with one or more friction categories (e.g., fit/size uncertainty, occasion suitability, style advice needed, review distrust, purchase delay reasons) with LLM validation checks.

---

## Phase 5: Opportunity Identification and Comparison
* **Objective:** Aggregate and analyze the processed tags to quantify the frequency of various friction points, identifying and comparing potential opportunity areas.
* **Inputs:** `data/processed/analyzed_feedback.jsonl`.
* **Outputs:** Structured reports containing volume charts, theme prioritization matrices, and representative user quotes for each identified opportunity area.
* **Files Expected:** 
  * `engine/summarizer.py`
  * `data/processed/opportunity_matrix.json`
  * `research/secondary_findings.md`
* **Completion Criteria:** Themes are quantified and sorted by frequency and sentiment intensity. The `secondary_findings.md` file is compiled to showcase top opportunity areas supported by statistical frequency in the dataset and direct user quotes.

---

## Phase 6: Metric Decomposition
* **Objective:** Connect the identified opportunity areas to our primary business metric (30-day wishlist-to-purchase conversion rate) to understand how user behavior translates into conversion.
* **Inputs:** `research/secondary_findings.md`, Myntra wishlist metrics (simulated/modeled logic).
* **Outputs:** Mathematical or logical decomposition of the business metric into behavioral sub-metrics.
* **Files Expected:** 
  * `research/metric_decomposition.md`
* **Completion Criteria:** Creation of a metric map outlining how different behavioral changes (e.g., reducing time-to-first-purchase, increasing shortlist checkout rates) influence the core 30-day conversion rate.

---

## Phase 7: User Research (Primary Research)
* **Objective:** Conduct 5–6 qualitative user interviews with real consumers to validate or invalidate the opportunity areas and pain points surfaced by the AI Discovery Engine.
* **Inputs:** Interview script, target user cohort definition.
* **Outputs:** Anonymized transcript summaries, user journey maps, and empathy maps.
* **Files Expected:** 
  * `research/interview_guide.md`
  * `research/interview_notes_1_to_6.md`
* **Completion Criteria:** Execution of 5-6 structured user interviews, documenting qualitative insights, friction points, wishlist habits, and decision processes without introducing interviewer bias or pre-fabricating answers.

---

## Phase 8: Final Problem Definition
* **Objective:** Synthesize findings from both primary research (interviews) and secondary research (AI analysis) to form a single, validated definition of the user problem.
* **Inputs:** `research/secondary_findings.md`, `research/interview_notes_1_to_6.md`.
* **Outputs:** A validated problem statement artifact detailing the core user friction, target segment, and justification.
* **Files Expected:** 
  * `research/final_problem_definition.md`
* **Completion Criteria:** A clear, evidence-backed problem statement that defines the primary reason why users wishlist items but do not purchase them, linking back to research data, without proposing a solution yet.

---

## Phase 9: MVP (Minimum Viable Product)
* **Objective:** Design and build a non-monetary MVP that directly addresses the validated user problem to improve wishlist conversion.
* **Inputs:** `research/final_problem_definition.md`, UX/UI sketches, Streamlit/Flask app template.
* **Outputs:** A functional local prototype of the feature (e.g., a "fit confidence checker", "occasion builder", or "styling companion") integrated into the local discovery interface.
* **Files Expected:** 
  * `mvp/app.py`
  * `mvp/templates/`
  * `mvp/components/`
* **Completion Criteria:** The MVP is fully functional, runs locally, addresses the validated problem statement, utilizes simulated Myntra product datasets, and operates strictly under the non-monetary constraint.

---

## Phase 10: MVP Deployment
* **Objective:** Deploy the MVP locally or to a cloud hosting platform (e.g., Hugging Face Spaces, Render, or a local server) so that it can be reviewed and tested by the team or test users.
* **Inputs:** Local codebase in `mvp/`.
* **Outputs:** Active deployment URL or reproducible local environment setup instructions.
* **Files Expected:** 
  * `mvp/Dockerfile`
  * `mvp/README.md` (MVP-specific instructions)
* **Completion Criteria:** The application is accessible online or locally via a single command, loads and functions correctly, and is ready for user walkthroughs.

---

## Phase 11: Success Metrics
* **Objective:** Define how we will measure the success of the MVP when deployed at scale, establishing tracking systems.
* **Inputs:** `research/final_problem_definition.md`, product parameters.
* **Outputs:** A framework defining the primary business metric, secondary guardrail metrics, and instrumentation requirements.
* **Files Expected:** 
  * `research/success_metrics.md`
* **Completion Criteria:** A finalized success metric document defining pre-MVP and post-MVP baseline calculations, statistical significance thresholds, and guardrails (e.g., making sure return rates don't increase).

---

## Phase 12: Risks and Mitigation
* **Objective:** Identify potential operational, technical, user-experience, and financial risks associated with the MVP and detail proactive mitigation strategies.
* **Inputs:** MVP design, research notes, technical architecture.
* **Outputs:** Risk log and mitigation strategies.
* **Files Expected:** 
  * `research/risks_and_mitigation.md`
* **Completion Criteria:** Documented risk assessment covering user privacy, technical scalability, negative behavioral impacts, catalog representation, and LLM output reliability.

---

## Phase 13: Final Evaluation / Documentation
* **Objective:** Document the results of the discovery phase, MVP performance indicators, key learnings, and recommendations for scaling or pivoting.
* **Inputs:** All previous documentation, MVP testing feedback, user reaction summaries.
* **Outputs:** Final case study, summary presentation deck (markdown), and clean, production-ready codebase documentation.
* **Files Expected:** 
  * `research/final_case_study.md`
  * `walkthrough.md`
* **Completion Criteria:** Full project documentation is updated, code repos are cleaned, and a comprehensive summary of the discovery and validation process is completed.
