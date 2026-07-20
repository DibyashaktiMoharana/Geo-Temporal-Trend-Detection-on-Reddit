from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.scrape_routes import router as scrape_router
from routes.translation_routes import router as translation_router
from routes.posts_routes import router as posts_router
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Reddit Scraper & Translation API",
    description="""
    A comprehensive API for scraping, storing, and analyzing Reddit posts from Indian cities.
    """,
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scrape_router)
app.include_router(translation_router)
app.include_router(posts_router)

@app.get("/")
async def root():
    """
    Root endpoint - API overview
    """
    return {
        "message": "Reddit Scraper & Translation API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "scraping": {
                "scrape_posts": "/api/scrape",
                "health_check": "/api/health"
            },
            "translation": {
                "translate_text": "/api/translation"
            },
            "posts": {
                "get_posts": "/api/posts",
                "get_subreddits": "/api/posts/subreddits",
                "get_stats": "/api/posts/stats"
            },
            "documentation": "/docs"
        },
        "database": {
            "name": "reddit_data",
            "collection_format": "{subreddit}Data"
        }
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
