from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Any

class RedditPost:
    def __init__(self, title: str, selftext: str, upvote_ratio: float, 
                 created_utc: float, permalink: str, subreddit: str = ""):
        self.title = title
        self.selftext = selftext
        self.upvote_ratio = upvote_ratio
        self.created_utc = created_utc
        self.permalink = permalink
        self.subreddit = subreddit
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "selftext": self.selftext,
            "upvote_ratio": self.upvote_ratio,
            "created_utc": self.created_utc,
            "permalink": self.permalink,
            "subreddit": self.subreddit,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RedditPost':
        return cls(
            title=data.get("title", ""),
            selftext=data.get("selftext", ""),
            upvote_ratio=data.get("upvote_ratio", 0.0),
            created_utc=data.get("created_utc", 0.0),
            permalink=data.get("permalink", ""),
            subreddit=data.get("subreddit", "")
        )
