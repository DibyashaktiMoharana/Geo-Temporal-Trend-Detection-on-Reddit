// API Types
export interface Topic {
  topic_id: number;
  topic_label: string;
  post_count: number;
}

export interface TopicDistribution {
  topic: number;
  topic_label: string;
  count: number;
  percentage: number;
}

export interface Post {
  _id: string;
  title: string;
  text?: string;
  selftext?: string;
  permalink: string;
  created_utc: string;
  upvote_ratio: number;
  num_comments?: number;
  score?: number;
  topic?: number;
  topic_label?: string;
}

export interface RepresentativePost {
  id: string;
  text: string;
  title: string;
  permalink: string;
}

export interface TopicDetail {
  success: boolean;
  topic_id: number;
  topic_label: string;
  statistics: {
    total_posts: number;
    avg_upvote_ratio: number;
    avg_comments: number;
  };
  representative_posts: RepresentativePost[];
  top_posts: Post[];
}

export interface Statistics {
  total_posts: number;
  total_topics: number;
  avg_upvote_ratio: number;
  total_comments: number;
  date_range: {
    start: string;
    end: string;
  };
  top_topics: {
    topic: number;
    topic_label: string;
    count: number;
  }[];
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  data_loaded: boolean;
  total_posts?: number;
  representative_posts_loaded?: boolean;
  processing_status: {
    is_processing: boolean;
    message: string;
    progress: number;
  };
}

export interface TimelineData {
  success: boolean;
  timeline: {
    date: string;
    topic: number;
    topic_label: string;
    count: number;
  }[];
  date_range?: {
    start: string;
    end: string;
  };
}

export interface SearchResult {
  success: boolean;
  query: string;
  total_results: number;
  results: Post[];
}

// Scraper Types
export interface ScrapeResult {
  status: string;
  message: string;
  data: {
    subreddit: string;
    method: string;
    time_filter: string;
    posts_saved: number;
    posts: any[];
  };
}
