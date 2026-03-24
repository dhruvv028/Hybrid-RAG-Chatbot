# multimodal_retriever.py
import os
from typing import List
from sentence_transformers import SentenceTransformer
from PIL import Image
from qwen3_embedder import Qwen3HFEmbedding
from langchain_chroma import Chroma
from sklearn.metrics.pairwise import cosine_similarity

# Load text and image embedders
text_embedder = Qwen3HFEmbedding()
image_embedder = SentenceTransformer("clip-ViT-B-32")

# Load vectorstore (must match what rebuild_vectorstore.py wrote)
vectorstore = Chroma(
    persist_directory="./vectorstore",
    embedding_function=None
)

# Fetch raw docs and metadata
raw_docs = vectorstore.get(include=["documents", "metadatas"])


def retrieve_hybrid(query: str, image_path: str = None, top_k: int = 5):
    text_vec = text_embedder.embed_query(query)
    image_vec = None

    if image_path and os.path.exists(image_path):
        try:
            img = Image.open(image_path).convert("RGB")
            image_vec = image_embedder.encode(img).tolist()
        except Exception as e:
            print(f"[⚠️ Image embed failed] {e}")

    results = []

    for doc, meta in zip(raw_docs["documents"], raw_docs["metadatas"]):
        score = 0.0

        # Get stored vectors
        text_vector = meta.get("text_vector")
        image_vector = meta.get("image_vector")

        if text_vector:
            score += cosine_similarity([text_vec], [text_vector])[0][0]

        if image_vec and image_vector:
            score += cosine_similarity([image_vec], [image_vector])[0][0]

        results.append((score, doc, meta))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    import sys
    query = input("🔎 Enter your query: ")
    hits = retrieve_hybrid(query)
    for score, doc, meta in hits:
        print(f"\n[🔥 {round(score, 4)}] {doc[:150]}...\n🖼️ Image: {meta.get('image_path')}")

