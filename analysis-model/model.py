
import pandas as pd
from langdetect import detect, DetectorFactory
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import google.generativeai as genai  # Gemini SDK
from sklearn.metrics import pairwise_distances_argmin_min
import json
import time
import pprint
from google.api_core import exceptions

# -----------------------------
# 4. Representative posts (text + permalink)
# -----------------------------
def get_representative_posts(cluster_id, embeddings, df, max_posts=5):
    mask = df["topic"] == cluster_id
    cluster_embeddings = embeddings[mask]
    cluster_texts = df.loc[mask, "text"].tolist()
    cluster_permalinks = df.loc[mask, "permalink"].tolist()

    if len(cluster_texts) == 0:
        return []

    centroid = cluster_embeddings.mean(axis=0).reshape(1, -1)
    sorted_idx = np.argsort(np.linalg.norm(cluster_embeddings - centroid, axis=1))

    selected = []
    for i in sorted_idx[:max_posts]:
        selected.append({
            "text": cluster_texts[i][:300],  # trim to avoid huge prompts
            "permalink": f"https://reddit.com{cluster_permalinks[i]}"
        })
    return selected


# -----------------------------
# 1. Load & Preprocess Data
# -----------------------------
df = pd.read_csv("delhiDatacsv.csv")
df["text"] = df["title"].fillna("") + " " + df["selftext"].fillna("")

DetectorFactory.seed = 0
df["language"] = df["text"].apply(lambda x: detect(x) if x.strip() else "unknown")
df = df[df["language"] == "en"]

# spaCy tokens/entities (optional for analysis)
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
# 3. Clustering
# -----------------------------
NUM_TOPICS = 15
clustering = KMeans(n_clusters=NUM_TOPICS, random_state=42)
df["topic"] = clustering.fit_predict(embeddings)



# -----------------------------
# 5. Gemini Setup
# -----------------------------
genai.configure(api_key="API_KEY_HERE")  # Replace with your actual API key

def label_topic(cluster_id, docs):
    """Send only text snippets to Gemini"""
    formatted_docs = "\n".join([f"- {d['text']}" for d in docs])

    prompt = f"""
    You are analyzing Reddit posts from Delhi.
    Here are some example posts from cluster {cluster_id}:

    {formatted_docs}

    Please give a short, human-readable topic name (2-5 words).
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    retries = 5
    delay = 5 # seconds

    for i in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except exceptions.ResourceExhausted as e: # Catch the rate limit error
            if i < retries - 1:
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2 # Exponential backoff
            else:
                raise e # Re-raise the exception if all retries fail
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e # Re-raise other exceptions

# -----------------------------
# 6. Label clusters
# -----------------------------
topic_labels = {}
topic_representatives = {}

for cluster_id in sorted(df["topic"].unique()):
    cluster_docs = get_representative_posts(cluster_id, embeddings, df, max_posts=5)
    docs_for_gemini = cluster_docs[:2]  # only first 2 posts go to Gemini
    topic_labels[cluster_id] = label_topic(cluster_id, docs_for_gemini)
    topic_representatives[cluster_id] = cluster_docs    #texts + permalinks
    time.sleep(5)  # Increased delay to 5 seconds between requests

df["topic_label"] = df["topic"].map(topic_labels)

# -----------------------------
# 7. Save results
# -----------------------------
df.to_csv("cleaned_delhiData_with_labels.csv", index=False)



# Convert keys before dumping
topic_representatives_clean = {int(k): v for k, v in topic_representatives.items()}

# Save representatives separately (with permalinks)
with open("topic_representatives.json", "w") as f:
    json.dump(topic_representatives_clean, f, indent=2)

# -----------------------------
# 8. Checking Model OUTPUTS
# -----------------------------

# Sample of labeled data
print(df[["text", "topic", "topic_label"]].head())

# All topic labels
print("\nAll Topic Labels:")
for cluster_id, label in sorted(topic_labels.items()):
    print(f"Cluster {cluster_id}: {label}")

#  topic labels with representative posts
for cluster_id in sorted(topic_labels.keys()):
    print(f"\nCluster {cluster_id} → Topic: {topic_labels[cluster_id]}")
    print("Top representative posts:")
    for idx, post in enumerate(topic_representatives[cluster_id], 1):
        print(f"  {idx}. {post['text']}")
        print(f"     Link: {post['permalink']}")