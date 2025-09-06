from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.scrape_routes import router
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Reddit Scraper API",
    description="A FastAPI application for scraping Reddit posts with various listing methods",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
