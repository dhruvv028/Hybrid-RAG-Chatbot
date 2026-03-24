from langchain_chroma import Chroma
from qwen3_embedder import Qwen3HFEmbedding
from generator import generate_answer
from langchain_core.documents import Document
from generator import generate_hypothetical_passage


# Load vectorstore
embedding = Qwen3HFEmbedding()
vectorstore = Chroma(
    persist_directory="./vectorstore",
    embedding_function=None  # Manual embedding, we use our own
)

# HYPE prompt format
HYPE_PROMPT_TEMPLATE = """
You are a helpful assistant.
Given the following query, generate a short passage that might appear in a document which answers this query.

Query: {query}

Hypothetical Passage:
"""

def retrieve_contexts_hype(query: str, k: int = 4):
    """HYPE = Hypothetical Passage Embedding"""
    try:
        # Step 1: Generate hypothetical answer
        hype_prompt = HYPE_PROMPT_TEMPLATE.format(query=query)
        hypothetical_passage = generate_hypothetical_passage(hype_prompt)
        print(f"[📘 HYPE Passage] {hypothetical_passage.strip()[:150]}...")

        # Step 2: Embed that answer using Qwen3HFEmbedding
        vector = embedding.embed_query(hypothetical_passage.strip())

        # Step 3: Retrieve similar chunks
        docs = vectorstore.similarity_search_by_vector(vector, k=k)
        return docs

    except Exception as e:
        print(f"[🔥 HYPE Retrieval Error] {e}")
        return []

# Fallback retrieval if needed
def retrieve_contexts(query: str, k: int = 4):
    try:
        vector = embedding.embed_query(query)
        return vectorstore.similarity_search_by_vector(vector, k=k)
    except Exception as e:
        print(f"[🔥 Basic Retrieval Error] {e}")
        return []

# Optional test block
if __name__ == "__main__":
    query = input("🔍 Ask a test query: ").strip()
    hits = retrieve_contexts_hype(query)
    for doc in hits:
        print("\n[📄 Chunk]", doc.page_content[:150])
        if doc.metadata.get("image_path"):
            print("[🖼️ Image Path]", doc.metadata["image_path"])
