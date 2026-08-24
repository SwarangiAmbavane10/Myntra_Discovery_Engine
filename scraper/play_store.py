import os
import json
from google_play_scraper import Sort, reviews

def scrape_play_store(app_id="com.myntra.android", count=100, output_path="data/raw/google_play/play_store_reviews.json"):
    """
    Scrapes reviews for com.myntra.android from the Google Play Store.
    Saves raw reviews to output_path.
    """
    print(f"Scraping {count} reviews from Play Store for app ID: {app_id}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        result, _ = reviews(
            app_id,
            lang='en',
            country='in',
            sort=Sort.NEWEST,
            count=count
        )
        
        # Save raw results
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, default=str)
            
        print(f"Play Store scraping successful. Saved {len(result)} reviews to {output_path}")
        return result
        
    except Exception as e:
        print(f"Failed to scrape Google Play Store: {e}")
        return []

if __name__ == "__main__":
    scrape_play_store()
