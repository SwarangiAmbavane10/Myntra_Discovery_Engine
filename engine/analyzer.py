import os
import json
import re
import pandas as pd
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Upgraded built-in cache for demo reviews mapping to the new schema
DEMO_AI_CACHE = {
    "gp_01": {
        "intent": "Product Comparison",
        "barrier": "Other",
        "purchase_stage": "consideration",
        "uncertainty": "Fabric",
        "purchase_postponement": "Comparing products",
        "decision_behavior": "Product comparison",
        "user_segment": "Comparison Shoppers",
        "unmet_need": "Side-by-side product fabric and fit comparison tool.",
        "emotion": "frustrated",
        "product_category": "unknown",
        "evidence": "cannot decide which one to buy. I wish there was a tool to compare the fabrics and fit side by side",
        "confidence": 0.9
    },
    "gp_02": {
        "intent": "Genuine Purchase Intent",
        "barrier": "Size/Fit",
        "purchase_stage": "wishlisted",
        "uncertainty": "Size",
        "purchase_postponement": "Need size confidence",
        "decision_behavior": "Review checking",
        "user_segment": "Fit-Conscious Shoppers",
        "unmet_need": "Sizing cross-brand consistency tool or visual fit adviser.",
        "emotion": "hesitant",
        "product_category": "clothing",
        "evidence": "hesitant to buy because the size chart is very confusing. Some reviews say buy one size larger, others say true to size",
        "confidence": 0.95
    },
    "gp_04": {
        "intent": "Genuine Purchase Intent",
        "barrier": "Availability",
        "purchase_stage": "wishlisted",
        "uncertainty": "Size",
        "purchase_postponement": "Other",
        "decision_behavior": "Review checking",
        "user_segment": "Fit-Conscious Shoppers",
        "unmet_need": "Low stock alert and sizing reservation queue.",
        "emotion": "frustrated",
        "product_category": "clothing",
        "evidence": "half of them are out of stock in my size (S)",
        "confidence": 0.9
    },
    "gp_06": {
        "intent": "Genuine Purchase Intent",
        "barrier": "Quality",
        "purchase_stage": "wishlisted",
        "uncertainty": "Fabric",
        "purchase_postponement": "Uncertain product quality",
        "decision_behavior": "Review checking",
        "user_segment": "Comparison Shoppers",
        "unmet_need": "Close-up fabric video reviews or fabric transparency indicators.",
        "emotion": "skeptical",
        "product_category": "clothing",
        "evidence": "not sure about the material. It says 'polyester blend' but in some photos it looks very thin and cheap",
        "confidence": 0.95
    },
    "gp_08": {
        "intent": "Bookmarking",
        "barrier": "Other",
        "purchase_stage": "consideration",
        "uncertainty": "Styling",
        "purchase_postponement": "Comparing products",
        "decision_behavior": "Product comparison",
        "user_segment": "Inspiration Collectors",
        "unmet_need": "Wishlist folders/organization boards.",
        "emotion": "overwhelmed",
        "product_category": "unknown",
        "evidence": "get overwhelmed trying to choose what to buy, so I end up buying nothing",
        "confidence": 0.9
    },
    "as_01": {
        "intent": "Inspiration",
        "barrier": "Styling",
        "purchase_stage": "wishlisted",
        "uncertainty": "Styling",
        "purchase_postponement": "Not urgent",
        "decision_behavior": "Social media validation",
        "user_segment": "Inspiration Collectors",
        "unmet_need": "Mix-and-match outfit builder in wishlist.",
        "emotion": "hesitant",
        "product_category": "clothing",
        "evidence": "don't know how to style them or what they will look like together",
        "confidence": 0.95
    },
    "as_02": {
        "intent": "Social Validation",
        "barrier": "Reviews/Trust",
        "purchase_stage": "wishlisted",
        "uncertainty": "Reviews",
        "purchase_postponement": "Need more reviews",
        "decision_behavior": "Social media validation",
        "user_segment": "Social Validators",
        "unmet_need": "Collaborative shared wishlists with voting features.",
        "emotion": "indifferent",
        "product_category": "clothing",
        "evidence": "want to get my friends' feedback... sharing wishlisted items is very clunky",
        "confidence": 0.85
    },
    "as_03": {
        "intent": "Genuine Purchase Intent",
        "barrier": "Size/Fit",
        "purchase_stage": "wishlisted",
        "uncertainty": "Fit",
        "purchase_postponement": "Need size confidence",
        "decision_behavior": "Offline validation",
        "user_segment": "Fit-Conscious Shoppers",
        "unmet_need": "3D virtual fitting room or body shape sizing predictor.",
        "emotion": "hesitant",
        "product_category": "clothing",
        "evidence": "denim fit is so tricky. Without a virtual fitting room... just don't feel confident buying",
        "confidence": 0.95
    },
    "as_05": {
        "intent": "Genuine Purchase Intent",
        "barrier": "Reviews/Trust",
        "purchase_stage": "wishlisted",
        "uncertainty": "Quality",
        "purchase_postponement": "Need more reviews",
        "decision_behavior": "Review checking",
        "user_segment": "Social Validators",
        "unmet_need": "Customer photo reviews for premium items.",
        "emotion": "skeptical",
        "product_category": "clothing",
        "evidence": "quite expensive... but there are no user reviews or photos on the product page",
        "confidence": 0.95
    },
    "t1_rd01": {
        "intent": "Inspiration",
        "barrier": "Price",
        "purchase_stage": "wishlisted",
        "uncertainty": "Price/value",
        "purchase_postponement": "Waiting for price drop",
        "decision_behavior": "Price comparison",
        "user_segment": "Deal Watchers",
        "unmet_need": "Separate aspirational mood-boards from active shopping wishlists.",
        "emotion": "neutral",
        "product_category": "clothing",
        "evidence": "aspirational board... will never buy because they are too expensive",
        "confidence": 0.9
    },
    "t1_rd02": {
        "intent": "Product Comparison",
        "barrier": "Quality",
        "purchase_stage": "wishlisted",
        "uncertainty": "Color",
        "purchase_postponement": "Uncertain product quality",
        "decision_behavior": "YouTube validation",
        "user_segment": "Comparison Shoppers",
        "unmet_need": "Daylight mode buyer photos and video reviews.",
        "emotion": "cautious",
        "product_category": "footwear",
        "evidence": "product photos on the app are highly edited and studio-lit. I want to see how the sneakers look in natural daylight",
        "confidence": 0.9
    },
    "t1_rd03": {
        "intent": "Product Comparison",
        "barrier": "Other",
        "purchase_stage": "consideration",
        "uncertainty": "Fabric",
        "purchase_postponement": "Comparing products",
        "decision_behavior": "Product comparison",
        "user_segment": "Comparison Shoppers",
        "unmet_need": "Side-by-side comparison matrices inside the wishlist.",
        "emotion": "overwhelmed",
        "product_category": "clothing",
        "evidence": "comparing them is such a headache... overwhelmed by the comparison process... didn't buy anything",
        "confidence": 0.95
    },
    "t1_rd05": {
        "intent": "Genuine Purchase Intent",
        "barrier": "Size/Fit",
        "purchase_stage": "wishlisted",
        "uncertainty": "Fit",
        "purchase_postponement": "Need size confidence",
        "decision_behavior": "Offline validation",
        "user_segment": "Fit-Conscious Shoppers",
        "unmet_need": "Virtual 3D body sizing model.",
        "emotion": "hesitant",
        "product_category": "clothing",
        "evidence": "hesitant to order because blazer tailoring is very sensitive. If the shoulders are loose or sleeves are long, it looks bad",
        "confidence": 0.95
    },
    "forms_0": {
        "intent": "Genuine Purchase Intent",
        "barrier": "Size/Fit",
        "purchase_stage": "wishlisted",
        "uncertainty": "Size",
        "purchase_postponement": "Need size confidence",
        "decision_behavior": "Review checking",
        "user_segment": "Fit-Conscious Shoppers",
        "unmet_need": "Cross-brand standard size mapping tools.",
        "emotion": "cautious",
        "product_category": "clothing",
        "evidence": "Unsure of how the shirt will fit me since sizes vary across brands. Myntra's sizing tool is not reliable",
        "confidence": 0.9
    },
    "forms_1": {
        "intent": "Product Comparison",
        "barrier": "Other",
        "purchase_stage": "consideration",
        "uncertainty": "Appearance",
        "purchase_postponement": "Comparing products",
        "decision_behavior": "Social media validation",
        "user_segment": "Comparison Shoppers",
        "unmet_need": "Shared wishlist board with custom votes.",
        "emotion": "overwhelmed",
        "product_category": "clothing",
        "evidence": "overwhelmed by having too many similar choices in my wishlist (e.g., 5 red sarees). I don't know how to compare them easily.",
        "confidence": 0.9
    },
    "forms_2": {
        "intent": "Genuine Purchase Intent",
        "barrier": "Quality",
        "purchase_stage": "wishlisted",
        "uncertainty": "Quality",
        "purchase_postponement": "Uncertain product quality",
        "decision_behavior": "Review checking",
        "user_segment": "Social Validators",
        "unmet_need": "Verified material authenticity ratings and customer reviews.",
        "emotion": "worried",
        "product_category": "footwear",
        "evidence": "worried about the quality. Sometimes the leather looks shiny in pictures but turns out to be plastic",
        "confidence": 0.95
    },
    "forms_3": {
        "intent": "Bookmarking",
        "barrier": "Other",
        "purchase_stage": "wishlisted",
        "uncertainty": "Styling",
        "purchase_postponement": "Not urgent",
        "decision_behavior": "Review checking",
        "user_segment": "Inspiration Collectors",
        "unmet_need": "Out-of-stock and low stock alerts for bookmarked items.",
        "emotion": "indifferent",
        "product_category": "accessories",
        "evidence": "bookmark and forget. I don't really have immediate purchase intent.",
        "confidence": 0.8
    },
    "forms_4": {
        "intent": "Price Tracking",
        "barrier": "Price",
        "purchase_stage": "wishlisted",
        "uncertainty": "Price/value",
        "purchase_postponement": "Waiting for price drop",
        "decision_behavior": "Price comparison",
        "user_segment": "Deal Watchers",
        "unmet_need": "Natural sale notifications and price trackers.",
        "emotion": "hesitant",
        "product_category": "clothing",
        "evidence": "out of my budget right now. I will buy only when the price drops.",
        "confidence": 0.95
    }
}

# Controlled categories as per specifications
VALID_INTENTS = {"Genuine Purchase Intent", "Price Tracking", "Product Comparison", "Bookmarking", "Inspiration", "Social Validation", "Unclear", "Not Mentioned"}
VALID_BARRIERS = {"Price", "Size/Fit", "Quality", "Reviews/Trust", "Styling", "Occasion", "Delivery", "Returns", "Availability", "Product Information", "Other", "Not Mentioned"}
VALID_UNCERTAINTIES = {"Fit", "Size", "Fabric", "Quality", "Color", "Appearance", "Styling", "Occasion", "Reviews", "Brand/Seller Trust", "Price/Value", "Other", "Not Mentioned"}
VALID_POSTPONEMENTS = {"Waiting for Sale", "Waiting for Price Drop", "Comparing Products", "Need More Reviews", "Need Size Confidence", "Waiting for Occasion", "Budget Constraint", "Not Urgent", "Product Uncertainty", "Other", "Not Mentioned"}
VALID_BEHAVIORS = {"Product Comparison", "Price Comparison", "Review Checking", "Size Research", "Social Validation", "YouTube Research", "Reddit Research", "Google/Search Research", "Brand Comparison", "Offline Validation", "Other", "Not Mentioned"}
VALID_SEGMENTS = {"Deal Watchers", "Fit-Conscious Shoppers", "Comparison Shoppers", "Inspiration Collectors", "Occasion Shoppers", "Social Validators", "Unknown"}

def normalize_extracted_fields(res):
    """
    Standardizes keys and values extracted from any source (cache, API, fallback)
    to match the exact casing and names of the specifications.
    """
    # Intent normalization
    intent = res.get("intent", "Not Mentioned")
    if intent not in VALID_INTENTS:
        intent_map = {"None": "Not Mentioned", "Unclear": "Unclear"}
        intent = intent_map.get(intent, "Not Mentioned")
    res["intent"] = intent
    
    # Barrier normalization
    barrier = res.get("barrier", "Not Mentioned")
    if barrier not in VALID_BARRIERS:
        barrier_map = {"None": "Not Mentioned", "Other": "Other"}
        barrier = barrier_map.get(barrier, "Not Mentioned")
    res["barrier"] = barrier
    
    # Uncertainty normalization
    uncertainty = res.get("uncertainty", "Not Mentioned")
    uncertainty_map = {
        "Seller/brand trust": "Brand/Seller Trust",
        "Price/value": "Price/Value",
        "None": "Not Mentioned",
        "Fabric": "Fabric",
        "Size": "Size",
        "Fit": "Fit"
    }
    if uncertainty in uncertainty_map:
        uncertainty = uncertainty_map[uncertainty]
    if uncertainty not in VALID_UNCERTAINTIES:
        uncertainty = "Not Mentioned"
    res["uncertainty"] = uncertainty
    
    # Postponement normalization
    postponement = res.get("purchase_postponement", "Not Mentioned")
    postponement_map = {
        "Waiting for sale": "Waiting for Sale",
        "Waiting for price drop": "Waiting for Price Drop",
        "Comparing products": "Comparing Products",
        "Need more reviews": "Need More Reviews",
        "Need size confidence": "Need Size Confidence",
        "Waiting for occasion": "Waiting for Occasion",
        "Budget constraint": "Budget Constraint",
        "Not urgent": "Not Urgent",
        "Uncertain product quality": "Product Uncertainty",
        "None": "Not Mentioned"
    }
    if postponement in postponement_map:
        postponement = postponement_map[postponement]
    if postponement not in VALID_POSTPONEMENTS:
        postponement = "Not Mentioned"
    res["purchase_postponement"] = postponement
    
    # Behavior normalization
    behavior = res.get("decision_behavior", "Not Mentioned")
    behavior_map = {
        "Product comparison": "Product Comparison",
        "Price comparison": "Price Comparison",
        "Review checking": "Review Checking",
        "Social media validation": "Social Validation",
        "YouTube validation": "YouTube Research",
        "Reddit/community validation": "Reddit Research",
        "Google search": "Google/Search Research",
        "Brand comparison": "Brand Comparison",
        "Offline validation": "Offline Validation",
        "None": "Not Mentioned"
    }
    if behavior in behavior_map:
        behavior = behavior_map[behavior]
    if behavior not in VALID_BEHAVIORS:
        behavior = "Not Mentioned"
    res["decision_behavior"] = behavior
    
    # Segment normalization
    segment = res.get("user_segment", "Unknown")
    if segment not in VALID_SEGMENTS:
        segment_map = {"None": "Unknown"}
        segment = segment_map.get(segment, "Unknown")
    res["user_segment"] = segment
    
    # Unmet need category normalization
    if "unmet_need_category" not in res or res["unmet_need_category"] not in VALID_BARRIERS:
        res["unmet_need_category"] = res.get("barrier", "Not Mentioned")
        
    # Evidence strength normalization
    if "evidence_strength" not in res or res["evidence_strength"] not in ["Low", "Medium", "High"]:
        if res.get("unmet_need") and res["unmet_need"] != "Insufficient evidence.":
            res["evidence_strength"] = "Medium"
        else:
            res["evidence_strength"] = "Low"
            
    return res

def fallback_heuristic_extraction(text):
    """
    Rule-based extraction when Gemini is offline and record is not in cache.
    """
    text_lower = text.lower()
    
    # Intent mapping
    intent = "Not Mentioned"
    if "compare" in text_lower or "decide" in text_lower:
        intent = "Product Comparison"
    elif "price" in text_lower or "budget" in text_lower or "drop" in text_lower or "sale" in text_lower:
        intent = "Price Tracking"
    elif "bookmark" in text_lower or "save" in text_lower:
        intent = "Bookmarking"
    elif "inspiration" in text_lower or "lookbook" in text_lower:
        intent = "Inspiration"
    elif "friend" in text_lower or "share" in text_lower or "feedback" in text_lower or "youtube" in text_lower or "reddit" in text_lower:
        intent = "Social Validation"
    elif "buy" in text_lower or "checkout" in text_lower or "purchase" in text_lower:
        intent = "Genuine Purchase Intent"
        
    # Barrier mapping
    barrier = "Not Mentioned"
    if any(w in text_lower for w in ["expensive", "price", "budget", "cost", "afford"]):
        barrier = "Price"
    elif any(w in text_lower for w in ["size", "fit", "sizing", "tight", "loose", "length"]):
        barrier = "Size/Fit"
    elif any(w in text_lower for w in ["quality", "material", "fabric", "thin", "cheap"]):
        barrier = "Quality"
    elif any(w in text_lower for w in ["review", "photo", "pic", "trust", "star", "friend", "social"]):
        barrier = "Reviews/Trust"
    elif "style" in text_lower or "coordinate" in text_lower or "outfit" in text_lower:
        barrier = "Styling"
    elif "occasion" in text_lower or "wedding" in text_lower or "party" in text_lower:
        barrier = "Occasion"
    elif "delivery" in text_lower or "shipping" in text_lower or "transit" in text_lower:
        barrier = "Delivery"
    elif "return" in text_lower or "refund" in text_lower:
        barrier = "Returns"
    elif "stock" in text_lower or "avail" in text_lower:
        barrier = "Availability"
    elif "info" in text_lower or "details" in text_lower or "description" in text_lower:
        barrier = "Product Information"

    # Uncertainty mapping
    uncertainty = "Not Mentioned"
    if "fit" in text_lower:
        uncertainty = "Fit"
    elif "size" in text_lower:
        uncertainty = "Size"
    elif "fabric" in text_lower or "material" in text_lower:
        uncertainty = "Fabric"
    elif "quality" in text_lower:
        uncertainty = "Quality"
    elif "color" in text_lower or "colour" in text_lower:
        uncertainty = "Color"
    elif "look" in text_lower or "photo" in text_lower:
        uncertainty = "Appearance"
    elif "style" in text_lower:
        uncertainty = "Styling"
    elif "occasion" in text_lower or "event" in text_lower:
        uncertainty = "Occasion"
    elif "review" in text_lower:
        uncertainty = "Reviews"
    elif "trust" in text_lower or "fake" in text_lower:
        uncertainty = "Brand/Seller Trust"
    elif "price" in text_lower or "value" in text_lower:
        uncertainty = "Price/Value"

    # Postponement mapping
    postponement = "Not Mentioned"
    if "sale" in text_lower:
        postponement = "Waiting for Sale"
    elif "drop" in text_lower or "discount" in text_lower:
        postponement = "Waiting for Price Drop"
    elif "compare" in text_lower:
        postponement = "Comparing Products"
    elif "review" in text_lower:
        postponement = "Need More Reviews"
    elif "size" in text_lower or "fit" in text_lower:
        postponement = "Need Size Confidence"
    elif "wedding" in text_lower or "occasion" in text_lower or "festival" in text_lower:
        postponement = "Waiting for Occasion"
    elif "budget" in text_lower or "afford" in text_lower:
        postponement = "Budget Constraint"
    elif "forget" in text_lower or "casual" in text_lower:
        postponement = "Not Urgent"
    elif "quality" in text_lower or "cheap" in text_lower:
        postponement = "Product Uncertainty"

    # Behavior mapping
    behavior = "Not Mentioned"
    if "compare" in text_lower:
        behavior = "Product Comparison"
    elif "brand" in text_lower:
        behavior = "Brand Comparison"
    elif "price" in text_lower or "budget" in text_lower:
        behavior = "Price Comparison"
    elif "review" in text_lower or "photo" in text_lower:
        behavior = "Review Checking"
    elif "youtube" in text_lower or "video" in text_lower:
        behavior = "YouTube Research"
    elif "reddit" in text_lower or "community" in text_lower:
        behavior = "Reddit Research"
    elif "google" in text_lower or "search" in text_lower:
        behavior = "Google/Search Research"
    elif "store" in text_lower or "try" in text_lower or "retail" in text_lower:
        behavior = "Offline Validation"
    elif "friend" in text_lower or "sister" in text_lower or "share" in text_lower:
        behavior = "Social Validation"

    # Segment mapping
    segment = "Unknown"
    if barrier == "Price" or intent == "Price Tracking":
        segment = "Deal Watchers"
    elif barrier == "Size/Fit":
        segment = "Fit-Conscious Shoppers"
    elif behavior == "Product Comparison" or intent == "Product Comparison":
        segment = "Comparison Shoppers"
    elif intent == "Inspiration":
        segment = "Inspiration Collectors"
    elif barrier == "Occasion":
        segment = "Occasion Shoppers"
    elif intent == "Social Validation" or behavior == "Social Validation":
        segment = "Social Validators"

    # Unmet need text matching
    unmet_need = "Insufficient evidence."
    unmet_need_category = barrier
    evidence_strength = "Low"
    
    if barrier == "Size/Fit":
        unmet_need = "Reliable cross-brand body sizing checker."
        evidence_strength = "Medium"
    elif barrier == "Price":
        unmet_need = "Natural markdown alert and budget tracking."
        evidence_strength = "Medium"
    elif behavior == "Product Comparison":
        unmet_need = "Side-by-side wishlist attribute comparison boards."
        evidence_strength = "Medium"
    elif barrier == "Quality":
        unmet_need = "Verified natural daylight customer review media."
        evidence_strength = "Medium"

    evidence = "Insufficient evidence."
    words = text.split()
    if len(words) >= 3:
        evidence = text
        
    return {
        "intent": intent,
        "barrier": barrier,
        "uncertainty": uncertainty,
        "purchase_postponement": postponement,
        "decision_behavior": behavior,
        "user_segment": segment,
        "unmet_need": unmet_need,
        "unmet_need_category": unmet_need_category,
        "evidence_strength": evidence_strength,
        "purchase_stage": "wishlisted",
        "emotion": "neutral",
        "product_category": "unknown",
        "evidence": evidence,
        "confidence": 0.5
    }

def call_gemini_api(text):
    """
    Calls the Gemini API to extract structured AI user intent & barriers.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        prompt = f"""
        Analyze this shopper feedback text from Myntra.
        Extract the following fields in strict JSON format:
        
        {{
            "intent": "Genuine Purchase Intent" | "Price Tracking" | "Product Comparison" | "Bookmarking" | "Inspiration" | "Social Validation" | "Unclear" | "Not Mentioned",
            "barrier": "Price" | "Size/Fit" | "Quality" | "Reviews/Trust" | "Styling" | "Occasion" | "Delivery" | "Returns" | "Availability" | "Product Information" | "Other" | "Not Mentioned",
            "uncertainty": "Fit" | "Size" | "Fabric" | "Quality" | "Color" | "Appearance" | "Styling" | "Occasion" | "Reviews" | "Brand/Seller Trust" | "Price/Value" | "Other" | "Not Mentioned",
            "purchase_postponement": "Waiting for Sale" | "Waiting for Price Drop" | "Comparing Products" | "Need More Reviews" | "Need Size Confidence" | "Waiting for Occasion" | "Budget Constraint" | "Not Urgent" | "Product Uncertainty" | "Other" | "Not Mentioned",
            "decision_behavior": "Product Comparison" | "Price Comparison" | "Review Checking" | "Size Research" | "Social Validation" | "YouTube Research" | "Reddit Research" | "Google/Search Research" | "Brand Comparison" | "Offline Validation" | "Other" | "Not Mentioned",
            "user_segment": "Deal Watchers" | "Fit-Conscious Shoppers" | "Comparison Shoppers" | "Inspiration Collectors" | "Occasion Shoppers" | "Social Validators" | "Unknown",
            "unmet_need": "string (Identify recurring unmet needs. If evidence is insufficient, return 'Insufficient evidence.')",
            "unmet_need_category": "match to one of VALID_BARRIERS value",
            "evidence_strength": "Low" | "Medium" | "High",
            "purchase_stage": "discovery" | "consideration" | "wishlisted" | "checkout" | "purchased" | "abandoned",
            "emotion": "string (frustrated, hesitant, skeptical, happy, neutral, etc.)",
            "product_category": "clothing" | "footwear" | "accessories" | "unknown",
            "evidence": "string (exact verbatim substring from text. If evidence is insufficient, return 'Insufficient evidence.')",
            "confidence": 0.0 to 1.0 (float)
        }}
        
        Shopper Feedback: "{text}"
        JSON Output:
        """
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        result_dict = json.loads(response.text)
        return result_dict
        
    except Exception as e:
        print(f"Gemini API request failed: {e}")
        return None

def analyze_review(review_id, text):
    """
    Extracts structured user intent and barriers for a single review.
    """
    review_id_str = str(review_id)
    
    # 1. Try local cache
    if review_id_str in DEMO_AI_CACHE:
        result = DEMO_AI_CACHE[review_id_str].copy()
        result["extraction_source"] = "local_cache"
        return normalize_extracted_fields(result)
        
    # 2. Try Live API
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        api_result = call_gemini_api(text)
        if api_result:
            api_result["extraction_source"] = "gemini_api"
            return normalize_extracted_fields(api_result)
            
    # 3. Try Heuristic Fallback
    fallback_result = fallback_heuristic_extraction(text)
    fallback_result["extraction_source"] = "heuristic_fallback"
    return normalize_extracted_fields(fallback_result)

def process_relevant_reviews(discovery_relevant_path="data/discovery_dataset.csv",
                             output_path="data/processed/analyzed_reviews.csv"):
    """
    Ingests discovery-relevant reviews, processes each with AI analyzer, and saves analysis.
    """
    if not os.path.exists(discovery_relevant_path):
        discovery_relevant_path = "data/processed/discovery_relevant.csv"
        
    if not os.path.exists(discovery_relevant_path):
        print(f"Discovery relevant file not found at {discovery_relevant_path}")
        return None
        
    df = pd.read_csv(discovery_relevant_path)
    # Support both string "YES" and boolean True/False
    relevant_df = df[df["discovery_relevant"].astype(str).str.upper().isin(["YES", "TRUE"])].copy()
    
    results = []
    for idx, row in relevant_df.iterrows():
        review_id = row.get("id", row.get("review_id", f"gen_{idx}"))
        text = row["text"]
        
        analysis = analyze_review(review_id, text)
        results.append(analysis)
        
    results_df = pd.DataFrame(results)
    combined_df = pd.concat([relevant_df.reset_index(drop=True), results_df.reset_index(drop=True)], axis=1)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined_df.to_csv(output_path, index=False)
    print(f"AI User Intent and Barrier extraction complete. Processed {len(combined_df)} relevant reviews.")
    
    return combined_df

if __name__ == "__main__":
    process_relevant_reviews()

if __name__ == "__main__":
    process_relevant_reviews()
