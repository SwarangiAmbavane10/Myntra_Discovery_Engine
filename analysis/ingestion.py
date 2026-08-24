# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
from datetime import datetime

# Common standardized schema columns
CANONICAL_COLUMNS = [
    "id", "source", "platform", "date", "author", "title", "text", 
    "rating", "url", "product", "product_id", "category", "brand", 
    "engagement", "language"
]

def format_date(date_val):
    if pd.isna(date_val) or date_val is None:
        return None
    try:
        if isinstance(date_val, (int, float)):
            # Handle timestamps
            return datetime.utcfromtimestamp(date_val).strftime("%Y-%m-%d %H:%M:%S")
        # Parse standard string dates
        parsed_dt = pd.to_datetime(date_val, errors="coerce")
        if pd.notna(parsed_dt):
            return parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    return str(date_val)

def normalize_to_schema(record):
    """
    Ensures that a record dictionary contains exactly the 15 canonical columns.
    Missing fields are filled with None.
    """
    normalized = {}
    for col in CANONICAL_COLUMNS:
        normalized[col] = record.get(col, None)
    # Ensure rating is float/int or None
    if normalized["rating"] is not None:
        try:
            normalized["rating"] = float(normalized["rating"])
        except ValueError:
            normalized["rating"] = None
    # Format date
    if normalized["date"]:
        normalized["date"] = format_date(normalized["date"])
    return normalized

def ingest_raw_data(raw_dir="data/raw"):
    """
    Scans the raw data subdirectories, normalizes their schemas,
    and returns a master raw DataFrame.
    """
    all_records = []
    
    if not os.path.exists(raw_dir):
        print(f"Raw directory {raw_dir} does not exist.")
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    
    # 1. Google Play Reviews
    play_dir = os.path.join(raw_dir, "google_play")
    if os.path.exists(play_dir):
        for filename in os.listdir(play_dir):
            if filename.startswith(".") or filename == ".gitkeep":
                continue
            filepath = os.path.join(play_dir, filename)
            try:
                if filename.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            all_records.append(normalize_to_schema({
                                "id": item.get("reviewId", f"gp_fallback_{idx}"),
                                "source": "Google Play",
                                "platform": "Google Play",
                                "date": item.get("at"),
                                "author": item.get("userName"),
                                "text": item.get("content", ""),
                                "rating": item.get("score"),
                                "url": item.get("url"),
                                "product": item.get("app_name"),
                                "engagement": item.get("thumbsUpCount")
                            }))
                elif filename.endswith((".csv", ".xlsx")):
                    df = pd.read_excel(filepath) if filename.endswith(".xlsx") else pd.read_csv(filepath)
                    for idx, row in df.iterrows():
                        all_records.append(normalize_to_schema({
                            "id": str(row.get("reviewId", row.get("id", f"gp_fallback_{idx}"))),
                            "source": "Google Play",
                            "platform": "Google Play",
                            "date": row.get("at", row.get("date")),
                            "author": row.get("userName", row.get("author")),
                            "text": row.get("content", row.get("text", "")),
                            "rating": row.get("score", row.get("rating")),
                            "url": row.get("url"),
                            "product": row.get("app_name", row.get("product")),
                            "engagement": row.get("thumbsUpCount", row.get("engagement"))
                        }))
            except Exception as e:
                print(f"Error parsing Google Play file {filename}: {e}")

    # 2. Apple App Store Reviews
    app_store_dir = os.path.join(raw_dir, "app_store")
    if os.path.exists(app_store_dir):
        for filename in os.listdir(app_store_dir):
            if filename.startswith(".") or filename == ".gitkeep":
                continue
            filepath = os.path.join(app_store_dir, filename)
            try:
                if filename.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            title = item.get("title", "")
                            review_body = item.get("review", item.get("text", ""))
                            full_text = f"{title}: {review_body}" if title else review_body
                            all_records.append(normalize_to_schema({
                                "id": item.get("id", f"as_fallback_{idx}"),
                                "source": "App Store",
                                "platform": "App Store",
                                "date": item.get("date"),
                                "author": item.get("userName", item.get("author")),
                                "title": title,
                                "text": full_text,
                                "rating": item.get("rating"),
                                "url": item.get("url")
                            }))
                elif filename.endswith((".csv", ".xlsx")):
                    df = pd.read_excel(filepath) if filename.endswith(".xlsx") else pd.read_csv(filepath)
                    for idx, row in df.iterrows():
                        title = row.get("title", "")
                        review_body = row.get("review", row.get("text", ""))
                        full_text = f"{title}: {review_body}" if title else review_body
                        all_records.append(normalize_to_schema({
                            "id": str(row.get("id", f"as_fallback_{idx}")),
                            "source": "App Store",
                            "platform": "App Store",
                            "date": row.get("date"),
                            "author": row.get("userName", row.get("author")),
                            "title": title,
                            "text": full_text,
                            "rating": row.get("rating"),
                            "url": row.get("url")
                        }))
            except Exception as e:
                print(f"Error parsing App Store file {filename}: {e}")

    # 3. Reddit Posts/Comments
    reddit_dir = os.path.join(raw_dir, "reddit")
    if os.path.exists(reddit_dir):
        for filename in os.listdir(reddit_dir):
            if filename.startswith(".") or filename == ".gitkeep":
                continue
            filepath = os.path.join(reddit_dir, filename)
            try:
                if filename.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            all_records.append(normalize_to_schema({
                                "id": item.get("id", f"reddit_fallback_{idx}"),
                                "source": "Reddit",
                                "platform": "Reddit",
                                "date": item.get("created_utc"),
                                "author": item.get("author"),
                                "title": item.get("title") or item.get("post_title"),
                                "text": item.get("body", item.get("selftext", item.get("text", ""))),
                                "url": f"https://reddit.com{item.get('permalink', '')}" if item.get("permalink") else item.get("url"),
                                "category": item.get("subreddit"),
                                "engagement": item.get("score")
                            }))
                elif filename.endswith((".csv", ".xlsx")):
                    df = pd.read_excel(filepath) if filename.endswith(".xlsx") else pd.read_csv(filepath)
                    for idx, row in df.iterrows():
                        all_records.append(normalize_to_schema({
                            "id": str(row.get("id", f"reddit_fallback_{idx}")),
                            "source": "Reddit",
                            "platform": "Reddit",
                            "date": row.get("created_utc", row.get("date")),
                            "author": row.get("author"),
                            "title": row.get("title", row.get("post_title")),
                            "text": row.get("body", row.get("selftext", row.get("text", ""))),
                            "url": row.get("url", row.get("permalink")),
                            "category": row.get("subreddit", row.get("category")),
                            "engagement": row.get("score", row.get("engagement"))
                        }))
            except Exception as e:
                print(f"Error parsing Reddit file {filename}: {e}")

    # 4. YouTube Comments
    yt_dir = os.path.join(raw_dir, "youtube")
    if os.path.exists(yt_dir):
        for filename in os.listdir(yt_dir):
            if filename.startswith(".") or filename == ".gitkeep":
                continue
            filepath = os.path.join(yt_dir, filename)
            try:
                if filename.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            all_records.append(normalize_to_schema({
                                "id": item.get("comment_id", item.get("id", f"yt_fallback_{idx}")),
                                "source": "YouTube",
                                "platform": "YouTube",
                                "date": item.get("date", item.get("published_at")),
                                "author": item.get("author", item.get("channel")),
                                "title": item.get("video_title", item.get("title")),
                                "text": item.get("comment_text", item.get("text", "")),
                                "url": item.get("url", item.get("video_url")),
                                "product_id": item.get("video_id"),
                                "engagement": item.get("likes", item.get("like_count"))
                            }))
                elif filename.endswith((".csv", ".xlsx")):
                    df = pd.read_excel(filepath) if filename.endswith(".xlsx") else pd.read_csv(filepath)
                    for idx, row in df.iterrows():
                        all_records.append(normalize_to_schema({
                            "id": str(row.get("comment_id", row.get("id", f"yt_fallback_{idx}"))),
                            "source": "YouTube",
                            "platform": "YouTube",
                            "date": row.get("date", row.get("published_at")),
                            "author": row.get("author", row.get("channel")),
                            "title": row.get("video_title", row.get("title")),
                            "text": row.get("comment_text", row.get("text", "")),
                            "url": row.get("url", row.get("video_url")),
                            "product_id": row.get("video_id"),
                            "engagement": row.get("likes", row.get("like_count"))
                        }))
            except Exception as e:
                print(f"Error parsing YouTube file {filename}: {e}")

    # 5. Myntra Reviews
    myntra_dir = os.path.join(raw_dir, "myntra")
    if os.path.exists(myntra_dir):
        for filename in os.listdir(myntra_dir):
            if filename.startswith(".") or filename == ".gitkeep":
                continue
            filepath = os.path.join(myntra_dir, filename)
            try:
                if filename.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            all_records.append(normalize_to_schema({
                                "id": item.get("id", item.get("review_id", f"myntra_fallback_{idx}")),
                                "source": "Myntra",
                                "platform": "Myntra",
                                "date": item.get("date"),
                                "author": item.get("author"),
                                "title": item.get("title", item.get("review_title")),
                                "text": item.get("text", item.get("review_text", "")),
                                "rating": item.get("rating", item.get("score")),
                                "url": item.get("url"),
                                "product": item.get("product", item.get("product_name")),
                                "product_id": item.get("product_id"),
                                "category": item.get("category"),
                                "brand": item.get("brand"),
                                "engagement": item.get("helpful", item.get("engagement"))
                            }))
                elif filename.endswith((".csv", ".xlsx")):
                    df = pd.read_excel(filepath) if filename.endswith(".xlsx") else pd.read_csv(filepath)
                    for idx, row in df.iterrows():
                        all_records.append(normalize_to_schema({
                            "id": str(row.get("id", row.get("review_id", f"myntra_fallback_{idx}"))),
                            "source": "Myntra",
                            "platform": "Myntra",
                            "date": row.get("date"),
                            "author": row.get("author"),
                            "title": row.get("title", row.get("review_title")),
                            "text": row.get("text", row.get("review_text", "")),
                            "rating": row.get("rating", row.get("score")),
                            "url": row.get("url"),
                            "product": row.get("product", row.get("product_name")),
                            "product_id": row.get("product_id"),
                            "category": row.get("category"),
                            "brand": row.get("brand"),
                            "engagement": row.get("helpful", row.get("engagement"))
                        }))
            except Exception as e:
                print(f"Error parsing Myntra file {filename}: {e}")

    # 6. Fashion Communities
    comm_dir = os.path.join(raw_dir, "fashion_communities")
    if os.path.exists(comm_dir):
        for filename in os.listdir(comm_dir):
            if filename.startswith(".") or filename == ".gitkeep":
                continue
            filepath = os.path.join(comm_dir, filename)
            try:
                if filename.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            all_records.append(normalize_to_schema({
                                "id": item.get("id", f"fc_fallback_{idx}"),
                                "source": "Fashion Community",
                                "platform": "Fashion Community",
                                "date": item.get("date"),
                                "author": item.get("author"),
                                "title": item.get("title"),
                                "text": item.get("text", item.get("body", "")),
                                "url": item.get("url"),
                                "category": item.get("category", item.get("community")),
                                "engagement": item.get("engagement", item.get("likes"))
                            }))
                elif filename.endswith((".csv", ".xlsx")):
                    df = pd.read_excel(filepath) if filename.endswith(".xlsx") else pd.read_csv(filepath)
                    for idx, row in df.iterrows():
                        all_records.append(normalize_to_schema({
                            "id": str(row.get("id", f"fc_fallback_{idx}")),
                            "source": "Fashion Community",
                            "platform": "Fashion Community",
                            "date": row.get("date"),
                            "author": row.get("author"),
                            "title": row.get("title"),
                            "text": row.get("text", row.get("body", "")),
                            "url": row.get("url"),
                            "category": row.get("category", row.get("community")),
                            "engagement": row.get("engagement", row.get("likes"))
                        }))
            except Exception as e:
                print(f"Error parsing Fashion Community file {filename}: {e}")

    # 7. Social Media
    social_dir = os.path.join(raw_dir, "social_media")
    if os.path.exists(social_dir):
        for filename in os.listdir(social_dir):
            if filename.startswith(".") or filename == ".gitkeep":
                continue
            filepath = os.path.join(social_dir, filename)
            try:
                if filename.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data):
                            all_records.append(normalize_to_schema({
                                "id": item.get("id", item.get("post_id", f"sm_fallback_{idx}")),
                                "source": "Social Media",
                                "platform": "Social Media",
                                "date": item.get("date", item.get("created_at")),
                                "author": item.get("author", item.get("user")),
                                "text": item.get("text", item.get("post", "")),
                                "url": item.get("url"),
                                "engagement": item.get("engagement", item.get("likes"))
                            }))
                elif filename.endswith((".csv", ".xlsx")):
                    df = pd.read_excel(filepath) if filename.endswith(".xlsx") else pd.read_csv(filepath)
                    for idx, row in df.iterrows():
                        all_records.append(normalize_to_schema({
                            "id": str(row.get("id", row.get("post_id", f"sm_fallback_{idx}"))),
                            "source": "Social Media",
                            "platform": "Social Media",
                            "date": row.get("date", row.get("created_at")),
                            "author": row.get("author", row.get("user")),
                            "text": row.get("text", row.get("post", "")),
                            "url": row.get("url"),
                            "engagement": row.get("engagement", row.get("likes"))
                        }))
            except Exception as e:
                print(f"Error parsing Social Media file {filename}: {e}")

    # 8. Google Forms
    forms_dir = os.path.join(raw_dir, "google_forms")
    if os.path.exists(forms_dir):
        for filename in os.listdir(forms_dir):
            if filename.startswith(".") or filename == ".gitkeep":
                continue
            filepath = os.path.join(forms_dir, filename)
            try:
                if filename.endswith(".csv"):
                    df = pd.read_csv(filepath)
                    # Check if it is the specific Google Forms format
                    if "Timestamp" in df.columns and "What is the biggest barrier that prevents you from purchasing wishlisted items?" in df.columns:
                        for idx, row in df.iterrows():
                            text_parts = []
                            reason = row.get("What is your main reason for adding items to your Myntra wishlist?")
                            barrier = row.get("What is the biggest barrier that prevents you from purchasing wishlisted items?")
                            feedback = row.get("Any other feedback?")
                            
                            if pd.notna(reason):
                                text_parts.append(f"Wishlist Reason: {reason}")
                            if pd.notna(barrier):
                                text_parts.append(f"Purchase Barrier: {barrier}")
                            if pd.notna(feedback) and str(feedback).strip() != "":
                                text_parts.append(f"Other Feedback: {feedback}")
                            
                            full_text = " | ".join(text_parts) if text_parts else ""
                            
                            all_records.append(normalize_to_schema({
                                "id": f"forms_{idx}",
                                "source": "Google Forms",
                                "platform": "Google Forms",
                                "date": row.get("Timestamp"),
                                "author": row.get("Participant Name"),
                                "text": full_text,
                                "category": row.get("Which product category do you wishlist the most?") if pd.notna(row.get("Which product category do you wishlist the most?")) else None,
                                "url": None
                            }))
                    else:
                        # Generic Forms CSV
                        for idx, row in df.iterrows():
                            all_records.append(normalize_to_schema({
                                "id": str(row.get("id", f"forms_{idx}")),
                                "source": "Google Forms",
                                "platform": "Google Forms",
                                "date": row.get("date", row.get("Timestamp")),
                                "author": row.get("author", row.get("Participant Name")),
                                "text": row.get("text", ""),
                                "url": row.get("url")
                            }))
            except Exception as e:
                print(f"Error parsing Google Forms file {filename}: {e}")

    # Build master DataFrame
    if all_records:
        master_df = pd.DataFrame(all_records)
    else:
        master_df = pd.DataFrame(columns=CANONICAL_COLUMNS)
    
    # Fill remaining columns to guarantee 15 schema columns
    for col in CANONICAL_COLUMNS:
        if col not in master_df.columns:
            master_df[col] = None
            
    master_df = master_df[CANONICAL_COLUMNS]
    
    # Save master raw dataset in required folders
    os.makedirs("data/processed/standardized", exist_ok=True)
    master_df.to_csv("data/raw_master_dataset.csv", index=False)
    master_df.to_csv("data/processed/standardized/raw_master_dataset.csv", index=False)
    
    return master_df

if __name__ == "__main__":
    df = ingest_raw_data()
    print(f"Ingested {len(df)} records.")
    print(df.head())
