import pandas as pd
from langdetect import detect, DetectorFactory
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import google.generativeai as genai
from sklearn.metrics import pairwise_distances_argmin_min
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def get_representative_posts(cluster_id, embeddings, df, max_posts=5):
    """Pick representative posts closest to the cluster centroid."""
    mask = df["topic"] == cluster_id
    cluster_embeddings = embeddings[mask]
    cluster_texts = df.loc[mask, "text"].tolist()

    if len(cluster_texts) == 0:
        return []

    centroid = cluster_embeddings.mean(axis=0).reshape(1, -1)
    sorted_idx = np.argsort(np.linalg.norm(cluster_embeddings - centroid, axis=1))
    selected = [cluster_texts[i] for i in sorted_idx[:max_posts]]
    return selected

def run_analysis():
    """Main analysis function"""
    print("Starting Reddit trend analysis...")
    
    # Check if source data exists
    if not os.path.exists("fine-tuning-dataset/delhiDatacsv.csv"):
        print("ERROR: fine-tuning-dataset/delhiDatacsv.csv not found!")
        print("Please ensure the source data file is available.")
        return False
    
    # Load & Preprocess Data
    print("Loading data...")
    df = pd.read_csv("fine-tuning-dataset/delhiDatacsv.csv")
    df["text"] = df["title"].fillna("") + " " + df["selftext"].fillna("")
    
    print("Detecting languages...")
    DetectorFactory.seed = 0
    df["language"] = df["text"].apply(lambda x: detect(x) if x.strip() else "unknown")
    df = df[df["language"] == "en"]
    print(f"Filtered to {len(df)} English posts")
    
    # spaCy processing
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")
    
    print("Extracting tokens and entities...")
    df["tokens"] = df["text"].apply(
        lambda x: [t.lemma_.lower() for t in nlp(x) if not t.is_stop and t.is_alpha]
    )
    df["entities"] = df["text"].apply(
        lambda x: [(ent.text, ent.label_) for ent in nlp(x).ents]
    )
    
    # Embeddings
    print("Generating embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)
    
    # Clustering
    print("Performing clustering...")
    NUM_TOPICS = 15
    clustering = KMeans(n_clusters=NUM_TOPICS, random_state=42)
    df["topic"] = clustering.fit_predict(embeddings)
    
    # Gemini Setup
    print("Configuring Gemini API...")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        return False
    genai.configure(api_key=gemini_api_key)
    
    def label_topic(cluster_id, docs):
        """Send representative docs to Gemini and ask for a topic name"""
        prompt = f"""
        You are analyzing Reddit posts from Delhi.
        Here are some example posts from cluster {cluster_id}:

        {docs}

        Please give a short, human-readable topic name (2-5 words).
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    
    # Label clusters
    print("Labeling topics with Gemini...")
    topic_labels = {}
    for cluster_id in sorted(df["topic"].unique()):
        print(f"  Labeling cluster {cluster_id}...")
        cluster_docs = get_representative_posts(cluster_id, embeddings, df, max_posts=5)
        topic_labels[cluster_id] = label_topic(cluster_id, cluster_docs)
    
    df["topic_label"] = df["topic"].map(topic_labels)
    
    # Save results
    print("Saving results...")
    df.to_csv("cleaned_delhiData_with_labels.csv", index=False)
    
    print("\n=== Analysis Complete! ===")
    print(f"Total posts processed: {len(df)}")
    print(f"Topics identified: {len(topic_labels)}")
    print("\nTopic labels:")
    for cluster_id, label in sorted(topic_labels.items()):
        print(f"  {cluster_id}: {label}")
    
    return True

if __name__ == "__main__":
    try:
        success = run_analysis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
