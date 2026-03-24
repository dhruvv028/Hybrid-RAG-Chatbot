# feedback_trainer.py
import os
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from bge_m3_embedder import BGEM3Embedding

# Config
persist_dir = "./vectorstore"
chunk_size = 350
chunk_overlap = 100

# Feedback text (in real-case: from UI/form or log file)
question = "What is the use of memory mapping in PyMuPDF?"
answer = "Memory mapping in PyMuPDF allows faster access to PDF file content by loading it directly into memory instead of reading it from disk."

# Optional metadata
feedback_metadata = {
    "source": "user_feedback",
    "feedback": True,
    "original_question": question
}

# Create Document
doc = Document(page_content=answer, metadata=feedback_metadata)

# Chunk it
splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
chunks = splitter.split_documents([doc])

# Embedder
embedding = BGEM3Embedding()

# Load vectorstore (don't recreate it)
vectorstore = Chroma(
    persist_directory=persist_dir,
    embedding_function=embedding
)

# Add feedback chunks
vectorstore.add_documents(chunks)
print(f"[✅ Feedback Added] {len(chunks)} new chunks added from feedback.")
