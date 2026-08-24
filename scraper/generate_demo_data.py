import os
import json
import csv

def generate_demo_data():
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(os.path.join(raw_dir, "google_play"), exist_ok=True)
    os.makedirs(os.path.join(raw_dir, "app_store"), exist_ok=True)
    os.makedirs(os.path.join(raw_dir, "reddit"), exist_ok=True)
    os.makedirs(os.path.join(raw_dir, "google_forms"), exist_ok=True)
    
    # 1. Play Store Reviews (JSON)
    play_store_reviews = [
        {
            "reviewId": "gp_01",
            "userName": "Rahul Sharma",
            "content": "The app is good but I have 15 items in my wishlist and I cannot decide which one to buy. I wish there was a tool to compare the fabrics and fit side by side. It's so confusing.",
            "score": 4,
            "thumbsUpCount": 12,
            "reviewCreatedVersion": "4.21.0",
            "at": "2026-08-10 12:00:00",
            "replyContent": None,
            "repliedAt": None
        },
        {
            "reviewId": "gp_02",
            "userName": "Priya Patel",
            "content": "I wishlisted a beautiful lehenga for my friend's wedding next month. But I am hesitant to buy because the size chart is very confusing. Some reviews say buy one size larger, others say true to size. I don't want to go through the hassle of returning it.",
            "score": 3,
            "thumbsUpCount": 4,
            "reviewCreatedVersion": "4.21.1",
            "at": "2026-08-11 14:30:00",
            "replyContent": None,
            "repliedAt": None
        },
        {
            "reviewId": "gp_03",
            "userName": "Amit Verma",
            "content": "Payment failed three times today while trying to buy shoes from my wishlist. Useless app, please fix UPI payment gateway!",
            "score": 1,
            "thumbsUpCount": 2,
            "reviewCreatedVersion": "4.21.0",
            "at": "2026-08-12 09:15:00",
            "replyContent": "Sorry for the issue...",
            "repliedAt": "2026-08-12 10:00:00"
        },
        {
            "reviewId": "gp_04",
            "userName": "Sneha Reddy",
            "content": "I keep adding dresses to my wishlist to buy later. But when I actually go to buy them, half of them are out of stock in my size (S). Why can't you alert me when my wishlisted items are running low on stock?",
            "score": 3,
            "thumbsUpCount": 18,
            "reviewCreatedVersion": "4.21.2",
            "at": "2026-08-13 18:22:00",
            "replyContent": None,
            "repliedAt": None
        },
        {
            "reviewId": "gp_05",
            "userName": "Vikram Singh",
            "content": "Nice app, great fashion collection.",
            "score": 5,
            "thumbsUpCount": 1,
            "reviewCreatedVersion": "4.21.0",
            "at": "2026-08-14 11:00:00",
            "replyContent": None,
            "repliedAt": None
        },
        {
            "reviewId": "gp_06",
            "userName": "Ananya Sen",
            "content": "I have added a lot of office wear kurtis to my wishlist, but I am not sure about the material. It says 'polyester blend' but in some photos it looks very thin and cheap. I wish there was video feedback or clearer close-up fabric shots so I could trust the quality before spending my money.",
            "score": 3,
            "thumbsUpCount": 9,
            "reviewCreatedVersion": "4.21.2",
            "at": "2026-08-15 15:40:00",
            "replyContent": None,
            "repliedAt": None
        },
        {
            "reviewId": "gp_07",
            "userName": "Rohan Das",
            "content": "Delivery is extremely delayed! Ordered a t-shirt 8 days ago and it is still in transit. Customer service is not responding to calls. Terrible experience.",
            "score": 1,
            "thumbsUpCount": 5,
            "reviewCreatedVersion": "4.21.1",
            "at": "2026-08-16 10:30:00",
            "replyContent": None,
            "repliedAt": None
        },
        {
            "reviewId": "gp_08",
            "userName": "Meera Joshi",
            "content": "I love the wishlist feature. I add items I like so I don't lose them. But I wish there was a way to organize my wishlist into folders like 'Workwear', 'Casuals', 'Party'. Right now it's just a long unsorted list and I get overwhelmed trying to choose what to buy, so I end up buying nothing.",
            "score": 4,
            "thumbsUpCount": 22,
            "reviewCreatedVersion": "4.21.3",
            "at": "2026-08-17 21:05:00",
            "replyContent": None,
            "repliedAt": None
        }
    ]
    
    with open(os.path.join(raw_dir, "google_play/demo_play_store_reviews.json"), "w", encoding="utf-8") as f:
        json.dump(play_store_reviews, f, indent=4)
        
    # 2. App Store Reviews (JSON)
    app_store_reviews = [
        {
            "id": "as_01",
            "userName": "Fashionista_99",
            "title": "Uncertain about styling",
            "review": "I have a lot of items in my wishlist, mostly unique crop tops and skirts. However, I hesitate to purchase because I don't know how to style them or what they will look like together. I wish Myntra had a feature to mix-and-match wishlisted items to see if they make a good outfit.",
            "rating": 4,
            "date": "2026-08-11 10:00:00",
            "developerResponse": None
        },
        {
            "id": "as_02",
            "userName": "Karan_M",
            "title": "Need second opinions",
            "review": "Whenever I wishlist formal shirts, I want to get my friends' feedback before buying. But sharing wishlisted items is very clunky. It just sends individual links. I wish we could share a collaborative wishlist folder so they could vote on what looks best. So I keep them saved and forget to buy.",
            "rating": 3,
            "date": "2026-08-12 16:45:00",
            "developerResponse": None
        },
        {
            "id": "as_03",
            "userName": "Riya_Kapoor",
            "title": "Size fit is a major worry",
            "review": "Added a couple of jeans to my wishlist. But denim fit is so tricky. I am between sizes 28 and 30. Without a virtual fitting room or detailed reviews from people with my exact height and weight, I just don't feel confident buying. I ended up purchasing from a retail store instead where I could try them on.",
            "rating": 3,
            "date": "2026-08-13 13:20:00",
            "developerResponse": None
        },
        {
            "id": "as_04",
            "userName": "AppUser102",
            "title": "App crashes during checkout",
            "review": "The app crashed three times when I tried to pay for items in my cart. Please fix the iOS app crash issues. Very frustrating experience.",
            "rating": 2,
            "date": "2026-08-14 08:30:00",
            "developerResponse": None
        },
        {
            "id": "as_05",
            "userName": "Siddharth_G",
            "title": "Price is high but waiting for reviews",
            "review": "I wishlisted a premium leather jacket. It is quite expensive, so I want to be 100% sure about the quality. But there are no user reviews or photos on the product page. I'm not going to buy an expensive item blindly. Still waiting in my wishlist for someone to review it.",
            "rating": 3,
            "date": "2026-08-15 19:10:00",
            "developerResponse": None
        }
    ]
    
    with open(os.path.join(raw_dir, "app_store/demo_app_store_reviews.json"), "w", encoding="utf-8") as f:
        json.dump(app_store_reviews, f, indent=4)

    # 3. Reddit Comments (JSON)
    reddit_comments = [
        {
            "id": "t1_rd01",
            "author": "StyleEnthusiast",
            "body": "Honestly, my Myntra wishlist is just an aspirational board. I add stuff I like but will never buy because they are too expensive or don't fit my daily casual lifestyle. I wish there was a filter to separate my 'aspirational' wishlist from things I actually intend to buy for upcoming occasions.",
            "score": 45,
            "created_utc": 1786536000.0,  # Aug 10 2026
            "subreddit": "IndianFashionAddicts",
            "permalink": "/r/IndianFashionAddicts/comments/xyz/comment/rd01/"
        },
        {
            "id": "t1_rd02",
            "author": "Curious_Shopper",
            "body": "Does anyone else wishlist shoes on Myntra and then search for real-life reviews on YouTube before buying? I do this because the product photos on the app are highly edited and studio-lit. I want to see how the sneakers look in natural daylight. If I don't find a video, I just leave them in my wishlist forever.",
            "score": 12,
            "created_utc": 1786622400.0,  # Aug 11 2026
            "subreddit": "IndianFashionAddicts",
            "permalink": "/r/IndianFashionAddicts/comments/xyz/comment/rd02/"
        },
        {
            "id": "t1_rd03",
            "author": "Puzzled_User",
            "body": "I have about 8 kurtas in my wishlist for an upcoming family pooja. I want to buy just one, but comparing them is such a headache. I have to open 8 different tabs, check their fabrics, length, reviews, and delivery dates. I got so overwhelmed by the comparison process that I closed the app and didn't buy anything.",
            "score": 28,
            "created_utc": 1786708800.0,  # Aug 12 2026
            "subreddit": "shopping",
            "permalink": "/r/shopping/comments/abc/comment/rd03/"
        },
        {
            "id": "t1_rd04",
            "author": "BargainHunter",
            "body": "Myntra customer support is terrible. I returned a defective shirt and they are refusing to refund my money, saying the tag was missing. I will never buy from them again. Deleting my wishlist.",
            "score": -2,
            "created_utc": 1786795200.0,  # Aug 13 2026
            "subreddit": "shopping",
            "permalink": "/r/shopping/comments/abc/comment/rd04/"
        },
        {
            "id": "t1_rd05",
            "author": "FitSeeker",
            "body": "I wishlisted a blazer on Myntra. I'm hesitant to order because blazer tailoring is very sensitive. If the shoulders are loose or sleeves are long, it looks bad. I wish Myntra had a virtual body model where I could enter my chest, shoulder, and height measurements to see a 3D fit visualization. That would make me checkout immediately.",
            "score": 67,
            "created_utc": 1786881600.0,  # Aug 14 2026
            "subreddit": "IndianFashionAddicts",
            "permalink": "/r/IndianFashionAddicts/comments/lmn/comment/rd05/"
        }
    ]
    
    with open(os.path.join(raw_dir, "reddit/demo_reddit_comments.json"), "w", encoding="utf-8") as f:
        json.dump(reddit_comments, f, indent=4)

    # 4. Google Forms / Primary Research (CSV)
    google_forms_data = [
        ["Timestamp", "Email Address", "Participant Name", "What is your main reason for adding items to your Myntra wishlist?", "What is the biggest barrier that prevents you from purchasing wishlisted items?", "Which product category do you wishlist the most?", "Would you buy wishlisted items faster if you could see how they look on someone with your body type?", "Any other feedback?"],
        ["2026-08-11 11:15:30", "user1@gmail.com", "Aditya Gupta", "To save items I like for future planning", "Unsure of how the shirt will fit me since sizes vary across brands. Myntra's sizing tool is not reliable enough.", "Clothing", "Yes, definitely", "I wish there were more reviews with customer photos showing the actual color in daylight."],
        ["2026-08-11 12:20:00", "user2@gmail.com", "Meghna Roy", "To track items for weddings/festivals", "I get overwhelmed by having too many similar choices in my wishlist (e.g., 5 red sarees). I don't know how to compare them easily.", "Clothing", "Yes", "Sharing wishlist with my sister is hard. She has to tell me which saree looks best."],
        ["2026-08-12 15:40:12", "user3@gmail.com", "Kunal Shah", "To save shoes I want to buy", "I am worried about the quality. Sometimes the leather looks shiny in pictures but turns out to be plastic. I need real user reviews.", "Footwear", "Maybe", "Delivery charges are high for cheap items."],
        ["2026-08-12 17:10:05", "user4@gmail.com", "Divya Nair", "Just casual browsing and bookmarking", "No real reason, I just add them as a bookmark and forget. I don't really have immediate purchase intent.", "Accessories", "No", "A gentle reminder that my wishlisted item is low on stock might make me purchase, but usually I just bookmark and move on."],
        ["2026-08-13 10:05:45", "user5@gmail.com", "Rohan Mehta", "To buy later when I have money", "I wishlist expensive jackets. I want to buy them but they are out of my budget right now. I will buy only when the price drops.", "Clothing", "Yes", "The full price is too high."]
    ]
    
    with open(os.path.join(raw_dir, "google_forms/demo_google_forms.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(google_forms_data)

    print("Demo datasets generated successfully in data/raw/")

if __name__ == "__main__":
    generate_demo_data()
