from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import threading
import subprocess
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File paths
LABELED_DATA_PATH = os.getenv("LABELED_DATA_PATH", "cleaned_delhiData_with_labels.csv")
REPRESENTATIVE_POSTS_PATH = "representative_posts.json"

# Global variables to store loaded data
labeled_df = None
representative_posts = {}  # Dict mapping topic_id -> list of representative posts

processing_status = {"is_processing": False, "message": "Not started", "progress": 0}

def load_data():
    """Load the processed data files - lightweight version without embeddings"""
    global labeled_df, representative_posts
    
    try:
        if os.path.exists(LABELED_DATA_PATH):
            print(f"Loading data from {LABELED_DATA_PATH}...")
            labeled_df = pd.read_csv(LABELED_DATA_PATH)
            
            # Drop unnecessary columns to save memory
            # columns_to_drop = ['tokens', 'entities', 'language', 'selftext']
            # for col in columns_to_drop:
            #     if col in labeled_df.columns:
            #         labeled_df.drop(col, axis=1, inplace=True)
            
            # Convert created_utc to datetime if it exists
            if 'created_utc' in labeled_df.columns:
                labeled_df['created_utc'] = pd.to_datetime(labeled_df['created_utc'], unit='s')
            
            print(f"Loaded {len(labeled_df)} posts successfully!")
            
            # Load representative posts if available
            if os.path.exists(REPRESENTATIVE_POSTS_PATH):
                with open(REPRESENTATIVE_POSTS_PATH, 'r') as f:
                    representative_posts = json.load(f)
                print(f"Loaded representative posts for {len(representative_posts)} topics")
            else:
                print(f"Warning: {REPRESENTATIVE_POSTS_PATH} not found")
                representative_posts = {}
            
            return True
        else:
            print(f"Warning: {LABELED_DATA_PATH} not found. Data needs to be processed.")
            labeled_df = None
            representative_posts = {}
            return False
            
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def process_data_background():
    """Process data in background thread"""
    global processing_status
    try:
        processing_status["is_processing"] = True
        processing_status["message"] = "Running model.py..."
        processing_status["progress"] = 10
        
        # Run model.py
        result = subprocess.run(['python', 'model.py'], capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            processing_status["progress"] = 90
            processing_status["message"] = "Loading processed data..."
            
            # Load the newly created data
            if load_data():
                processing_status["is_processing"] = False
                processing_status["message"] = "Processing complete!"
                processing_status["progress"] = 100
            else:
                processing_status["is_processing"] = False
                processing_status["message"] = "Failed to load processed data"
                processing_status["progress"] = 0
        else:
            processing_status["is_processing"] = False
            processing_status["message"] = f"Processing failed: {result.stderr}"
            processing_status["progress"] = 0
            
    except subprocess.TimeoutExpired:
        processing_status["is_processing"] = False
        processing_status["message"] = "Processing timed out (>10 minutes)"
        processing_status["progress"] = 0
    except Exception as e:
        processing_status["is_processing"] = False
        processing_status["message"] = f"Error: {str(e)}"
        processing_status["progress"] = 0

# Load data on startup (if available)
print("=== Starting API Server ===")
data_loaded = load_data()
if not data_loaded:
    print("No processed data found. Use /api/process endpoint to start processing.")


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        'service': 'Reddit Trend Analysis API',
        'status': 'running',
        'data_loaded': labeled_df is not None,
        'endpoints': {
            'health': '/api/health',
            'process_data': 'POST /api/process',
            'processing_status': '/api/processing-status',
            'all_topics': '/api/topics',
            'topic_details': '/api/topic/<id>',
            'statistics': '/api/stats',
            'timeline': '/api/timeline',
            'search': '/api/search?q=<query>',
            'distribution': '/api/topic-distribution',
            'reload': 'POST /api/reload'
        },
        'message': 'Data not processed yet. Send POST to /api/process to start.' if labeled_df is None else 'API ready to serve data!'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': labeled_df is not None,
        'total_posts': len(labeled_df) if labeled_df is not None else 0,
        'representative_posts_loaded': len(representative_posts) > 0,
        'processing_status': processing_status
    })


@app.route('/api/process', methods=['POST'])
def trigger_processing():
    """Trigger data processing"""
    global processing_status
    
    if processing_status["is_processing"]:
        return jsonify({
            'success': False,
            'message': 'Processing already in progress',
            'status': processing_status
        }), 400
    
    if labeled_df is not None:
        return jsonify({
            'success': False,
            'message': 'Data already processed. Use /api/reload to reload.',
            'status': processing_status
        }), 400
    
    # Start processing in background thread
    thread = threading.Thread(target=process_data_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Processing started in background. Check /api/health for status.',
        'status': processing_status
    })


@app.route('/api/processing-status', methods=['GET'])
def get_processing_status():
    """Get current processing status"""
    return jsonify({
        'success': True,
        'status': processing_status,
        'data_available': labeled_df is not None
    })


@app.route('/api/topics', methods=['GET'])
def get_all_topics():
    """Get all topics with their labels and post counts"""
    if labeled_df is None:
        return jsonify({
            'error': 'Data not loaded. Please run /api/process first.',
            'processing_status': processing_status
        }), 503
    
    try:
        # Group by topic and get counts
        topic_summary = labeled_df.groupby(['topic', 'topic_label']).agg({
            '_id': 'count'
        }).reset_index()
        
        topic_summary.columns = ['topic_id', 'topic_label', 'post_count']
        
        # Sort by post count
        topic_summary = topic_summary.sort_values('post_count', ascending=False)
        
        # Convert to list of dicts
        topics = topic_summary.to_dict('records')
        
        # Convert topic_id to int
        for topic in topics:
            topic['topic_id'] = int(topic['topic_id'])
        
        return jsonify({
            'success': True,
            'total_topics': len(topics),
            'topics': topics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#calls get_representative_posts
@app.route('/api/topic/<int:topic_id>', methods=['GET'])
def get_topic_details(topic_id):
    """Get detailed information about a specific topic"""
    if labeled_df is None:
        return jsonify({
            'error': 'Data not loaded. Please run /api/process first.',
            'processing_status': processing_status
        }), 503
    
    try:
        # Filter posts for this topic
        topic_posts = labeled_df[labeled_df['topic'] == topic_id]
        
        if len(topic_posts) == 0:
            return jsonify({'error': f'Topic {topic_id} not found'}), 404
        
        # Get topic label
        topic_label = topic_posts['topic_label'].iloc[0] if pd.notna(topic_posts['topic_label'].iloc[0]) else f"Topic {topic_id}"
        
        # Get statistics
        stats = {
            'total_posts': int(len(topic_posts)),
            'avg_upvote_ratio': round(float(topic_posts['upvote_ratio'].mean()), 2) if 'upvote_ratio' in topic_posts.columns else 0,
            'avg_comments': round(float(topic_posts['num_comments'].mean()), 2) if 'num_comments' in topic_posts.columns else 0
        }
        
        # Get representative posts from pre-computed data
        # Convert topic_id to string since JSON keys are strings
        representatives = representative_posts.get(str(topic_id), [])
        
        # If no pre-computed representatives, fall back to first 5 posts
        if not representatives:
            top_5_posts = topic_posts.head(5)
            representatives = []
            for _, post in top_5_posts.iterrows():
                representatives.append({
                    "text": post["text"][:300] if pd.notna(post["text"]) else "",
                    "title": post["title"] if "title" in topic_posts.columns and pd.notna(post["title"]) else "",
                    "permalink": f"https://reddit.com{post['permalink']}" if "permalink" in topic_posts.columns and pd.notna(post["permalink"]) else "",
                    "id": post["_id"] if "_id" in topic_posts.columns and pd.notna(post["_id"]) else ""
                })
        
        # Get recent posts
        columns_to_get = ['title', '_id']
        if 'permalink' in topic_posts.columns:
            columns_to_get.append('permalink')
        if 'created_utc' in topic_posts.columns:
            columns_to_get.append('created_utc')
        if 'upvote_ratio' in topic_posts.columns:
            columns_to_get.append('upvote_ratio')
        
        # Sort by created_utc if available, otherwise just take first 10
        if 'created_utc' in topic_posts.columns:
            top_posts = topic_posts.nlargest(10, 'created_utc')[columns_to_get].to_dict('records')
        else:
            top_posts = topic_posts.head(10)[columns_to_get].to_dict('records')
            
        for post in top_posts:
            if 'created_utc' in post and pd.notna(post['created_utc']):
                post['created_utc'] = post['created_utc'].isoformat()
            if 'permalink' in post and pd.notna(post['permalink']):
                post['permalink'] = f"https://reddit.com{post['permalink']}"
        
        return jsonify({
            'success': True,
            'topic_id': topic_id,
            'topic_label': topic_label,
            'statistics': stats,
            'representative_posts': representatives,
            'top_posts': top_posts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    """Get topic distribution over time"""
    if labeled_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Check if created_utc exists
        if 'created_utc' not in labeled_df.columns:
            return jsonify({'error': 'Timestamp data not available'}), 400
        
        df_copy = labeled_df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['created_utc']).dt.date
        
        # Group by date and topic
        timeline = df_copy.groupby(['date', 'topic', 'topic_label']).size().reset_index(name='count')
        timeline['date'] = timeline['date'].astype(str)
        
        # Convert to dict format
        timeline_data = timeline.to_dict('records')
        
        return jsonify({
            'success': True,
            'timeline': timeline_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_posts():
    """Search posts by keyword"""
    if labeled_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        query = request.args.get('q', '').lower()
        topic_filter = request.args.get('topic', None)
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        # Search in title and text
        df_search = labeled_df.copy()
        df_search['combined'] = (df_search['title'].fillna('') + ' ' + df_search['text'].fillna('')).str.lower()
        results = df_search[df_search['combined'].str.contains(query, na=False)]
        
        # Apply topic filter if provided
        if topic_filter is not None:
            results = results[results['topic'] == int(topic_filter)]
        
        # Select relevant columns and limit results
        columns = ['title', 'topic', 'topic_label', 'upvote_ratio', 'permalink', 'created_utc']
        available_columns = [col for col in columns if col in results.columns]
        results = results[available_columns].head(limit)
        
        # Convert to dict
        results_list = results.to_dict('records')
        for result in results_list:
            if 'created_utc' in result and pd.notna(result['created_utc']):
                result['created_utc'] = result['created_utc'].isoformat()
        
        return jsonify({
            'success': True,
            'query': query,
            'total_results': len(results_list),
            'results': results_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_overall_stats():
    """Get overall statistics"""
    if labeled_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        stats = {
            'total_posts': int(len(labeled_df)),
            'total_topics': int(labeled_df['topic'].nunique()),
            'avg_upvote_ratio': round(float(labeled_df['upvote_ratio'].mean()), 2) if 'upvote_ratio' in labeled_df.columns else 0,
            'total_comments': int(labeled_df['num_comments'].sum()) if 'num_comments' in labeled_df.columns else 0,
            'date_range': {
                'start': labeled_df['created_utc'].min().isoformat() if 'created_utc' in labeled_df.columns else None,
                'end': labeled_df['created_utc'].max().isoformat() if 'created_utc' in labeled_df.columns else None
            }
        }
        
        # Top topics by post count
        top_topics = labeled_df.groupby(['topic', 'topic_label']).size().reset_index(name='count')
        top_topics = top_topics.nlargest(5, 'count')
        stats['top_topics'] = top_topics.to_dict('records')
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reload', methods=['POST'])
def reload_data():
    """Reload the data files (useful after model re-runs)"""
    try:
        success = load_data()
        if success:
            return jsonify({
                'success': True,
                'message': 'Data reloaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to reload data'
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/topic-distribution', methods=['GET'])
def get_topic_distribution():
    """Get topic distribution for visualization"""
    if labeled_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        distribution = labeled_df.groupby(['topic', 'topic_label']).size().reset_index(name='count')
        distribution = distribution.sort_values('count', ascending=False)
        
        # Calculate percentages
        total = distribution['count'].sum()
        distribution['percentage'] = (distribution['count'] / total * 100).round(2)
        
        return jsonify({
            'success': True,
            'distribution': distribution.to_dict('records')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
