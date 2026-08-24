import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def scrape_reddit(subreddits=["IndianFashionAddicts", "shopping"], keywords=["myntra", "wishlist", "fit", "size"], limit=50, output_path="data/raw/reddit/reddit_comments.json"):
    """
    Searches specified subreddits for Myntra wishlist/shopping discussions using PRAW.
    Exits gracefully if API credentials are not configured.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "myntra-discovery-engine-v1")
    
    if not client_id or not client_secret:
        print("Reddit API credentials (REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET) not found in environment.")
        print("Skipping live Reddit scraper (no live comments gathered).")
        return []
        
    try:
        import praw
        
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        print(f"Initializing Reddit scraper. Querying subreddits: {subreddits} for keywords: {keywords}...")
        
        comments_dataset = []
        
        for sub_name in subreddits:
            subreddit = reddit.subreddit(sub_name)
            
            for keyword in keywords:
                print(f"Searching r/{sub_name} for '{keyword}'...")
                # Search submissions
                submissions = subreddit.search(keyword, limit=limit)
                
                for submission in submissions:
                    # Include the submission selftext if relevant
                    if submission.selftext and "myntra" in submission.selftext.lower():
                        comments_dataset.append({
                            "id": f"t3_{submission.id}",
                            "author": str(submission.author),
                            "body": submission.selftext,
                            "score": submission.score,
                            "created_utc": submission.created_utc,
                            "subreddit": sub_name,
                            "permalink": submission.permalink
                        })
                    
                    # Fetch hot comments
                    submission.comments.replace_more(limit=0) # Only top-level comments
                    for comment in submission.comments.list()[:20]:
                        if any(k in comment.body.lower() for k in ["myntra", "wishlist", "buy", "purchase", "save"]):
                            comments_dataset.append({
                                "id": f"t1_{comment.id}",
                                "author": str(comment.author),
                                "body": comment.body,
                                "score": comment.score,
                                "created_utc": comment.created_utc,
                                "subreddit": sub_name,
                                "permalink": comment.permalink
                            })
                            
        # Deduplicate comments by id
        unique_comments = {c["id"]: c for c in comments_dataset}.values()
        unique_comments_list = list(unique_comments)
        
        # Save raw results
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(unique_comments_list, f, indent=4, default=str)
            
        print(f"Reddit scraping completed successfully. Saved {len(unique_comments_list)} comments to {output_path}")
        return unique_comments_list
        
    except Exception as e:
        print(f"Failed to scrape Reddit: {e}")
        return []

if __name__ == "__main__":
    scrape_reddit()
