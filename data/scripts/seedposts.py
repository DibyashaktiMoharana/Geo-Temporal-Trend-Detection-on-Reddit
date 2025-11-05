import json
import os
from database.connectdb import get_collection_for_subreddit
from models.reddit_post import RedditPost

def seedposts(subreddit_name: str = "pune", method: str = "hot", clear_existing: bool = True):
    """
    Seed Reddit posts from JSON file to MongoDB
    """
    
    # Load JSON data
    json_filename = f"reddit_posts_{subreddit_name.lower()}_{method}.json"
    
    if not os.path.exists(json_filename):
        print(f"JSON file {json_filename} not found!")
        return
    
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
        
        print(f"Loaded {len(posts_data)} posts from {json_filename}")
        
        # Get collection using the refactored function
        collection = get_collection_for_subreddit(subreddit_name)
        collection_name = f"{subreddit_name.lower()}Data"
        
        # Clear existing data if requested
        if clear_existing:
            delete_result = collection.delete_many({})
            print(f"Cleared {delete_result.deleted_count} existing posts from {collection_name}")
        
        # Convert to RedditPost objects and prepare for insertion
        reddit_posts = []
        errors = 0
        
        for post_data in posts_data:
            try:
                reddit_post = RedditPost.from_dict(post_data)
                reddit_posts.append(reddit_post.to_dict())
            except Exception as e:
                errors += 1
                print(f"Error processing post '{post_data.get('title', 'Unknown')[:50]}...': {e}")
                continue
        
        # Insert posts into MongoDB
        if reddit_posts:
            result = collection.insert_many(reddit_posts)
            print(f"Successfully seeded {len(result.inserted_ids)} posts to {collection_name}")
            
            if errors > 0:
                print(f"Skipped {errors} posts due to errors")
            
            # Delete the temporary JSON file after successful insertion
            try:
                os.remove(json_filename)
                print(f"Deleted temporary file: {json_filename}")
            except Exception as delete_error:
                print(f"Warning: Could not delete temporary file {json_filename}: {delete_error}")
        else:
            print(f"No valid posts to seed (errors: {errors})")
            
        return {
            "success": True,
            "posts_inserted": len(reddit_posts),
            "errors": errors,
            "collection": collection_name
        }
            
    except Exception as e:
        print(f"Error seeding posts: {e}")
        raise
