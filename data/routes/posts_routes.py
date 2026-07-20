from fastapi import APIRouter, HTTPException, Query
from database.connectdb import (
    get_collection_for_subreddit, 
    get_all_subreddit_collections,
    get_collection
)
from typing import Optional
from datetime import datetime

# Create router
router = APIRouter(prefix="/api/posts", tags=["posts"])

def _format_post(post: dict) -> dict:
    """Format a single post for JSON response"""
    # Convert ObjectId to string for JSON serialization
    post["_id"] = str(post["_id"])
    
    # Format datetime objects to ISO format strings
    if "created_at" in post and isinstance(post["created_at"], datetime):
        post["created_at"] = post["created_at"].isoformat()
    
    return post

@router.get("/")
async def get_posts(
    subreddit: Optional[str] = Query(None, description="Filter by subreddit name (e.g., 'delhi', 'pune')"),
    limit: int = Query(100, description="Number of posts to fetch per collection", ge=1, le=1000),
    skip: int = Query(0, description="Number of posts to skip (for pagination)", ge=0)
):
    """
    Fetch posts from MongoDB sorted by creation date (newest first)
    
    - **subreddit**: Optional filter to get posts from a specific subreddit (e.g., 'delhi', 'pune', 'mumbai')
    - **limit**: Number of posts to return per collection (default: 100, max: 1000)
    - **skip**: Number of posts to skip for pagination (default: 0)
    
    If no subreddit is specified, fetches from all available subreddit collections.
    """
    try:
        all_posts = []
        total_count = 0
        collections_queried = []
        
        if subreddit:
            # Query specific subreddit collection
            collection = get_collection_for_subreddit(subreddit)
            collections_queried.append(f"{subreddit.lower()}Data")
            
            posts_cursor = collection.find({}).sort("created_at", -1).skip(skip).limit(limit)
            all_posts = [_format_post(post) for post in posts_cursor]
            total_count = collection.count_documents({})
        else:
            # Query all subreddit collections
            collection_names = get_all_subreddit_collections()
            collections_queried = collection_names
            
            for collection_name in collection_names:
                collection = get_collection(collection_name)
                posts_cursor = collection.find({}).sort("created_at", -1).limit(limit)
                
                for post in posts_cursor:
                    all_posts.append(_format_post(post))
                
                total_count += collection.count_documents({})
            
            # Sort all posts by created_at (newest first)
            all_posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Apply pagination after combining
            all_posts = all_posts[skip:skip + limit]
        
        return {
            "status": "success",
            "data": {
                "posts": all_posts,
                "count": len(all_posts),
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": (skip + len(all_posts)) < total_count,
                "collections_queried": collections_queried
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")


@router.get("/subreddits")
async def get_subreddits():
    """
    Get a list of all subreddits that have posts in the database
    
    Returns a list of unique subreddit names with their post counts.
    Reads from all collections ending with 'Data'.
    """
    try:
        collection_names = get_all_subreddit_collections()
        subreddits_info = []
        
        for collection_name in collection_names:
            collection = get_collection(collection_name)
            post_count = collection.count_documents({})
            
            # Extract subreddit name from collection name (e.g., 'delhiData' -> 'delhi')
            subreddit_name = collection_name.replace("Data", "").lower()
            
            # Get oldest and newest post dates
            oldest_post = collection.find_one({}, sort=[("created_at", 1)])
            newest_post = collection.find_one({}, sort=[("created_at", -1)])
            
            subreddits_info.append({
                "subreddit": subreddit_name,
                "collection_name": collection_name,
                "post_count": post_count,
                "oldest_post_date": oldest_post["created_at"].isoformat() if oldest_post and "created_at" in oldest_post else None,
                "newest_post_date": newest_post["created_at"].isoformat() if newest_post and "created_at" in newest_post else None
            })
        
        # Sort by post count (descending)
        subreddits_info.sort(key=lambda x: x["post_count"], reverse=True)
        
        return {
            "status": "success",
            "data": {
                "subreddits": subreddits_info,
                "total_subreddits": len(subreddits_info),
                "total_posts": sum(s["post_count"] for s in subreddits_info)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subreddits: {str(e)}")

