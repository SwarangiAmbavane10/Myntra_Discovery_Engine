import os
import pandas as pd
import json

# Define the PM-level problem clusters and map the new column values to them
CLUSTER_DEFINITIONS = {
    "Fit and Sizing Uncertainty": {
        "filter_col": "barrier",
        "filter_vals": ["Size/Fit"],
        "description": "Shoppers are hesitant to buy wishlisted fashion items due to fear of incorrect fit or brand sizing discrepancies, wanting 3D fit tools or body measurements comparison.",
        "severity": 4.5,
        "purchase_proximity": 0.9
    },
    "Choice and Decision Overload": {
        "filter_col": "decision_behavior",
        "filter_vals": ["Product Comparison", "Product comparison"],
        "description": "Shoppers wishlist multiple similar products and become overwhelmed by comparison friction, ending up buying nothing.",
        "severity": 4.0,
        "purchase_proximity": 0.85
    },
    "Material and Visual Disconnect": {
        "filter_col": "barrier",
        "filter_vals": ["Quality"],
        "description": "Shoppers worry that fabrics will look thin/cheap or colors will vary from studio photos, wanting natural daylight views or close-up fabric videos.",
        "severity": 4.2,
        "purchase_proximity": 0.8
    },
    "Social Proof & Reviews Deficit": {
        "filter_col": "barrier",
        "filter_vals": ["Reviews/Trust"],
        "description": "Shoppers postpone purchases of expensive or premium products because they lack user reviews, ratings, and customer-uploaded photos.",
        "severity": 3.8,
        "purchase_proximity": 0.75
    },
    "Styling and Outfit Coordination Uncertainty": {
        "filter_col": "barrier",
        "filter_vals": ["Styling"],
        "description": "Shoppers wishlist unique clothes but hesitate to checkout because they do not know how to style them or if they match other items they own.",
        "severity": 3.5,
        "purchase_proximity": 0.7
    },
    "Price Hesitation / Budget Constraints": {
        "filter_col": "barrier",
        "filter_vals": ["Price"],
        "description": "Shoppers wishlist items outside their budget and wait indefinitely for discounts or sales.",
        "severity": 3.0,
        "purchase_proximity": 0.6
    },
    "Availability and Stock Restocking Issues": {
        "filter_col": "barrier",
        "filter_vals": ["Availability"],
        "description": "Wishlisted products run out of stock in the user's size before checkout, due to lack of low-stock alert systems.",
        "severity": 3.8,
        "purchase_proximity": 0.95
    },
    "Aspirational Bookmarking / Low Purchase Intent": {
        "filter_col": "intent",
        "filter_vals": ["Bookmarking"],
        "description": "Shoppers wishlist items strictly as a mood-board or catalog save, without immediate intention to purchase.",
        "severity": 1.5,
        "purchase_proximity": 0.3
    }
}

def cluster_problems(analyzed_csv_path="data/processed/analyzed_reviews.csv"):
    """
    Groups analyzed reviews into clusters based on the new variable classifications.
    Calculates metrics for each cluster.
    """
    if not os.path.exists(analyzed_csv_path):
        print(f"Analyzed reviews file not found at {analyzed_csv_path}")
        return []
        
    df = pd.read_csv(analyzed_csv_path)
    total_relevant = len(df)
    
    clusters = []
    
    for cluster_name, config in CLUSTER_DEFINITIONS.items():
        col = config["filter_col"]
        vals = config["filter_vals"]
        
        # Filter reviews belonging to this cluster
        cluster_df = df[df[col].isin(vals)]
        count = len(cluster_df)
        
        if count == 0:
            continue
            
        percentage = (count / total_relevant) * 100
        sources = list(cluster_df["source"].unique())
        
        # Collect evidence (user quote, source, id, url)
        evidence_list = []
        for idx, row in cluster_df.iterrows():
            evidence_list.append({
                "source": row["source"],
                "review_id": row.get("review_id", row.get("id", f"gen_{idx}")),
                "text": row["text"],
                "url": row.get("url") if pd.notna(row.get("url")) else None
            })
            
        # Determine purchase stage concentration (mode)
        stages = cluster_df["purchase_stage"].dropna()
        purchase_stage_concentration = stages.mode()[0] if not stages.empty else "wishlisted"
        
        # Average confidence
        avg_confidence = float(cluster_df["confidence"].mean()) if "confidence" in cluster_df.columns else 0.8
        
        clusters.append({
            "name": cluster_name,
            "description": config["description"],
            "count": count,
            "percentage": round(percentage, 2),
            "sources": sources,
            "evidence": evidence_list,
            "severity": config["severity"],
            "purchase_proximity": config["purchase_proximity"],
            "confidence": round(avg_confidence, 2),
            "purchase_stage_concentration": purchase_stage_concentration
        })
        
    # Sort clusters by size
    clusters = sorted(clusters, key=lambda x: x["count"], reverse=True)
    print(f"Problem clustering complete. Identified {len(clusters)} problem clusters.")
    
    return clusters

if __name__ == "__main__":
    clusters = cluster_problems()
    for c in clusters:
        print(f"{c['name']} (n={c['count']}) - {c['percentage']}%")
