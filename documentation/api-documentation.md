# Analysis Model API Documentation

This Flask-based API provides JSON endpoints for the Reddit trend analysis model.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Download spaCy language model:

```bash
python -m spacy download en_core_web_sm
```

3. Run the model first to generate data files:

```bash
python model.py
```

4. Start the API server:

```bash
python api.py
```

The API will run on `http://localhost:5000`

## Changes from Previous Version

The API now computes representative posts **on-the-fly** using sentence embeddings instead of reading from a pre-generated JSON file. This means:

- No need for `topic_representatives.json`
- Representative posts are computed dynamically based on centroid distances
- More flexible and always up-to-date with the latest data
- On startup, the API precomputes embeddings for all posts for better performance

## API Endpoints

### 1. Health Check

**GET** `/api/health`

Check if the API is running and data is loaded.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T10:30:00",
  "data_loaded": true
}
```

### 2. Get All Topics

**GET** `/api/topics`

Get a summary of all detected topics.

**Response:**

```json
{
  "success": true,
  "total_topics": 15,
  "topics": [
    {
      "topic_id": 0,
      "topic_label": "Delhi Air Quality",
      "post_count": 245,
      "avg_score": 12.5
    }
  ]
}
```

### 3. Get Topic Details

**GET** `/api/topic/<topic_id>`

Get detailed information about a specific topic.

**Response:**

```json
{
  "success": true,
  "topic_id": 0,
  "topic_label": "Delhi Air Quality",
  "statistics": {
    "total_posts": 245,
    "avg_score": 12.5,
    "avg_comments": 8.3,
    "total_upvotes": 3062
  },
  "representative_posts": [
    {
      "text": "Sample post text...",
      "permalink": "https://reddit.com/r/delhi/..."
    }
  ],
  "top_posts": [
    {
      "title": "Post title",
      "score": 150,
      "permalink": "https://reddit.com/...",
      "created_utc": "2025-11-01T12:00:00"
    }
  ]
}
```

### 4. Get Timeline

**GET** `/api/timeline`

Get topic distribution over time.

**Response:**

```json
{
  "success": true,
  "timeline": [
    {
      "date": "2025-11-01",
      "topic": 0,
      "topic_label": "Delhi Air Quality",
      "count": 15
    }
  ]
}
```

### 5. Search Posts

**GET** `/api/search?q=<query>&topic=<topic_id>&limit=<limit>`

Search posts by keyword.

**Query Parameters:**

- `q` (required): Search query
- `topic` (optional): Filter by topic ID
- `limit` (optional): Maximum results (default: 20)

**Response:**

```json
{
  "success": true,
  "query": "pollution",
  "total_results": 15,
  "results": [
    {
      "title": "Post title",
      "topic": 0,
      "topic_label": "Delhi Air Quality",
      "score": 25,
      "permalink": "https://reddit.com/...",
      "created_utc": "2025-11-01T12:00:00"
    }
  ]
}
```

### 6. Get Overall Statistics

**GET** `/api/stats`

Get overall statistics about the dataset.

**Response:**

```json
{
  "success": true,
  "statistics": {
    "total_posts": 5000,
    "total_topics": 15,
    "avg_score": 10.5,
    "total_comments": 25000,
    "date_range": {
      "start": "2025-01-01T00:00:00",
      "end": "2025-11-04T23:59:59"
    },
    "top_topics": [
      {
        "topic": 0,
        "topic_label": "Delhi Air Quality",
        "count": 245
      }
    ]
  }
}
```

### 7. Get Topic Distribution

**GET** `/api/topic-distribution`

Get topic distribution with percentages for visualization.

**Response:**

```json
{
  "success": true,
  "distribution": [
    {
      "topic": 0,
      "topic_label": "Delhi Air Quality",
      "count": 245,
      "percentage": 16.33
    }
  ]
}
```

### 8. Reload Data

**POST** `/api/reload`

Reload data files (useful after re-running the model).

**Response:**

```json
{
  "success": true,
  "message": "Data reloaded successfully"
}
```

## CORS

CORS is enabled for all origins. For production, update the CORS settings in `api.py`.

## Error Handling

All endpoints return errors in the following format:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:

- `200`: Success
- `400`: Bad request (missing parameters)
- `404`: Resource not found
- `500`: Server error

## Example Usage

### JavaScript/Fetch

```javascript
// Get all topics
fetch("http://localhost:5000/api/topics")
  .then((response) => response.json())
  .then((data) => console.log(data));

// Get specific topic
fetch("http://localhost:5000/api/topic/0")
  .then((response) => response.json())
  .then((data) => console.log(data));

// Search
fetch("http://localhost:5000/api/search?q=pollution&limit=10")
  .then((response) => response.json())
  .then((data) => console.log(data));
```

### Python/Requests

```python
import requests

# Get all topics
response = requests.get('http://localhost:5000/api/topics')
topics = response.json()

# Get specific topic
response = requests.get('http://localhost:5000/api/topic/0')
topic_details = response.json()

# Search
response = requests.get('http://localhost:5000/api/search', params={'q': 'pollution', 'limit': 10})
search_results = response.json()
```

## Notes

- Make sure to run `model.py` first to generate the required data files
- The API expects `cleaned_delhiData_with_labels.csv` and `topic_representatives.json` in the same directory
- For production deployment, set `debug=False` and configure proper CORS origins
