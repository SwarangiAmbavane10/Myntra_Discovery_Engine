# Context: Myntra AI Discovery Engine

## 1. Business Context
Myntra is one of India's leading fashion, lifestyle, and e-commerce platforms. Millions of users browse fashion products, save items they like, and add products to their wishlists daily. Wishlisting represents a high-intent, explicit interest in a product. However, only a small proportion of these wishlisted products eventually translate into actual purchases.

## 2. Growth Team Context & Role
As the Growth Team, our focus is on optimizing user activation, retention, and monetization. Within this context, the wishlist is a critical touchpoint. It captures high-intent demand that has already been generated but is not yet fully realized. 

## 3. Business Goal
Our primary objective is to:
**Increase the percentage of users who purchase at least one item from their wishlist within 30 days of adding it.**

## 4. Business Value
Optimizing wishlist-to-purchase conversion is highly valuable because it:
* **Increases Purchase Frequency:** Encourages users to complete transactions they have already expressed interest in.
* **Improves Monetization from Existing Users:** Drives incremental revenue from active users without requiring additional customer acquisition costs (CAC).
* **Extracts Greater Value from High-Intent Demand:** Capitalizes on existing traffic and catalog engagement rather than relying solely on top-of-funnel growth.

## 5. Critical Constraints
* **No Monetary Incentives:** We cannot offer discounts, coupons, cashback, or other direct monetary incentives to users to drive wishlist conversion. We must find other product-led or experience-led solutions.

## 6. What is Known vs. What is Unknown

### What is Known
* Users actively use the wishlist feature to save items they like.
* Wishlisting indicates explicit interest in a fashion product.
* Only a small percentage of wishlisted items are purchased.
* Direct monetary incentives (discounts/coupons) are off-limits for this initiative.

### What is Unknown (Critical Discovery Principle)
The underlying user problem that prevents wishlisted items from converting is **completely unknown**. We must not assume or predetermine any root cause. Potential factors are strictly hypotheses that require empirical investigation. These include, but are not limited to:
* Price sensitivity (independent of discount incentives)
* Fit and size uncertainty
* Product quality, reviews, or lack of social proof
* Styling and coordination questions
* Lack of urgency or purchase postponement reasons
* Comparison friction between multiple wishlisted items
* Occasion-based buying behavior vs. aspirational bookmarking

## 7. Discovery Questions
To guide our research, we will investigate the following questions:
* Why do users add fashion products to their wishlist?
* What prevents wishlisted products from being purchased?
* What uncertainty remains after users identify a product they like?
* What causes purchase postponement?
* How do users compare shortlisted products?
* What information do users seek outside Myntra before purchasing?
* What role do fit, size, styling, price, reviews, occasion, and social validation play?
* When is wishlist behavior genuine purchase intent versus casual bookmarking?
* How do behaviors differ across user segments?
* What unmet needs emerge consistently?

## 8. Expected Role of the AI Discovery Engine
The AI Discovery Engine will serve as our primary tool for parsing, analyzing, and synthesizing public user feedback at scale. Rather than relying solely on manual research, this engine will process text data from diverse public channels (App Store/Play Store reviews, Reddit, fashion forums, social media, YouTube, and product Q&As). 

It will go beyond simple sentiment analysis or basic summarization. The engine will:
1. Detect patterns, pain points, and themes in public fashion shopping discussions.
2. Filter for conversations relevant to shortlisting, wishlisting, decision-making, and purchase hesitation.
3. Help quantify, compare, and prioritize potential opportunity areas based on real user feedback.
4. Provide structured, evidence-backed insights to inform our primary research and MVP direction.
