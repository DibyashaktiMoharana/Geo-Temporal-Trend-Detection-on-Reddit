import json
import os
# from connectdb import get_collection
from database.connectdb import get_collection
from models.reddit_post import RedditPost

def seedposts(subreddit_name: str = "pune", method: str = "hot"):
    """Seed Reddit posts from JSON file to MongoDB"""
    
    # Load JSON data using new format
    json_filename = f"reddit_posts_{subreddit_name.lower()}_{method}.json"
    
    if not os.path.exists(json_filename):
        print(f"JSON file {json_filename} not found!")
        return
    
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
        
        # Get collection - will create if doesn't exist
        collection_name = f"{subreddit_name.lower()}Data"
        collection = get_collection(collection_name)
        
        # Clear all existing data in the collection
        collection.delete_many({})
        print(f"Cleared all existing data from {collection_name}")
        
        # Convert to RedditPost objects and insert
        reddit_posts = []
        for post_data in posts_data:
            try:
                reddit_post = RedditPost.from_dict(post_data)
                reddit_posts.append(reddit_post.to_dict())
            except Exception as e:
                print(f"Error processing post '{post_data.get('title', 'Unknown')}': {e}")
                continue
        
        if reddit_posts:
            result = collection.insert_many(reddit_posts)
            print(f"Successfully seeded {len(result.inserted_ids)} posts to {collection_name}")
            
            # Delete the temporary JSON file after successful MongoDB insertion
            try:
                os.remove(json_filename)
                print(f"Deleted temporary file: {json_filename}")
            except Exception as delete_error:
                print(f"Warning: Could not delete temporary file {json_filename}: {delete_error}")
        else:
            print("No valid posts to seed")
            
    except Exception as e:
        print(f"Error seeding posts: {e}")
        raise
