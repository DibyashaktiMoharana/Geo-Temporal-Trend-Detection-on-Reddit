import os
import json
import asyncpraw
from dotenv import load_dotenv
from scripts.seedposts import seedposts

# Load environment variables
load_dotenv()

class RedditController:
    def __init__(self):
        """Initialize Reddit API client"""
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")
        
        if not all([self.client_id, self.client_secret, self.user_agent]):
            raise ValueError("Missing required Reddit API credentials in environment variables")
    
    async def _get_reddit_instance(self):
        """Get AsyncPRAW Reddit instance"""
        return asyncpraw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )
    
    async def scrape_posts(self, subreddit_name: str, listing_method: str = "hot", 
                    time_filter: str = "month"):
        """
        Scrape Reddit posts using various listing methods
        
        Args:
            subreddit_name (str): Name of the subreddit to scrape
            listing_method (str): Method to use - 'hot', 'new', 'top', 'rising'
            time_filter (str): Time filter for data collection - 'day', 'week', 'month', 'year', 'all'
        
        Returns:
            dict: Result with success status and data
        """
        try:
            reddit = await self._get_reddit_instance()
            subreddit = await reddit.subreddit(subreddit_name)
            posts_data = []
            
            print(f"Fetching {listing_method} posts from r/{subreddit_name} for {time_filter} timeframe...")
            
            # Get posts based on listing method (no limit for maximum data)
            if listing_method == "hot":
                posts = subreddit.hot(limit=None)
            elif listing_method == "new":
                posts = subreddit.new(limit=None)
            elif listing_method == "top":
                posts = subreddit.top(time_filter=time_filter, limit=None)
            elif listing_method == "rising":
                posts = subreddit.rising(limit=None)
            else:
                raise ValueError(f"Invalid listing method: {listing_method}. Use 'hot', 'new', 'top', or 'rising'")
            
            # Extract post data with 6 months filtering
            import time
            six_months_ago = time.time() - (6 * 30 * 24 * 60 * 60)  # 6 months in seconds
            
            async for post in posts:
                # Filter posts from last 6 months
                if post.created_utc < six_months_ago:
                    break  # Stop when we reach posts older than 6 months
                
                post_data = {
                    "title": post.title,
                    "selftext": post.selftext,
                    "upvote_ratio": post.upvote_ratio,
                    "created_utc": post.created_utc,
                    "permalink": post.permalink,
                    "subreddit": subreddit_name.lower(),
                }
                posts_data.append(post_data)
            
            # Save to JSON file
            json_filename = f"reddit_posts_{subreddit_name.lower().replace('+', '_')}_{listing_method}.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(posts_data, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully saved {len(posts_data)} posts to {json_filename}")
            
            # Close the reddit instance
            await reddit.close()
            
            # Seed to MongoDB
            try:
                seedposts(subreddit_name, listing_method)
                print("Successfully seeded data to MongoDB")
            except Exception as e:
                print(f"Error seeding to MongoDB: {e}")
                print("Posts saved to JSON file only")
            
            return {
                "success": True,
                "message": f"Successfully scraped {len(posts_data)} posts",
                "data": {
                    "posts_count": len(posts_data),
                    "json_file": json_filename,
                    "subreddit": subreddit_name,
                    "listing_method": listing_method,
                    "time_filter": time_filter
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error scraping posts: {str(e)}",
                "data": None
            }
    
    def get_available_listing_methods(self):
        """Get available listing methods and their descriptions"""
        return {
            "hot": "Most popular content right now",
            "new": "Most recent content", 
            "top": "Best posts in the specified timeframe",
            "rising": "Posts gaining traction quickly"
        }
    
    def get_available_time_filters(self):
        """Get available time filters for 'top' method"""
        return ["all", "day", "week", "month", "year"]
