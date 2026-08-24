import os
import json
import pandas as pd

# Detailed PM insight templates mapping to clusters
PM_INSIGHT_DATA = {
    "Fit and Sizing Uncertainty": {
        "workaround": "Users try to cross-reference multiple contradictory reviews, search YouTube for sizing guides, or visit offline physical stores to try on similar sizes.",
        "opportunity": "Introduce an interactive 'Sizing Companion' directly on the wishlist page. Users input key measurements (height, weight, chest), and the app visualizes fit confidence (e.g., 'Fits like a glove' or 'Shoulders might be tight') using aggregation of previous buyer data.",
        "hypothesis": "If Myntra helps users visualize garment fit on their specific body measurements using aggregated past-buyer reviews, then wishlist-to-purchase conversion will improve because buyers will checkout with high sizing confidence and less fear of return hassles."
    },
    "Choice and Decision Overload": {
        "workaround": "Users open multiple tabs, take screenshots to compare items side-by-side, or send individual links to friends on WhatsApp for second opinions.",
        "opportunity": "Implement an interactive 'Wishlist Comparison Board' that displays user-selected wishlisted items side-by-side, comparing fabric material, length, delivery speed, and customer ratings. Include a 'Share Board' feature for collaborative voting.",
        "hypothesis": "If Myntra helps users compare their saved items side-by-side on key styling and logistic parameters, then wishlist-to-purchase conversion will improve because shoppers can resolve choice paralysis without leaving the app."
    },
    "Material and Visual Disconnect": {
        "workaround": "Shoppers search external social media platforms (YouTube hauls, Instagram) to find unedited photos or videos of the items in daylight.",
        "opportunity": "Add a 'Daylight Mode' media tab to product review sections, aggregating buyer-uploaded videos and images taken in natural sunlight, highlighting fabric close-ups and material weight details.",
        "hypothesis": "If Myntra helps users view real buyer photos and close-up fabric videos under natural daylight conditions, then wishlist-to-purchase conversion will improve because fabric quality and color representation doubts will be eliminated."
    },
    "Social Proof & Reviews Deficit": {
        "workaround": "Shoppers leave items in their wishlists indefinitely, waiting for reviews to appear, or search other e-commerce sites to find matching product reviews.",
        "opportunity": "Launch a non-monetary community incentive program (e.g., 'Style Reviewer' badges or priority styling consultations) to motivate buyers to write the first reviews and upload photos for unreviewed items, particularly premium stock.",
        "hypothesis": "If Myntra helps users access customer reviews on newly added or premium catalog items, then wishlist-to-purchase conversion will improve because purchase hesitation surrounding unreviewed products will decrease."
    },
    "Styling and Outfit Coordination Uncertainty": {
        "workaround": "Shoppers save items and mentally try to coordinate outfits, or browse external fashion blogs for styling inspiration.",
        "opportunity": "Develop a 'Mix-and-Match Outfit Builder' tool in the wishlist, allowing users to drag and drop wishlisted tops, bottoms, and shoes onto a virtual canvas to see how they coordinate together.",
        "hypothesis": "If Myntra helps users visualize how different wishlisted items look together as a single styled outfit, then wishlist-to-purchase conversion will improve because styling hesitation will be resolved."
    },
    "Price Hesitation / Budget Constraints": {
        "workaround": "Shoppers manually refresh the wishlist daily to check if the price has dropped or if there is a natural markdown.",
        "opportunity": "Provide a 'Low-Stock Alert' and natural price-drop tracker for wishlisted items, notifying users when items in their size are running out during seasonal sales.",
        "hypothesis": "If Myntra helps users track price trends and stock limits without manual checking, then wishlist-to-purchase conversion will improve because price-conscious shoppers can checkout during organic markdown events."
    },
    "Availability and Stock Restocking Issues": {
        "workaround": "Shoppers wait for replenishment or manually search other apps for similar items that are currently in stock.",
        "opportunity": "Introduce a 'Notify Me / Waitlist' reservation queue for wishlisted items, alerting users immediately when their size is restocked or when stock is running critically low.",
        "hypothesis": "If Myntra helps users reserve or receive high-priority alerts for restocked items, then wishlist-to-purchase conversion will improve because stockout friction will be mitigated."
    },
    "Aspirational Bookmarking / Low Purchase Intent": {
        "workaround": "Users save items as a virtual 'pinterest' board for inspiration, with no immediate intention to purchase.",
        "opportunity": "Create separate 'Aspirational Moodboards' from 'Active Wishlists' to keep active shopping lists clutter-free.",
        "hypothesis": "If Myntra helps users organize aspirational bookmarks separately from active purchase lists, then wishlist-to-purchase conversion will improve because active cart lists will remain focused on real buying intent."
    }
}

def generate_opportunities(clusters):
    """
    Takes problem clusters, calculates opportunity scores, ranks them,
    and generates detailed PM insights.
    """
    prioritized_opportunities = []
    
    for c in clusters:
        name = c["name"]
        freq_pct = c["percentage"]
        severity = c["severity"]
        proximity = c["purchase_proximity"]
        confidence = c["confidence"]
        
        # Opportunity Score calculation: Frequency % * Severity * Proximity * Confidence
        # Max theoretical raw score: 100 * 5.0 * 1.0 * 1.0 = 500
        # Normalize to 0-100 by dividing by 5.0
        raw_score = freq_pct * severity * proximity * confidence
        opp_score = round(raw_score / 5.0, 2)
        
        # Load PM Insight details
        insight_info = PM_INSIGHT_DATA.get(name, {
            "workaround": "unknown",
            "opportunity": "unknown",
            "hypothesis": "unknown"
        })
        
        # Get representative evidence
        evidence_samples = [e["text"] for e in c["evidence"][:2]]
        
        # Get who is affected (based on evidence categories and stages)
        who = f"Shoppers in '{c['purchase_stage_concentration']}' stage, primarily discussing '{', '.join(c['sources'])}' channels."
        
        prioritized_opportunities.append({
            "name": name,
            "problem": c["description"],
            "opp_score": opp_score,
            "frequency_pct": freq_pct,
            "severity": severity,
            "purchase_proximity": proximity,
            "confidence": confidence,
            "who": who,
            "evidence": evidence_samples,
            "workaround": insight_info["workaround"],
            "opportunity": insight_info["opportunity"],
            "hypothesis": insight_info["hypothesis"],
            "sources": c["sources"]
        })
        
    # Sort by opportunity score descending
    prioritized_opportunities = sorted(prioritized_opportunities, key=lambda x: x["opp_score"], reverse=True)
    return prioritized_opportunities

if __name__ == "__main__":
    from clustering import cluster_problems
    clusters = cluster_problems()
    opps = generate_opportunities(clusters)
    for idx, o in enumerate(opps):
        print(f"Rank {idx+1}: {o['name']} - Score: {o['opp_score']}")
