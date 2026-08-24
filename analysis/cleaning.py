# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
import re

def clean_text_field(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    # 1. Strip HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # 2. Normalize whitespace
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    # 3. Normalize tracking URLs to [URL]
    text = re.sub(r'https?://(?:www\.)?\S+', '[URL]', text)
    return text

def is_spam(text):
    """
    Identifies bot-like comments, advertisements, affiliate links, or promotional spam.
    Does NOT flag negative customer feedback.
    """
    text_lower = text.lower()
    spam_patterns = [
        r"discount code", r"promo code", r"use my code", r"click here to buy",
        r"subscribe to my", r"visit my website", r"follow me on", r"whatsapp group",
        r"telegram link", r"telegram channel", r"make money online", r"earn money",
        r"affiliate link", r"join now", r"dm me for", r"promotions", r"promotional code",
        r"advertisement", r"free gift card"
    ]
    for pattern in spam_patterns:
        if re.search(pattern, text_lower):
            return True
            
    # Check for meaningless repeated characters (e.g., "aaaaa...")
    if re.search(r'(.)\1{9,}', text_lower):
        return True
        
    return False

def detect_language(text):
    """
    Simple heuristic language detection: en (English), hinglish (Hinglish), other.
    """
    text_lower = text.lower()
    # Typical Hinglish keywords
    hinglish_words = [
        "hai", "bhai", "acha", "achha", "aur", "hota", "nahi", "nahin", "par",
        "hoga", "tha", "ye", "wo", "toh", "krna", "karna", "likha", "mil", "mila",
        "kuch", "kuchh", "bahut", "bohot", "sasta", "mehenga", "mahanga", "kharida",
        "lekin", "hi", "he", "sahi", "yaar", "kya", "ispe", "uspe", "kaise", "kab"
    ]
    words = text_lower.split()
    if not words:
        return "en"
        
    hinglish_count = sum(1 for w in words if w in hinglish_words)
    # If a significant number of words match Hinglish dictionary list, classify as hinglish
    if hinglish_count >= 1 or (hinglish_count / len(words)) > 0.05:
        return "hinglish"
        
    # Check if text contains non-ASCII characters primarily
    non_ascii_count = sum(1 for c in text if ord(c) > 127)
    if non_ascii_count / len(text) > 0.15 if len(text) > 0 else False:
        return "other"
        
    return "en"

def clean_data(raw_df, output_path="data/clean_master_dataset.csv"):
    """
    Cleans, deduplicates, filters spam, detects language, and normalizes raw Master dataset.
    """
    original_records = len(raw_df)
    print(f"Starting data cleaning pipeline for {original_records} records...")
    
    # Ensure directories
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs("data/processed/cleaned", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)
    
    # 1. Standardize and clean text fields
    df = raw_df.copy()
    df["text"] = df["text"].apply(clean_text_field)
    
    # Remove records with empty text
    df = df[df["text"].str.strip() != ""]
    invalid_removed = original_records - len(df)
    
    # 2. Heuristic Language Detection
    df["language"] = df["text"].apply(detect_language)
    
    # 3. Spam Detection & Filtering
    df["is_spam"] = df["text"].apply(is_spam)
    spam_df = df[df["is_spam"] == True]
    df = df[df["is_spam"] == False].drop(columns=["is_spam"])
    spam_removed = len(spam_df)
    
    # 4. Source-Specific Duplicate Tracking
    # We track: original_count, duplicate_count, clean_count for each source
    source_stats = {}
    sources = df["source"].unique()
    
    cleaned_records_list = []
    
    for src in sources:
        src_df = df[df["source"] == src].copy()
        raw_src_count = len(raw_df[raw_df["source"] == src])
        
        # Deduplication criteria:
        # We drop duplicate texts, duplicate non-fallback IDs, and duplicate URLs
        # a) Deduplicate text
        src_df["text_lower"] = src_df["text"].str.lower().str.strip()
        dedup_text = src_df.drop_duplicates(subset=["text_lower"], keep="first")
        
        # b) Deduplicate IDs (where ID is not standard fallback representation)
        def is_not_fallback(id_str):
            if not id_str:
                return False
            for fallback in ["fallback", "gp_fallback", "as_fallback", "reddit_fallback", "yt_fallback", "myntra_fallback", "fc_fallback", "sm_fallback", "forms_fallback"]:
                if fallback in str(id_str):
                    return False
            return True
        
        dedup_id = dedup_text.copy()
        if "id" in dedup_id.columns:
            non_fallback_mask = dedup_id["id"].apply(is_not_fallback)
            fallback_df = dedup_id[~non_fallback_mask]
            non_fallback_df = dedup_id[non_fallback_mask]
            
            non_fallback_dedup = non_fallback_df.drop_duplicates(subset=["id"], keep="first")
            dedup_id = pd.concat([non_fallback_dedup, fallback_df], ignore_index=True)
            
        # c) Deduplicate URLs (where URL is not null/empty)
        dedup_url = dedup_id.copy()
        if "url" in dedup_url.columns:
            url_mask = dedup_url["url"].notna() & (dedup_url["url"] != "") & (dedup_url["url"] != "[URL]")
            no_url_df = dedup_url[~url_mask]
            url_df = dedup_url[url_mask]
            
            url_dedup = url_df.drop_duplicates(subset=["url"], keep="first")
            dedup_url = pd.concat([url_dedup, no_url_df], ignore_index=True)
            
        # Drop temporary lowercase text helper column
        if "text_lower" in dedup_url.columns:
            dedup_url = dedup_url.drop(columns=["text_lower"])
            
        dedup_src_count = len(dedup_url)
        duplicates_removed_src = raw_src_count - invalid_removed - spam_removed - dedup_src_count # estimated
        # Clamp to 0
        if duplicates_removed_src < 0:
            duplicates_removed_src = 0
            
        source_stats[src] = {
            "original_count": int(raw_src_count),
            "duplicate_count": int(raw_src_count - dedup_src_count),
            "clean_count": int(dedup_src_count)
        }
        
        cleaned_records_list.append(dedup_url)
        
    if cleaned_records_list:
        clean_df = pd.concat(cleaned_records_list, ignore_index=True)
    else:
        clean_df = pd.DataFrame(columns=raw_df.columns)
        
    # Save Master clean dataset in required folders
    clean_df.to_csv("data/clean_master_dataset.csv", index=False)
    clean_df.to_csv("data/processed/cleaned/clean_master_dataset.csv", index=False)
    
    # Save standard clean reviews path as fallback for downstream code
    clean_df.to_csv("data/processed/clean_reviews.csv", index=False)
    
    # Compile cleaning report metadata
    report = {
        "raw_records": original_records,
        "valid_records": len(clean_df),
        "duplicates_removed": int(original_records - len(clean_df) - spam_removed - invalid_removed),
        "spam_removed": int(spam_removed),
        "invalid_removed": int(invalid_removed),
        "source_stats": source_stats
    }
    
    # Save JSON report
    with open("data/processed/cleaning_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print(f"Data cleaning complete. Total cleaned: {len(clean_df)}, Spam removed: {spam_removed}")
    return clean_df, report

if __name__ == "__main__":
    from ingestion import ingest_raw_data
    df = ingest_raw_data()
    clean_df, report = clean_data(df)
