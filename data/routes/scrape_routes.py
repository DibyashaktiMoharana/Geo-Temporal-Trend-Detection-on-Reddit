from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from controllers.reddit_controller import RedditController
import uvicorn

# Create router
router = APIRouter(prefix="/api/v1", tags=["reddit-scraper"])

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

@router.get("/methods")
async def get_listing_methods():
    """Get available listing methods and their descriptions"""
    return {
        "status": "success",
        "data": reddit_controller.get_available_listing_methods()
    }

@router.get("/time-filters")
async def get_time_filters():
    """Get available time filters for 'top' method"""
    return {
        "status": "success",
        "data": reddit_controller.get_available_time_filters()
    }

@router.get("/help")
async def get_help():
    """Get help information and usage examples"""
    listing_methods = reddit_controller.get_available_listing_methods()
    time_filters = reddit_controller.get_available_time_filters()
    
    help_data = {
        "listing_methods": listing_methods,
        "time_filters": time_filters,
        "examples": {
            "hot_posts_6months": "/api/v1/scrape?subreddit=Pune&method=hot&time_filter=month",
            "top_posts_week": "/api/v1/scrape?subreddit=Mumbai&method=top&time_filter=week",
            "new_posts_6months": "/api/v1/scrape?subreddit=Delhi&method=new&time_filter=month",
            "rising_posts_6months": "/api/v1/scrape?subreddit=Bangalore&method=rising&time_filter=month",
            "top_posts_all_time": "/api/v1/scrape?subreddit=Pune&method=top&time_filter=all"
        }
    }
    
    return {
        "status": "success",
        "data": help_data
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Reddit Scraper API is running"
    }

@router.get("/debug/collections")
async def debug_collections():
    """Debug endpoint to list all MongoDB collections and their document counts"""
    try:
        from database.connectdb import connectdb
        
        # Connect to MongoDB
        client = connectdb()
        db = client.reddit_data
        
        # Get all collections
        collections = db.list_collection_names()
        
        collection_info = []
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            collection_info.append({
                "name": collection_name,
                "document_count": count
            })
        
        client.close()
        
        return {
            "status": "success",
            "data": {
                "database": "reddit_data",
                "collections": collection_info,
                "total_collections": len(collections)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error accessing MongoDB: {str(e)}"
        }

@router.get("/debug/collection/{collection_name}")
async def debug_collection(collection_name: str, limit: int = 5):
    """Debug endpoint to inspect a specific collection"""
    try:
        from database.connectdb import get_collection
        
        collection = get_collection(collection_name)
        
        # Get sample documents
        sample_docs = list(collection.find().limit(limit))
        
        # Get total count
        total_count = collection.count_documents({})
        
        return {
            "status": "success",
            "data": {
                "collection_name": collection_name,
                "total_documents": total_count,
                "sample_documents": sample_docs
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error accessing collection {collection_name}: {str(e)}"
        }

@router.delete("/debug/collection/{collection_name}")
async def clear_collection(collection_name: str):
    """Debug endpoint to clear a specific collection"""
    try:
        from database.connectdb import get_collection
        
        collection = get_collection(collection_name)
        
        # Clear all documents
        result = collection.delete_many({})
        
        return {
            "status": "success",
            "message": f"Cleared {result.deleted_count} documents from {collection_name}",
            "data": {
                "collection_name": collection_name,
                "deleted_count": result.deleted_count
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error clearing collection {collection_name}: {str(e)}"
        }
