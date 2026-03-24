# # utils/lazy_loader.py

# def load_embedding_model(name: str):
#     if name == "bge-m3":
#         from bge_m3_embedder import BGEM3Embedding
#         return BGEM3Embedding()
#     elif name == "sentence-transformer":
#         from sentence_transformers import SentenceTransformer
#         return SentenceTransformer("all-MiniLM-L6-v2")
#     else:
#         raise ValueError(f"[❌ Unsupported embedding model] '{name}'")


# def load_image_embedder(name: str):
#     from sentence_transformers import SentenceTransformer
#     return SentenceTransformer(name)
# utils/lazy_loader.py

def load_embedding_model(name: str):
    if name == "bge-m3":
        from bge_m3_embedder import BGEM3Embedding
        return BGEM3Embedding()
    elif name == "sentence-transformer":
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    else:
        raise ValueError(f"[❌ Unsupported embedding model] '{name}'")


def load_image_embedder(name: str):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(name)


def load_llm_model(model_name: str = "llama3"):
    """
    Lazy-loads Ollama LLM for HYDE or answer generation.
    Returns a callable: lambda prompt -> str
    """
    try:
        from ollama import Client
        client = Client()
        return lambda prompt: client.generate(model=model_name, prompt=prompt)["response"]
    except Exception as e:
        raise RuntimeError(f"[🔥 Failed to load LLM model] {e}")
