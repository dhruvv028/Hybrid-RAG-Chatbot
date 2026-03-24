import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings


def ingest_all_documents(directory):
    docs = []
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if filename.endswith(".pdf"):
            loader = PyMuPDFLoader(path)
            documents = loader.load()
            docs.extend(documents)

    splitter = RecursiveCharacterTextSplitter(
    chunk_size=800, chunk_overlap=100, separators=["\n\n", "\n", ".", " ", ""]
    )
    split_docs = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model="qwen3:8b")#USE QUEN2 HERE 
    Chroma.from_documents(split_docs, embedding=embeddings, persist_directory="./vectorstore")
    print("✅ Knowledgebase ingested successfully.")
    
if __name__ == "__main__":
    ingest_all_documents("..app/data/knowledge")