from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File paths
LABELED_DATA_PATH = os.getenv("LABELED_DATA_PATH", "cleaned_delhiData_with_labels.csv")

# Global variables to store loaded data
labeled_df = None
embeddings_model = None
embeddings_cache = None

def load_data():
    """Load the processed data files"""
    global labeled_df, embeddings_model, embeddings_cache
    
    try:
        if os.path.exists(LABELED_DATA_PATH):
            labeled_df = pd.read_csv(LABELED_DATA_PATH)
            # Convert created_utc to datetime if it exists
            if 'created_utc' in labeled_df.columns:
                labeled_df['created_utc'] = pd.to_datetime(labeled_df['created_utc'], unit='s')
            
            # Load embedding model for computing representative posts
            embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("Loaded sentence transformer model")
            
            # Precompute embeddings for efficiency (optional, but recommended)
            embeddings_cache = embeddings_model.encode(labeled_df["text"].tolist(), show_progress_bar=True)
            print(f"Precomputed embeddings for {len(labeled_df)} posts")
        else:
            print(f"Warning: {LABELED_DATA_PATH} not found")
            labeled_df = None
            embeddings_model = None
            embeddings_cache = None
            
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def get_representative_posts(topic_id, max_posts=5):
    """
    Compute representative posts for a topic on-the-fly.
    Returns posts closest to the cluster centroid.
    """
    if labeled_df is None or embeddings_cache is None:
        return []
    
    # Filter posts in this topic
    mask = labeled_df["topic"] == topic_id
    topic_df = labeled_df[mask]
    cluster_embeddings = embeddings_cache[mask]
    
    if len(topic_df) == 0:
        return []
    
    # Compute centroid
    centroid = cluster_embeddings.mean(axis=0).reshape(1, -1)
    
    # Find posts closest to centroid
    distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
    sorted_idx = np.argsort(distances)
    
    # Select top posts
    representatives = []
    for i in sorted_idx[:max_posts]:
        post = topic_df.iloc[i]
        representatives.append({
            "text": post["text"][:300] if pd.notna(post["text"]) else "",
            "title": post["title"] if "title" in post and pd.notna(post["title"]) else "",
            "permalink": f"https://reddit.com{post['permalink']}" if "permalink" in post and pd.notna(post["permalink"]) else "",
            "score": int(post["score"]) if "score" in post and pd.notna(post["score"]) else 0
        })
    
    return representatives

# Load data on startup
load_data()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': labeled_df is not None,
        'embeddings_loaded': embeddings_cache is not None
    })


@app.route('/api/topics', methods=['GET'])
def get_all_topics():
    """Get all topics with their labels and post counts"""
    if labeled_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        # Group by topic and get counts
        topic_summary = labeled_df.groupby(['topic', 'topic_label']).agg({
            'id': 'count',
            'score': 'mean'
        }).reset_index()
        
        topic_summary.columns = ['topic_id', 'topic_label', 'post_count', 'avg_score']
        
        # Sort by post count
        topic_summary = topic_summary.sort_values('post_count', ascending=False)
        
        # Convert to list of dicts
        topics = topic_summary.to_dict('records')
        
        # Round avg_score
        for topic in topics:
            topic['avg_score'] = round(topic['avg_score'], 2)
            topic['topic_id'] = int(topic['topic_id'])
        
        return jsonify({
            'success': True,
            'total_topics': len(topics),
            'topics': topics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/topic/<int:topic_id>', methods=['GET'])
def get_topic_details(topic_id):
    """Get detailed information about a specific topic"""
    if labeled_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
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
            'avg_score': round(float(topic_posts['score'].mean()), 2) if 'score' in topic_posts.columns else 0,
            'avg_comments': round(float(topic_posts['num_comments'].mean()), 2) if 'num_comments' in topic_posts.columns else 0,
            'total_upvotes': int(topic_posts['score'].sum()) if 'score' in topic_posts.columns else 0
        }
        
        # Get representative posts (computed on-the-fly)
        representatives = get_representative_posts(topic_id, max_posts=5)
        
        # Get top posts by score
        columns_to_get = ['title', 'score']
        if 'permalink' in topic_posts.columns:
            columns_to_get.append('permalink')
        if 'created_utc' in topic_posts.columns:
            columns_to_get.append('created_utc')
        
        top_posts = topic_posts.nlargest(10, 'score')[columns_to_get].to_dict('records')
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
        columns = ['title', 'topic', 'topic_label', 'score', 'permalink', 'created_utc']
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
            'avg_score': round(float(labeled_df['score'].mean()), 2) if 'score' in labeled_df.columns else 0,
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
