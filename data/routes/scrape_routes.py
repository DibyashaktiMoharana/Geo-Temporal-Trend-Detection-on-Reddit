from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from controllers.reddit_controller import RedditController
import uvicorn

# Create router
router = APIRouter(prefix="/api", tags=["reddit-scraper"])

# Initialize controller
reddit_controller = RedditController()

@router.get("/scrape")
async def scrape_reddit_posts(
    subreddit: str = Query(..., description="Name of the subreddit to scrape"),
    method: str = Query("hot", description="Listing method: hot, new, top, rising"),
    time_filter: str = Query("month", description="Time filter: day, week, month, year, all")
):
    """
    Scrape Reddit posts using various listing methods
    
    - **subreddit**: Name of the subreddit to scrape
    - **method**: Listing method (hot, new, top, rising)
    - **time_filter**: Time filter (only works with 'top' method: day, week, month, year, all)
    
    Note: For 'hot', 'new', and 'rising' methods, all posts from the last 6 months are fetched.
    """
    try:
        result = await reddit_controller.scrape_posts(
            subreddit_name=subreddit,
            listing_method=method,
            time_filter=time_filter
        )
        
        if result["success"]:
            return {
                "status": "success",
                "message": result["message"],
                "data": result["data"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Reddit Scraper API is running"
    }

# @router.delete("/debug/collection/{collection_name}")
# async def clear_collection(collection_name: str):
#     """Debug endpoint to clear a specific collection"""
#     try:
#         from database.connectdb import get_collection
        
#         collection = get_collection(collection_name)
        
#         # Clear all documents
#         result = collection.delete_many({})
        
#         return {
#             "status": "success",
#             "message": f"Cleared {result.deleted_count} documents from {collection_name}",
#             "data": {
#                 "collection_name": collection_name,
#                 "deleted_count": result.deleted_count
#             }
#         }
        
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"Error clearing collection {collection_name}: {str(e)}"
#         }
