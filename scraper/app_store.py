import os
import json
import requests
from app_store_scraper import AppStore

def scrape_app_store_rss(app_id=907394059, count=100):
    """
    Scrapes reviews directly from Apple's iTunes Customer Reviews JSON RSS feed.
    This is highly reliable and bypasses external scraping library limitations.
    """
    reviews_list = []
    # Fetch top 100 reviews (5 pages of 20 reviews each or single page)
    # The iTunes RSS feed allows up to page 10 (200 reviews)
    max_pages = min(5, (count // 20) + 1)
    
    print(f"Attempting to scrape App Store via JSON RSS feed for app ID: {app_id}...")
    
    for page in range(1, max_pages + 1):
        url = f"https://itunes.apple.com/in/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                break
                
            data = response.json()
            feed = data.get("feed", {})
            entries = feed.get("entry", [])
            
            if not entries:
                break
                
            # If entry is a single dictionary (occurs when there's only 1 review)
            if isinstance(entries, dict):
                entries = [entries]
                
            for entry in entries:
                # The first entry in the feed is often metadata about the app itself
                # Reviews contain 'im:rating'
                if "im:rating" not in entry:
                    continue
                    
                review_id = entry.get("id", {}).get("label")
                author = entry.get("author", {}).get("name", {}).get("label", "Anonymous")
                title = entry.get("title", {}).get("label", "")
                review_text = entry.get("content", {}).get("label", "")
                rating = int(entry.get("im:rating", {}).get("label", 0))
                
                # Apple RSS feeds do not provide an explicit date field inside standard json entries,
                # but we can map the title/content metadata or insert current time as date
                from datetime import datetime
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                reviews_list.append({
                    "id": review_id,
                    "userName": author,
                    "title": title,
                    "review": review_text,
                    "rating": rating,
                    "date": date_str,
                    "developerResponse": None
                })
                
            if len(reviews_list) >= count:
                reviews_list = reviews_list[:count]
                break
                
        except Exception as e:
            print(f"Error reading RSS feed page {page}: {e}")
            break
            
    return reviews_list

def scrape_app_store(app_name="myntra-fashion-shopping-app", app_id=907394059, count=100, output_path="data/raw/app_store/app_store_reviews.json"):
    """
    Main controller for iOS scraping. Tries RSS feed first, falls back to AppStore library.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1. Try RSS feed (Reliable JSON parser)
    result = scrape_app_store_rss(app_id=app_id, count=count)
    
    # 2. Fall back to standard app-store-scraper library if RSS is empty
    if not result:
        print("RSS feed returned 0 reviews. Falling back to AppStore library scraper...")
        try:
            app_scraper = AppStore(country="in", app_name=app_name, app_id=app_id)
            app_scraper.review(how_many=count)
            result = app_scraper.reviews
        except Exception as e:
            print(f"Fallback AppStore library scraper failed: {e}")
            
    # Save raw results
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, default=str)
        print(f"iOS App Store scraping completed. Saved {len(result)} reviews to {output_path}")
    except Exception as e:
        print(f"Failed to write App Store file: {e}")
        
    return result

if __name__ == "__main__":
    scrape_app_store()
