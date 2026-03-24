🔍 Hybrid RAG Chatbot (BGE-M3 + HYDE + BM25)

A high-performance, locally-deployable RAG chatbot using:
- BGE-M3 for dense embeddings
- BM25 for sparse retrieval
- HYDE-based query expansion
- Multi-modal support (image paths)
- Streamlit UI with bot switching

---

## 📦 Installation

```bash
git clone <repo-url>
cd <project-directory>
pip install -r requirements.txt
```

## ⚙️ Configuration

Update `.env` (or set environment variables):

```env
EMBEDDING_MODEL=bge-m3
VECTORSTORE_PATH=./vectorstore
LOG_FILE=chatbot_interactions.log
IMAGE_EMBEDDER=clip-ViT-B-32
```

## 🚀 Running the App

```bash
streamlit run app.py
```

## 🧠 Features

- [x] Toggle between Knowledge Bot / Support Bot / Both
- [x] Persistent selection and chat history
- [x] Fast hybrid retrieval with HYDE generation
- [x] Terminal + file logging for all events
- [x] Image path previews

---

## 🗂 Directory Structure

```
├── app.py
├── config.py
├── utils/
│   └── lazy_loader.py
├── generator.py
├── retriever.py
├── hybrid_retriever.py
├── generator_bot_b.py
├── retriever_bot_b.py
├── logger.py
├── rebuild_vectorstore.py
├── requirements.txt
└── README.md
```

---

## ✅ Ready to Scale
- Easy to modularize into multiple apps
- Runs entirely local (ideal for private data)
