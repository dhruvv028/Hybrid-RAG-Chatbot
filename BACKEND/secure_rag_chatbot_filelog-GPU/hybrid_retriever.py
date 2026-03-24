# # hybrid_retriever.py
# from langchain_chroma import Chroma
# from langchain_core.documents import Document
# from langchain_community.retrievers import BM25Retriever
# from bge_m3_embedder import BGEM3Embedding
# from generator import generate_hypothetical_passage
# from typing import List, Tuple
# import numpy as np
# import re
# # ---------------------------
# # Configurable parameters
# # ---------------------------
# MIN_SCORE = 0.35   # minimum hybrid score for valid docs
# MIN_TOKENS = 15    # minimum token count per doc
# HYDE_DOMAIN_TERMS = ["transaction", "account", "payment", "credit", "authorization"]

# # ---------------------------
# # Embedding
# # ---------------------------
# embedding = BGEM3Embedding()

# # ---------------------------
# # Utility functions
# # ---------------------------
# def hybrid_score(dense_score, sparse_score, alpha=0.65):
#     return alpha * dense_score + (1 - alpha) * sparse_score

# def is_domain_query(query: str) -> bool:
#     return any(term in query.lower() for term in HYDE_DOMAIN_TERMS)


# # ---------------------------
# # Intent detection
# # ---------------------------
# ELABORATE_TRIGGERS = ["elaborate", "explain all", "all draft", "full details", "everything about draft"]

# def is_elaboration_query(query: str) -> bool:
#     q = query.lower()
#     return any(trigger in q for trigger in ELABORATE_TRIGGERS)

# def filter_exact_match(results, query: str):
#     """Keep only docs that contain the exact query phrase."""
#     key_term = query.lower().strip()
#     filtered = []
#     pattern = re.compile(rf"\b{re.escape(key_term)}\b", re.IGNORECASE)
#     for s, t, m in results:
#         if pattern.search(t.lower()):
#             filtered.append((s, t, m))
#     return filtered if filtered else results  # fallback to original if nothing matches


# # ---------------------------
# # Retrieval function
# # ---------------------------
# def retrieve_hybrid(query: str, k: int = 5, use_hyde: bool = False, bot: str = "A") -> List[Tuple[float, str, dict]]:
#     try:
#         # ---------------------------
#         # Optional HYDE (domain-gated)
#         # ---------------------------
#         if use_hyde and bot != "B" and is_domain_query(query):
#             hype_prompt = f"You are a helpful assistant. Generate a short passage that answers this query:\n\nQuery: {query}\n\nHypothetical Passage:"
#             query = generate_hypothetical_passage(hype_prompt)
#             print("[🧠 HYDE Query]", query[:100])

#         # ---------------------------
#         # Vectorstore selection
#         # ---------------------------
#         vectorstore_path = "./vectorstore" if bot == "A" else "./vectorstore_bot_b"
#         dense_store = Chroma(
#             persist_directory=vectorstore_path,
#             embedding_function=embedding
#         )

#         # Defensive: fetch docs
#         chroma_data = dense_store.get()
#         raw_docs = chroma_data.get("documents", [])
#         raw_meta = chroma_data.get("metadatas", [])
#         if not raw_docs:
#             print(f"[⚠️ No documents found in {vectorstore_path}]")
#             return []

#         # ---------------------------
#         # Sparse side
#         # ---------------------------
#         bm25_docs = [
#             Document(page_content=text, metadata=meta if isinstance(meta, dict) else {})
#             for text, meta in zip(raw_docs, raw_meta)
#         ]
#         sparse_store = BM25Retriever.from_documents(bm25_docs)

#         # ---------------------------
#         # Dense + sparse retrieval
#         # ---------------------------
#         dense_results = dense_store.similarity_search_with_score(query, k=k)
#         dense_dict = {doc.page_content: (score, doc.metadata) for doc, score in dense_results}
#         sparse_results = sparse_store.invoke(query)
#         sparse_dict = {doc.page_content: doc.metadata for doc in sparse_results}

#         # ---------------------------
#         # Hybrid scoring & filtering
#         # ---------------------------
#         all_texts = list(set(dense_dict.keys()) | set(sparse_dict.keys()))
#         results = []
#         for text in all_texts:
#             dense_score, dense_meta = dense_dict.get(text, (0.0, {}))
#             sparse_meta = sparse_dict.get(text, {})
#             metadata = {**dense_meta, **sparse_meta}
#             score = hybrid_score(dense_score, 1.0 if text in sparse_dict else 0.0)
#             results.append((score, text, metadata))

#         # Filter low-quality docs
#         filtered = [
#             (s, t, m)
#             for (s, t, m) in results
#             if s >= MIN_SCORE and len(t.split()) >= MIN_TOKENS
#         ]

#         if not filtered:
#             return []


#         # Optional debug
#         print("\n[🔎 Hybrid Results]")
#         for s, t, m in sorted(filtered, key=lambda x: x[0], reverse=True)[:k]:
#             print(f"Score={s:.3f} | Snippet={t[:80]}...")

#         sorted_results = sorted(filtered, key=lambda x: x[0], reverse=True)[:k]

#         # Intent-aware filtering
#         if not is_elaboration_query(query):
#             sorted_results = filter_exact_match(sorted_results, query)
#             print("[🎯 Mode] Narrow (exact match only)")
#         else:
#             print("[🎯 Mode] Elaborate (returning all related terms)")

#         return sorted_results


#     except Exception as e:
#         print(f"[🔥 Retrieval failed] {e}")
#         return []
# ---------------------------
# Advanced Hybrid Retriever
# ---------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
# from langchain_chroma import Chroma
# from langchain_core.documents import Document
# from langchain_community.retrievers import BM25Retriever
# from bge_m3_embedder import BGEM3Embedding
# from generator import generate_hypothetical_passage
# from typing import List, Tuple
# import numpy as np
# import re

# # ---------------------------
# # Config
# # ---------------------------
# MIN_SCORE = 0.35
# MIN_TOKENS = 15
# HYDE_DOMAIN_TERMS = ["transaction", "account", "payment", "credit", "authorization"]
# ELABORATE_TRIGGERS = ["elaborate", "explain all", "all draft", "full details", "everything about draft"]

# embedding = BGEM3Embedding()

# # ---------------------------
# # Utilities
# # ---------------------------
# def hybrid_score(dense_score, sparse_score, alpha=0.65):
#     return alpha * dense_score + (1 - alpha) * sparse_score

# def is_domain_query(query: str) -> bool:
#     return any(term in query.lower() for term in HYDE_DOMAIN_TERMS)

# def is_elaboration_query(query: str) -> bool:
#     q = query.lower()
#     return any(trigger in q for trigger in ELABORATE_TRIGGERS)

# def filter_exact_match(results, query: str):
#     """Keep only docs that contain the exact query phrase."""
#     key_term = query.lower().strip()
#     pattern = re.compile(rf"\b{re.escape(key_term)}\b", re.IGNORECASE)
#     filtered = []
#     for s, t, m in results:
#         if pattern.search(t.lower()):
#             filtered.append((s, t, m))
#     return filtered if filtered else results  # fallback if nothing matches

# # ---------------------------
# # Retrieval function
# # ---------------------------
# def retrieve_hybrid(query: str, k: int = 5, use_hyde: bool = False, bot: str = "A",
#                     reranker=None) -> List[Tuple[float, str, dict]]:
#     """
#     Retrieves top-k documents based on hybrid scoring, entity filtering, and intent detection.
#     Optional `reranker` can be a callable that takes [(score, text, meta), ...] and re-scores.
#     """
#     try:
#         # ---------------------------
#         # Optional HYDE (domain-gated)
#         # ---------------------------
#         if use_hyde and bot != "B" and is_domain_query(query):
#             hype_prompt = f"You are a helpful assistant. Generate a short passage that answers this query:\n\nQuery: {query}\n\nHypothetical Passage:"
#             query = generate_hypothetical_passage(hype_prompt)
#             print("[🧠 HYDE Query]", query[:100])

#         # ---------------------------
#         # Vectorstore selection
#         # ---------------------------
#         vectorstore_path = "./vectorstore" if bot == "A" else "./vectorstore_bot_b"
#         dense_store = Chroma(
#             persist_directory=vectorstore_path,
#             embedding_function=embedding
#         )

#         # Defensive fetch
#         chroma_data = dense_store.get()
#         raw_docs = chroma_data.get("documents", [])
#         raw_meta = chroma_data.get("metadatas", [])
#         if not raw_docs:
#             print(f"[⚠️ No documents found in {vectorstore_path}]")
#             return []

#         # ---------------------------
#         # Sparse side
#         # ---------------------------
#         bm25_docs = [
#             Document(page_content=text, metadata=meta if isinstance(meta, dict) else {})
#             for text, meta in zip(raw_docs, raw_meta)
#         ]
#         sparse_store = BM25Retriever.from_documents(bm25_docs)

#         # ---------------------------
#         # Dense + sparse retrieval
#         # ---------------------------
#         dense_results = dense_store.similarity_search_with_score(query, k=k*2)
#         dense_dict = {doc.page_content: (score, doc.metadata) for doc, score in dense_results}
#         sparse_results = sparse_store.invoke(query)
#         sparse_dict = {doc.page_content: doc.metadata for doc in sparse_results}

#         # Merge results
#         all_texts = list(set(dense_dict.keys()) | set(sparse_dict.keys()))
#         results = []
#         for text in all_texts:
#             dense_score, dense_meta = dense_dict.get(text, (0.0, {}))
#             sparse_meta = sparse_dict.get(text, {})
#             metadata = {**dense_meta, **sparse_meta}
#             score = hybrid_score(dense_score, 1.0 if text in sparse_dict else 0.0)
#             results.append((score, text, metadata))

#         # Filter low-quality docs
#         filtered = [
#             (s, t, m)
#             for (s, t, m) in results
#             if s >= MIN_SCORE and len(t.split()) >= MIN_TOKENS
#         ]

#         if not filtered:
#             return []

#         # ---------------------------
#         # Optional Reranker
#         # ---------------------------
#         if reranker is not None:
#             filtered = reranker(filtered)

#         # ---------------------------
#         # Intent-aware filtering
#         # ---------------------------
#         sorted_results = sorted(filtered, key=lambda x: x[0], reverse=True)[:k]

#         if is_elaboration_query(query):
#             print("[🎯 Mode] Elaborate (returning all related terms)")
#         else:
#             print("[🎯 Mode] Narrow (exact match only)")
#             sorted_results = filter_exact_match(sorted_results, query)

#         # Debug logging
#         for s, t, m in sorted_results:
#             print(f"Score={s:.3f} | Snippet={t[:80]}...")

#         return sorted_results

#     except Exception as e:
#         print(f"[🔥 Retrieval failed] {e}")
#         return []
# hybrid_retriever.py
# ============================================================
# SAFE, SINGLETON-BASED HYBRID RETRIEVER
# Fixes Chroma Rust panic + SQLite corruption
# ============================================================
 # hybrid_retriever.py
# hybrid_retriever.py
# hybrid_retriever.py
 
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from bge_m3_embedder import BGEM3Embedding
from generator import generate_hypothetical_passage
from typing import List, Tuple
import threading
import re
 
# ---------------------------
# GLOBAL SAFETY LOCK (CRITICAL)
# ---------------------------
_CHROMA_LOCK = threading.Lock()
 
# ---------------------------
# Config
# ---------------------------
MIN_SCORE = 0.05
MIN_TOKENS = 5
 
HYDE_DOMAIN_TERMS = [
    "transaction",
    "claim",
    "payment",
    "remittance",
    "835"
]
 
ELABORATE_TRIGGERS = [
    "elaborate",
    "explain all",
    "full details",
    "everything about"
]
 
COMPARISON_TRIGGERS = [
    "difference between",
    "compare",
    "vs",
    "versus"
]
 
embedding = BGEM3Embedding()
 
# ---------------------------
# Utilities
# ---------------------------
def hybrid_score(dense_score, sparse_score, alpha=0.65):
    return alpha * dense_score + (1 - alpha) * sparse_score
 
 
def is_domain_query(query: str) -> bool:
    return any(term in query.lower() for term in HYDE_DOMAIN_TERMS)
 
 
def is_elaboration_query(query: str) -> bool:
    return any(t in query.lower() for t in ELABORATE_TRIGGERS)
 
 
def is_comparison_query(query: str) -> bool:
    q = query.lower()
    return any(t in q for t in COMPARISON_TRIGGERS)
 
 
def filter_exact_match(results, query: str):
    key = query.lower().strip()
    pattern = re.compile(rf"\b{re.escape(key)}\b", re.IGNORECASE)
    filtered = [(s, t, m) for s, t, m in results if pattern.search(t.lower())]
    return filtered if filtered else results
 
 
def has_multi_source_evidence(results) -> bool:
    """
    Comparison questions REQUIRE at least 2 distinct sources
    (e.g. TR3 + Companion Guide).
    """
    sources = set()
    for _, _, meta in results:
        src = meta.get("source")
        if src:
            sources.add(src)
    return len(sources) >= 2
 
 
# ---------------------------
# Retrieval
# ---------------------------
def retrieve_hybrid(
    query: str,
    k: int = 5,
    use_hyde: bool = False,
    bot: str = "A",
    reranker=None
) -> List[Tuple[float, str, dict]]:
 
    try:
        # ---------------------------
        # HYDE (Knowledge Bot only)
        # ---------------------------
        if use_hyde and bot == "A" and is_domain_query(query):
            query = generate_hypothetical_passage(
                f"Generate a short factual passage strictly from domain context:\n{query}"
            )
 
        vectorstore_path = "./vectorstore" if bot == "A" else "./vectorstore_bot_b"
 
        with _CHROMA_LOCK:
            store = Chroma(
                persist_directory=vectorstore_path,
                embedding_function=embedding
            )
            dense_results = store.similarity_search_with_score(query, k=k * 2)
 
        if not dense_results:
            return []
 
        # ---------------------------
        # SUPPORT BOT → DENSE ONLY
        # ---------------------------
        if bot == "B":
            return [
                (float(score), doc.page_content, doc.metadata or {})
                for doc, score in dense_results
                if score >= MIN_SCORE and len(doc.page_content.split()) >= MIN_TOKENS
            ][:k]
 
        # ---------------------------
        # KNOWLEDGE BOT → SAFE HYBRID
        # ---------------------------
        dense_dict = {
            doc.page_content: (score, doc.metadata or {})
            for doc, score in dense_results
        }
 
        bm25_docs = [
            Document(page_content=text, metadata=meta)
            for text, (_, meta) in dense_dict.items()
        ]
 
        sparse = BM25Retriever.from_documents(bm25_docs)
        sparse_hits = sparse.invoke(query)
        sparse_texts = {d.page_content for d in sparse_hits}
 
        results = []
        for text, (dense_score, meta) in dense_dict.items():
            score = hybrid_score(
                dense_score,
                1.0 if text in sparse_texts else 0.0
            )
            if score >= MIN_SCORE and len(text.split()) >= MIN_TOKENS:
                results.append((score, text, meta))
 
        if not results:
            return []
 
        if reranker:
            results = reranker(results)
 
        results = sorted(results, key=lambda x: x[0], reverse=True)[:k]
 
        # ---------------------------
        # 🚫 COMPARISON SAFETY GATE
        # ---------------------------
        if is_comparison_query(query):
            if not has_multi_source_evidence(results):
                print("[🛑 BLOCKED] Comparison without multi-source evidence")
                return []
 
        # ---------------------------
        # Narrow unless elaboration
        # ---------------------------
        #if not is_elaboration_query(query):
        #    results = filter_exact_match(results, query)
 
        return results
 
    except Exception as e:
        print(f"[🔥 Hybrid Retrieval Failed] {e}")
        return []
 