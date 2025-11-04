# API Documentation

## Base URL
- **Local Development**: `http://localhost:5000`
- **Production**: `https://reddit-trend-analysis-api.onrender.com`

---

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Endpoints](#endpoints)
   - [Root & Health Check](#root--health-check)
   - [Data Processing](#data-processing)
   - [Topics](#topics)
   - [Statistics](#statistics)
   - [Search & Timeline](#search--timeline)

---

## Overview

This API provides access to analyzed Reddit posts from subreddits. It uses machine learning to cluster posts into topics, generates topic labels using Google Gemini AI, and provides multilingual support through Sarvam AI translation.

### Key Features
- **15 Topic Clusters**: Posts automatically categorized into trending topics
- **Multilingual Support**: Auto-detects and translates Hindi, Bengali, Tamil, Telugu, and other Indian languages to English
- **Representative Posts**: Pre-computed most relevant posts for each topic
- **Time-based Analysis**: Timeline view of topic distribution
- **Search Functionality**: Full-text search across all posts

---

## Authentication

Currently, this API does not require authentication. All endpoints are publicly accessible.

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Error description message",
  "processing_status": {
    "is_processing": false,
    "message": "Status message",
    "progress": 0
  }
}
```

### HTTP Status Codes
- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side error
- **503 Service Unavailable**: Data not loaded/processed

---

## Endpoints

### Root & Health Check

#### `GET /`
Get API information and available endpoints.

**Response:**
```json
{
  "service": "Reddit Trend Analysis API",
  "status": "running",
  "data_loaded": true,
  "endpoints": {
    "health": "/api/health",
    "process_data": "POST /api/process",
    "processing_status": "/api/processing-status",
    "all_topics": "/api/topics",
    "topic_details": "/api/topic/<id>",
    "statistics": "/api/stats",
    "timeline": "/api/timeline",
    "search": "/api/search?q=<query>",
    "distribution": "/api/topic-distribution",
    "reload": "POST /api/reload"
  },
  "message": "API ready to serve data!"
}
```

---

#### `GET /api/health`
Health check endpoint with detailed status information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T10:30:00.123456",
  "data_loaded": true,
  "total_posts": 965,
  "representative_posts_loaded": true,
  "processing_status": {
    "is_processing": false,
    "message": "Processing complete!",
    "progress": 100
  }
}
```

**Response Fields:**
- `status` (string): Service health status ("healthy" | "unhealthy")
- `timestamp` (string): Current server timestamp (ISO 8601)
- `data_loaded` (boolean): Whether processed data is available
- `total_posts` (integer): Number of posts loaded
- `representative_posts_loaded` (boolean): Whether representative posts are available
- `processing_status` (object): Current processing status

---

### Data Processing

#### `POST /api/process`
Trigger background data processing (runs model.py).

**Response (Success):**
```json
{
  "success": true,
  "message": "Processing started in background. Check /api/health for status.",
  "status": {
    "is_processing": true,
    "message": "Running model.py...",
    "progress": 10
  }
}
```

**Response (Already Processing):**
```json
{
  "success": false,
  "message": "Processing already in progress",
  "status": {
    "is_processing": true,
    "message": "Running model.py...",
    "progress": 50
  }
}
```
*HTTP Status: 400*

---

#### `GET /api/processing-status`
Get current data processing status.

**Response:**
```json
{
  "success": true,
  "status": {
    "is_processing": false,
    "message": "Processing complete!",
    "progress": 100
  },
  "data_available": true
}
```

**Status Progress Values:**
- `0`: Not started or failed
- `10`: Started running model.py
- `90`: Model complete, loading data
- `100`: Processing complete

---

#### `POST /api/reload`
Reload data files from disk (useful after manual model reruns).

**Response:**
```json
{
  "success": true,
  "message": "Data reloaded successfully"
}
```

---

### Topics

#### `GET /api/topics`
Get all topics with labels and post counts.

**Response:**
```json
{
  "success": true,
  "total_topics": 15,
  "topics": [
    {
      "topic_id": 0,
      "topic_label": "Traffic and Transportation Issues",
      "post_count": 125
    },
    {
      "topic_id": 1,
      "topic_label": "Air Quality and Pollution",
      "post_count": 98
    },
    {
      "topic_id": 2,
      "topic_label": "Metro Services and Updates",
      "post_count": 87
    }
    // ... more topics
  ]
}
```

**Response Fields:**
- `success` (boolean): Request success status
- `total_topics` (integer): Number of unique topics
- `topics` (array): List of topic objects
  - `topic_id` (integer): Unique topic identifier (0-14)
  - `topic_label` (string): Human-readable topic name
  - `post_count` (integer): Number of posts in this topic

---

#### `GET /api/topic/<topic_id>`
Get detailed information about a specific topic.

**Parameters:**
- `topic_id` (integer, path): Topic ID (0-14)

**Response:**
```json
{
  "success": true,
  "topic_id": 0,
  "topic_label": "Traffic and Transportation Issues",
  "statistics": {
    "total_posts": 125,
    "avg_upvote_ratio": 0.87,
    "avg_comments": 23.5
  },
  "representative_posts": [
    {
      "text": "The traffic on Ring Road is getting worse every day...",
      "title": "Ring Road Traffic Nightmare",
      "permalink": "https://reddit.com/r/delhi/comments/abc123/...",
      "id": "abc123"
    }
    // ... 4 more representative posts
  ],
  "top_posts": [
    {
      "title": "Latest traffic update on NH-24",
      "_id": "xyz789",
      "permalink": "https://reddit.com/r/delhi/comments/xyz789/...",
      "created_utc": "2025-11-04T15:30:00",
      "upvote_ratio": 0.92
    }
    // ... up to 10 recent posts
  ]
}
```

**Response Fields:**
- `success` (boolean): Request success status
- `topic_id` (integer): Topic identifier
- `topic_label` (string): Topic name
- `statistics` (object): Aggregate statistics
  - `total_posts` (integer): Number of posts in topic
  - `avg_upvote_ratio` (float): Average upvote ratio (0-1)
  - `avg_comments` (float): Average number of comments
- `representative_posts` (array): 5 most representative posts (centroid-based)
  - `text` (string): Post content (first 300 chars)
  - `title` (string): Post title
  - `permalink` (string): Reddit URL
  - `id` (string): Reddit post ID
- `top_posts` (array): Up to 10 most recent posts

**Error Response (404):**
```json
{
  "error": "Topic 99 not found"
}
```

---

#### `GET /api/topic-distribution`
Get topic distribution for visualization.

**Response:**
```json
{
  "success": true,
  "distribution": [
    {
      "topic": 0,
      "topic_label": "Traffic and Transportation Issues",
      "count": 125,
      "percentage": 12.95
    },
    {
      "topic": 1,
      "topic_label": "Air Quality and Pollution",
      "count": 98,
      "percentage": 10.15
    }
    // ... all topics sorted by count descending
  ]
}
```

**Response Fields:**
- `success` (boolean): Request success status
- `distribution` (array): Topic distribution sorted by post count
  - `topic` (integer): Topic ID
  - `topic_label` (string): Topic name
  - `count` (integer): Number of posts
  - `percentage` (float): Percentage of total posts (2 decimal places)

---

### Statistics

#### `GET /api/stats`
Get overall statistics across all posts and topics.

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_posts": 965,
    "total_topics": 15,
    "avg_upvote_ratio": 0.84,
    "total_comments": 15420,
    "date_range": {
      "start": "2025-01-01T00:00:00",
      "end": "2025-11-05T23:59:59"
    },
    "top_topics": [
      {
        "topic": 0,
        "topic_label": "Traffic and Transportation Issues",
        "count": 125
      },
      {
        "topic": 1,
        "topic_label": "Air Quality and Pollution",
        "count": 98
      }
      // ... top 5 topics
    ]
  }
}
```

**Response Fields:**
- `success` (boolean): Request success status
- `statistics` (object): Overall statistics
  - `total_posts` (integer): Total number of posts analyzed
  - `total_topics` (integer): Number of unique topics
  - `avg_upvote_ratio` (float): Average upvote ratio across all posts
  - `total_comments` (integer): Sum of all comments
  - `date_range` (object): Time range of posts
    - `start` (string, ISO 8601): Earliest post timestamp
    - `end` (string, ISO 8601): Latest post timestamp
  - `top_topics` (array): Top 5 topics by post count

---

### Search & Timeline

#### `GET /api/search`
Search posts by keyword with optional filters.

**Query Parameters:**
- `q` (string, required): Search query
- `topic` (integer, optional): Filter by topic ID
- `limit` (integer, optional): Maximum results to return (default: 20)

**Example Request:**
```
GET /api/search?q=pollution&topic=1&limit=10
```

**Response:**
```json
{
  "success": true,
  "query": "pollution",
  "total_results": 10,
  "results": [
    {
      "title": "Air pollution levels hit new high in Delhi",
      "topic": 1,
      "topic_label": "Air Quality and Pollution",
      "upvote_ratio": 0.95,
      "permalink": "https://reddit.com/r/delhi/comments/abc123/...",
      "created_utc": "2025-11-04T10:00:00"
    }
    // ... more results
  ]
}
```

**Response Fields:**
- `success` (boolean): Request success status
- `query` (string): Search query used
- `total_results` (integer): Number of results returned
- `results` (array): Matching posts
  - `title` (string): Post title
  - `topic` (integer): Topic ID
  - `topic_label` (string): Topic name
  - `upvote_ratio` (float): Upvote ratio
  - `permalink` (string): Reddit URL
  - `created_utc` (string, ISO 8601): Post timestamp

**Error Response (400):**
```json
{
  "error": "Query parameter \"q\" is required"
}
```

---

#### `GET /api/timeline`
Get topic distribution over time.

**Response:**
```json
{
  "success": true,
  "timeline": [
    {
      "date": "2025-11-01",
      "topic": 0,
      "topic_label": "Traffic and Transportation Issues",
      "count": 15
    },
    {
      "date": "2025-11-01",
      "topic": 1,
      "topic_label": "Air Quality and Pollution",
      "count": 12
    },
    {
      "date": "2025-11-02",
      "topic": 0,
      "topic_label": "Traffic and Transportation Issues",
      "count": 18
    }
    // ... more timeline data
  ]
}
```

**Response Fields:**
- `success` (boolean): Request success status
- `timeline` (array): Daily topic distribution
  - `date` (string, YYYY-MM-DD): Date
  - `topic` (integer): Topic ID
  - `topic_label` (string): Topic name
  - `count` (integer): Number of posts on that date for that topic

**Error Response (400):**
```json
{
  "error": "Timestamp data not available"
}
```

---

## Data Processing Pipeline

### 1. **Data Loading**
- Loads Reddit posts from CSV (`fine-tuning-dataset/delhiDatacsv.csv`)
- Posts contain: title, selftext, upvote_ratio, created_utc, permalink, subreddit

### 2. **Multilingual Translation** 
- **Auto-detects** language using Sarvam AI
- **Translates** non-English posts (Hindi, Bengali, Tamil, etc.) to English
- Creates `title_english` and `selftext_english` columns
- Fallback: Uses original text if translation fails

### 3. **Language Filtering**
- Filters to English posts (after translation)
- Uses `langdetect` library

### 4. **Text Processing**
- Tokenization using spaCy (`en_core_web_sm`)
- Lemmatization and stopword removal
- Memory-optimized (disabled parser/NER)

### 5. **Embeddings**
- Generates semantic embeddings using `sentence-transformers` (all-MiniLM-L6-v2)
- Batch processing (batch_size=32) for memory efficiency

### 6. **Topic Clustering**
- KMeans clustering (15 topics)
- Assigns each post to a topic

### 7. **Topic Labeling**
- Uses Google Gemini AI (gemini-2.5-flash) to generate human-readable topic labels
- Analyzes representative posts per cluster

### 8. **Representative Posts Selection**
- Centroid-based selection
- Picks 5 most representative posts per topic
- Pre-computed and saved to `representative_posts.json`

### 9. **Output Files**
- `cleaned_delhiData_with_labels.csv`: Full dataset with topics and labels
- `representative_posts.json`: Pre-computed representative posts

---

## Environment Variables

Required environment variables (in `.env` file):

```bash
# Google Gemini API for topic labeling
GEMINI_API_KEY=your_gemini_api_key_here

# Sarvam AI API for multilingual translation
SARVAM_API_KEY=your_sarvam_api_key_here

# Server port (optional, default: 5000)
PORT=5000

# Path to labeled data file (optional)
LABELED_DATA_PATH=cleaned_delhiData_with_labels.csv
```

---

## Rate Limits

Currently, there are no rate limits enforced. However, consider implementing rate limiting for production use.

---

## Examples

### Using cURL

**Get all topics:**
```bash
curl https://reddit-trend-analysis-api.onrender.com/api/topics
```

**Get topic details:**
```bash
curl https://reddit-trend-analysis-api.onrender.com/api/topic/0
```

**Search posts:**
```bash
curl "https://reddit-trend-analysis-api.onrender.com/api/search?q=pollution&limit=5"
```

**Health check:**
```bash
curl https://reddit-trend-analysis-api.onrender.com/api/health
```

### Using JavaScript (Fetch API)

```javascript
// Get all topics
fetch('https://reddit-trend-analysis-api.onrender.com/api/topics')
  .then(response => response.json())
  .then(data => console.log(data.topics));

// Search posts
fetch('https://reddit-trend-analysis-api.onrender.com/api/search?q=traffic')
  .then(response => response.json())
  .then(data => console.log(data.results));

// Get topic details
fetch('https://reddit-trend-analysis-api.onrender.com/api/topic/0')
  .then(response => response.json())
  .then(data => {
    console.log('Topic:', data.topic_label);
    console.log('Representative posts:', data.representative_posts);
  });
```

### Using Python (requests)

```python
import requests

# Base URL
BASE_URL = "https://reddit-trend-analysis-api.onrender.com"

# Get all topics
response = requests.get(f"{BASE_URL}/api/topics")
topics = response.json()['topics']

# Search posts
params = {"q": "pollution", "limit": 10}
response = requests.get(f"{BASE_URL}/api/search", params=params)
results = response.json()['results']

# Get statistics
response = requests.get(f"{BASE_URL}/api/stats")
stats = response.json()['statistics']
print(f"Total posts: {stats['total_posts']}")
print(f"Total topics: {stats['total_topics']}")
```

---

## TypeScript Type Definitions

```typescript
// Response types
interface APIResponse<T> {
  success: boolean;
  [key: string]: T | boolean;
}

interface Topic {
  topic_id: number;
  topic_label: string;
  post_count: number;
}

interface TopicDetails {
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

interface RepresentativePost {
  text: string;
  title: string;
  permalink: string;
  id: string;
}

interface Post {
  title: string;
  _id: string;
  permalink?: string;
  created_utc?: string;
  upvote_ratio?: number;
  topic?: number;
  topic_label?: string;
}

interface Statistics {
  total_posts: number;
  total_topics: number;
  avg_upvote_ratio: number;
  total_comments: number;
  date_range: {
    start: string | null;
    end: string | null;
  };
  top_topics: Array<{
    topic: number;
    topic_label: string;
    count: number;
  }>;
}

interface SearchResult {
  success: boolean;
  query: string;
  total_results: number;
  results: Post[];
}

interface TimelineData {
  date: string;
  topic: number;
  topic_label: string;
  count: number;
}

interface ProcessingStatus {
  is_processing: boolean;
  message: string;
  progress: number;
}

interface HealthCheck {
  status: "healthy" | "unhealthy";
  timestamp: string;
  data_loaded: boolean;
  total_posts: number;
  representative_posts_loaded: boolean;
  processing_status: ProcessingStatus;
}
```

