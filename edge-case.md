# Edge Case Management & Analytical Risks

This document outlines potential edge cases, data quality issues, and technical/analytical risks that the Myntra AI Discovery Engine must handle, along with proposed mitigation strategies.

---

## 1. Data Cleaning & Quality Issues

### Duplicate Feedback
* **Problem:** Users may post the exact same review multiple times due to app submission retries or network errors.
* **Mitigation:** Run an exact-string deduplication check on raw review text before saving to `data/cleaned/`.

### Cross-Source Duplicates
* **Problem:** Users may copy and paste their reviews across multiple platforms (e.g., App Store, Play Store, and Twitter).
* **Mitigation:** Calculate semantic similarity or run fuzzy hashing (like MinHash) on reviews across sources to flag and remove cross-platform duplicates.

### Spam & Bot Content
* **Problem:** Promotional spam, affiliate codes, or automated bot feedback can skew keyword frequency.
* **Mitigation:** Implement heuristic filtering to flag repetitive text, links, promotional keywords, and accounts posting high-frequency reviews.

### Short / Low-Information Feedback
* **Problem:** One-word or low-value comments like "Nice", "Worst app", "Fashion", or "Okay".
* **Mitigation:** Apply a character-length and word-count threshold (e.g., discard feedback under 3 words or 15 characters unless it contains specific key phrases).

### Irrelevant Feedback
* **Problem:** Reviews focusing on app issues unrelated to shopping behaviors (e.g., payment failures, delivery delays, app crashes, or customer service issues).
* **Mitigation:** Use a classifier or rule-based filter to flag and separate operational complaints from discovery-relevant product, fit, price, or choice conversations.

---

## 2. Linguistic & Textual Challenges

### Multilingual Content (Hinglish/Code-Mixing)
* **Problem:** Indian e-commerce users frequently write in "Hinglish" (Hindi written in the Latin alphabet) or mix local languages with English (e.g., "Size badli kaise kare?", "Quality acha nahi hai").
* **Mitigation:** Select an LLM (such as Gemini) that has strong multilingual and code-mixed comprehension, or pre-translate Hinglish texts using light heuristic mappings where necessary.

### Sarcasm & Irony
* **Problem:** Users posting sarcastic comments (e.g., "Amazing fit, it could fit a giant") might be misclassified as positive by simple sentiment analyzers.
* **Mitigation:** Rely on LLM-based semantic analysis rather than basic keyword-based sentiment tools, as LLMs excel at detecting context and sarcasm.

### Contradictory Feedback
* **Problem:** One user states "The size runs too small", while another states "The size runs too large" for the same or similar items.
* **Mitigation:** Do not aggregate contradictory statements into a single truth; represent them as user-segment variances or product-specific variation points.

---

## 3. Sampling & Source Biases

### Biased Samples
* **Problem:** Users who write public reviews are usually those with extreme opinions (highly satisfied or highly dissatisfied).
* **Mitigation:** Balance App/Play Store data (highly skewed towards crashes and basic feedback) with Reddit/community discussions (rich, descriptive shopping journeys).

### Source-Specific Bias
* **Problem:** App Store reviewers may represent a higher-income demographic, whereas Play Store reviews cover a broader user base. Reddit discussions tend to be more tech-savvy and community-driven.
* **Mitigation:** Track and display the source distribution of every identified theme to ensure decision-makers understand the segment bias behind the data.

---

## 4. AI & Analytical Risks

### Insufficient Evidence
* **Problem:** A theme or pain point is highlighted but is backed by only one or two user comments.
* **Mitigation:** Set minimum threshold counters (e.g., a theme must appear in at least 5 independent feedback records to be surfaced as a potential opportunity area).

### False Patterns (Apophenia)
* **Problem:** The AI groups unrelated user comments into a single "theme" that does not exist in reality.
* **Mitigation:** Require the LLM to output a "confidence score" and point directly to the raw, anonymized user quotes that support the theme.

### LLM Hallucinations
* **Problem:** The LLM generates summary insights or quotes that were never actually present in the dataset.
* **Mitigation:** Use strict temperature settings (T=0) for LLM prompts, enforce output formatting (JSON schemas), and programmatically validate that synthesized quotes exist in the cleaned raw dataset.

---

## 5. Technical & Operational Issues

### API Failures & Rate Limits
* **Problem:** Reaching API limits for scraping (e.g., Reddit API limits) or LLM analysis (Gemini API token limits).
* **Mitigation:** Implement exponential backoff, retry mechanisms, and batch processing delays inside our pipeline code.

### Scraping Failures (HTML/DOM Changes)
* **Problem:** Web structures of forums and communities change, breaking scraper scripts.
* **Mitigation:** Rely on stable APIs (PRAW, App Store Scrapers) rather than fragile DOM scraping where possible. Include error alerts for scraper scripts.

---

## 6. Privacy & Causality Constraints

### Privacy Concerns
* **Problem:** Inadvertently scraping and exposing personally identifiable information (PII) of users (names, profile links, locations).
* **Mitigation:** Anonymize all raw data during the cleaning phase. Strip user handles, real names, and profile URLs before passing text to the AI engine or storing in processed databases.

### Inability to Establish Causality
* **Problem:** Public conversations show correlation (e.g., users talk about fit issues and wishlists in the same thread), but this does not prove fit issues *cause* the wishlist-to-purchase drop.
* **Mitigation:** Treat all findings from the Discovery Engine as **hypotheses**. Use primary user interviews (Phase 7) and MVP experiments (Phase 9) to establish causality.
