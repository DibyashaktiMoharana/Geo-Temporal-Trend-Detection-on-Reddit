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

# Load environment variables
load_dotenv()

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
df = pd.read_csv("fine-tuning-dataset/delhiDatacsv.csv")
df["text"] = df["title"].fillna("") + " " + df["selftext"].fillna("")

DetectorFactory.seed = 0
df["language"] = df["text"].apply(lambda x: detect(x) if x.strip() else "unknown")
df = df[df["language"] == "en"]

# spaCy tokens/entities (optional but useful for later)
nlp = spacy.load("en_core_web_sm")
df["tokens"] = df["text"].apply(
    lambda x: [t.lemma_.lower() for t in nlp(x) if not t.is_stop and t.is_alpha]
)
df["entities"] = df["text"].apply(
    lambda x: [(ent.text, ent.label_) for ent in nlp(x).ents]
)

# -----------------------------
# 2. Embeddings
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)


# -----------------------------
# 3. Clustering (KMeans here)
# -----------------------------
NUM_TOPICS = 15  # change based on dataset size
clustering = KMeans(n_clusters=NUM_TOPICS, random_state=42)
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
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# -----------------------------
# 5. Sample docs per cluster & Label with Gemini
# -----------------------------
topic_labels = {}
for cluster_id in sorted(df["topic"].unique()):
    # Get most representative posts
    cluster_docs = get_representative_posts(cluster_id, embeddings, df, max_posts=5)
    topic_labels[cluster_id] = label_topic(cluster_id, cluster_docs)

# Map labels back
df["topic_label"] = df["topic"].map(topic_labels)

# -----------------------------
# 6. Save results
# -----------------------------
df.to_csv("cleaned_delhiData_with_labels.csv", index=False)

print(df[["text", "tokens", "entities", "topic", "topic_label"]].head()) #only showing top
print("\nTopic labels:", topic_labels)