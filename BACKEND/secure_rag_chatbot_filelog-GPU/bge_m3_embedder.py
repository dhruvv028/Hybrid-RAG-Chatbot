# ===============================
# bge_m3_embedder.py (OFFLINE SAFE)
# ===============================
 
import os
 
# 🔒 FORCE HUGGINGFACE OFFLINE (MUST BE FIRST)
# os.environ["HF_HUB_OFFLINE"] = "1"
# os.environ["TRANSFORMERS_OFFLINE"] = "1"
# os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
 
from typing import List
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
 
 
# 🔁 CHANGE THIS PATH TO WHERE YOU STORED THE MODEL
MODEL_PATH = os.path.abspath("C:/models/bge-m3")
 
 
class BGEM3Embedding(Embeddings):
    """
    Fully offline BGE-M3 embedding loader.
    No external network calls possible.
    """
 
    def __init__(
        self,
        task: str = "query",
        device: str = None,
    ):
        """
        task:
          - "query"   → for search queries
          - "passage" → for documents
        """
        self.device = device or ("cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu")
        self.task = task
 
        # 🚫 LOCAL ONLY LOAD — NO HF CALLS
        self.model = SentenceTransformer(
            model_name_or_path=MODEL_PATH,
            device=self.device,
            cache_folder=None
        )
 
    def _encode(self, texts: List[str], task: str = None) -> List[List[float]]:
        task = task or self.task
 
        prompt = {
            "query": "Represent this query for retrieval: ",
            "passage": "Represent this passage for retrieval: ",
        }[task]
 
        to_encode = [prompt + text for text in texts]
 
        embeddings = self.model.encode(
            to_encode,
            normalize_embeddings=True,
            convert_to_tensor=False
        )
 
        return embeddings
 
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._encode(texts, task="passage")
 
    def embed_query(self, text: str) -> List[float]:
        return self._encode([text], task="query")[0]
 