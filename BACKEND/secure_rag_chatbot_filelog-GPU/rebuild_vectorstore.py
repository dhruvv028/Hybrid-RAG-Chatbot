import os
import shutil
import fitz  # PyMuPDF for PDF image extraction
from collections import defaultdict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from bge_m3_embedder import BGEM3Embedding
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    PyMuPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredHTMLLoader,
    UnstructuredCSVLoader,
)

# Paths
knowledge_dir = "./app/data/knowledge"
image_output_dir = "./app/data/images"
vectorstore_dir = "./vectorstore"

# Clear old vectorstore before rebuild
if os.path.exists(vectorstore_dir):
    print("🧹 Clearing old vectorstore...")
    shutil.rmtree(vectorstore_dir)

os.makedirs(image_output_dir, exist_ok=True)

# Supported loaders
supported_extensions = {
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
    ".pdf": PyMuPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".pptx": UnstructuredPowerPointLoader,
    ".html": UnstructuredHTMLLoader,
    ".htm": UnstructuredHTMLLoader,
    ".csv": UnstructuredCSVLoader,
}

all_docs = []
doc_origin_map = defaultdict(list)  # Track which doc came from which file

# Load and extract
for filename in os.listdir(knowledge_dir):
    ext = os.path.splitext(filename)[1].lower()
    full_path = os.path.join(knowledge_dir, filename)
    loader_class = supported_extensions.get(ext)

    if loader_class:
        try:
            print(f"[📥 Loading] {filename}")
            loader = loader_class(full_path)
            docs = loader.load()

            for doc in docs:
                doc_origin_map[filename].append(doc)
                print(f"[🧾 Extracted from {filename}] {doc.page_content[:200].strip()}...")

            # Extract images from PDFs
            if ext == ".pdf":
                doc_pdf = fitz.open(full_path)
                for page_num in range(len(doc_pdf)):
                    page = doc_pdf.load_page(page_num)
                    pix = page.get_pixmap()
                    image_filename = f"{filename}_page_{page_num+1}.png"
                    image_path = os.path.join(image_output_dir, image_filename)
                    pix.save(image_path)

                    for doc in docs:
                        if doc.metadata.get("page") == page_num:
                            doc.metadata["image_path"] = image_filename

            all_docs.extend(docs)
        except Exception as e:
            print(f"[⚠️ Skipped] {filename} - {str(e)}")
    else:
        print(f"[❌ Unsupported file] {filename} - Skipping.")

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=100)
chunks = splitter.split_documents(all_docs)

# Track chunks per file
chunks_per_file = defaultdict(int)
for chunk in chunks:
    source_file = chunk.metadata.get("source", "UNKNOWN")
    chunks_per_file[source_file] += 1

    # Ensure image path stays just filename
    if "image_path" in chunk.metadata:
        chunk.metadata["image_path"] = os.path.basename(chunk.metadata["image_path"])

print(f"✂️ Split into {len(chunks)} chunks")

# Embedding
embedding = BGEM3Embedding()
print("📌 Embedding model in use:", embedding.model)

# Build Chroma vectorstore
vectorstore = Chroma(
    persist_directory=vectorstore_dir,
    embedding_function=embedding,
)

# Add chunks
vectorstore.add_documents(chunks)

# ⚠️ No need to call persist() — handled automatically
print(f"✅ Vectorstore built with {len(chunks)} chunks at {vectorstore_dir}")

# Quick sanity check
results = vectorstore._collection.get(include=["metadatas"], limit=3)
print("🔍 Sample metadata from Chroma:", results["metadatas"])

# Final summary
print("\n📊 Chunking Summary:")
for fname, count in chunks_per_file.items():
    print(f"   {fname}: {count} chunks")
