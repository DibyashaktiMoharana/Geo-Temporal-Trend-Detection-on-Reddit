import pandas as pd
from langdetect import detect, DetectorFactory
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import google.generativeai as genai  # Gemini SDK
from sklearn.metrics import pairwise_distances_argmin_min
import os
from dotenv import load_dotenv
import gc
from sarvamai import SarvamAI

# Load environment variables
load_dotenv()

# -----------------------------
# Sarvam Translation Setup
# -----------------------------
sarvam_api_key = os.getenv("SARVAM_API_KEY")
if not sarvam_api_key:
    print("WARNING: SARVAM_API_KEY not set. Translation will be skipped.")
    sarvam_client = None
else:
    sarvam_client = SarvamAI(api_subscription_key=sarvam_api_key)

def auto_translate_to_english(text):
    """
    Automatically detect language and translate to English using Sarvam AI
    Returns the translated text or original if already English/translation fails
    """
    if not sarvam_client or not text or not text.strip():
        return text
    
    try:
        # Step 1: Detect language
        detection_response = sarvam_client.text.identify_language(input=text)
        detected_language = detection_response.language_code
        
        # Step 2: If already English, return as is
        if detected_language == "en-IN":
            return text
        
        # Step 3: Translate to English
        translation_response = sarvam_client.text.translate(
            input=text,
            source_language_code=detected_language,
            target_language_code="en-IN",
            speaker_gender="Male",
            mode="classic-colloquial",
            enable_preprocessing=False,
        )
        
        translated_text = translation_response.translated_text
        print(f"Translated from {detected_language}: {text[:50]}... -> {translated_text[:50]}...")
        return translated_text
        
    except Exception as e:
        print(f"Translation error for text '{text[:50]}...': {e}")
        return text  # Return original text if translation fails

# -----------------------------
# Representative posts function
# -----------------------------
def get_representative_posts(cluster_id, embeddings, df, max_posts=5):
    """
    Pick representative posts closest to the cluster centroid.
    """
    # Filter posts in this cluster
    mask = df["topic"] == cluster_id
    cluster_embeddings = embeddings[mask]
    cluster_texts = df.loc[mask, "text"].tolist()

    if len(cluster_texts) == 0:
        return []

    # Compute centroid
    centroid = cluster_embeddings.mean(axis=0).reshape(1, -1)

    # Find closest posts to centroid
    closest_idx, _ = pairwise_distances_argmin_min(centroid, cluster_embeddings)
    sorted_idx = np.argsort(np.linalg.norm(cluster_embeddings - centroid, axis=1))

    # Select top max_posts closest
    selected = [cluster_texts[i] for i in sorted_idx[:max_posts]]
    return selected


# -----------------------------
# 1. Load & Preprocess Data
# -----------------------------
print("Loading data...")
df = pd.read_csv("fine-tuning-dataset/delhiDatacsv.csv")

# Translate title and selftext to English if not already
print("Translating non-English posts to English...")
if sarvam_client:
    # Translate titles
    df["title_english"] = df["title"].fillna("").apply(auto_translate_to_english)
    # Translate selftext
    df["selftext_english"] = df["selftext"].fillna("").apply(auto_translate_to_english)
    # Use translated versions for processing
    df["text"] = df["title_english"] + " " + df["selftext_english"]
    print(f"Translation complete. Processed {len(df)} posts.")
else:
    # Fallback if Sarvam API not available
    print("Sarvam API not available. Using original text without translation.")
    df["text"] = df["title"].fillna("") + " " + df["selftext"].fillna("")

print("Detecting language for filtering...")
DetectorFactory.seed = 0
df["language"] = df["text"].apply(lambda x: detect(x) if x.strip() else "unknown")

# Keep only English posts (after translation, most should be English)
initial_count = len(df)
df = df[df["language"] == "en"]
print(f"Filtered to {len(df)} English posts (from {initial_count} total)")

# Use smaller spaCy model to save memory
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])  # Disable unnecessary components
df["tokens"] = df["text"].apply(
    lambda x: [t.lemma_.lower() for t in nlp(x) if not t.is_stop and t.is_alpha]
)

# Skip entities to save memory
df["entities"] = [[] for _ in range(len(df))]

# Unload spaCy to free memory
del nlp
gc.collect()
print("Freed spaCy memory")

# -----------------------------
# 2. Embeddings
# -----------------------------
print("Generating embeddings...")
model = SentenceTransformer("all-MiniLM-L6-v2")
# Process in batches to reduce memory usage
batch_size = 32
embeddings = model.encode(df["text"].tolist(), show_progress_bar=True, batch_size=batch_size)

# Free embedding model memory
del model
gc.collect()
print("Freed SentenceTransformer memory")


# -----------------------------
# 3. Clustering (KMeans here)
# -----------------------------
print("Clustering...")
NUM_TOPICS = 15  # change based on dataset size
clustering = KMeans(n_clusters=NUM_TOPICS, random_state=42, n_init=10)
df["topic"] = clustering.fit_predict(embeddings)

# -----------------------------
# 4. Gemini Setup
# -----------------------------
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")
genai.configure(api_key=gemini_api_key)

def label_topic(cluster_id, docs):
    """Send representative docs to Gemini and ask for a topic name"""
    prompt = f"""
    You are analyzing Reddit posts from Delhi.
    Here are some example posts from cluster {cluster_id}:

    {docs}

    Please give a short, human-readable topic name (2-5 words).
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# -----------------------------
# 5. Sample docs per cluster & Label with Gemini
# -----------------------------
print("Labeling topics with Gemini...")
topic_labels = {}
representative_posts_data = {}  # Store representative posts for each topic

for cluster_id in sorted(df["topic"].unique()):
    # Get most representative posts
    cluster_docs = get_representative_posts(cluster_id, embeddings, df, max_posts=5)
    topic_labels[cluster_id] = label_topic(cluster_id, cluster_docs)
    print(f"Topic {cluster_id}: {topic_labels[cluster_id]}")
    
    # Store representative posts with full details
    mask = df["topic"] == cluster_id
    cluster_df = df[mask]
    cluster_embeddings = embeddings[mask]
    
    if len(cluster_df) > 0:
        # Compute centroid
        centroid = cluster_embeddings.mean(axis=0).reshape(1, -1)
        # Find closest posts to centroid
        distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
        sorted_idx = np.argsort(distances)
        
        # Get top 5 representative posts with full details
        representative_posts = []
        for i in sorted_idx[:5]:
            post = cluster_df.iloc[i]
            representative_posts.append({
                "text": post["text"][:300] if pd.notna(post["text"]) else "",
                "title": post["title"] if "title" in cluster_df.columns and pd.notna(post["title"]) else "",
                "permalink": post["permalink"] if "permalink" in cluster_df.columns and pd.notna(post["permalink"]) else "",
                "id": post["_id"] if "_id" in cluster_df.columns and pd.notna(post["_id"]) else ""
            })
        
        representative_posts_data[int(cluster_id)] = representative_posts

# Map labels back
df["topic_label"] = df["topic"].map(topic_labels)

# Free embeddings to save memory before saving
del embeddings
del clustering
gc.collect()
print("Freed clustering memory")

# -----------------------------
# 6. Save results
# -----------------------------
print("Saving results...")
df.to_csv("cleaned_delhiData_with_labels.csv", index=False)

# Save representative posts to a separate JSON file
import json
with open("representative_posts.json", "w") as f:
    json.dump(representative_posts_data, f, indent=2)
print("Saved representative posts to representative_posts.json")

print("\n=== Processing Complete ===")
print(df[["text", "tokens", "topic", "topic_label"]].head()) #only showing top
print("\nTopic labels:", topic_labels)
print(f"\nTotal posts: {len(df)}")
print(f"Total topics: {len(topic_labels)}")