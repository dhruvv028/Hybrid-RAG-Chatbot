# rebuild_vectorstore_bot_b.py
 
import os
import shutil
import time
import pandas as pd
 
from langchain_chroma import Chroma
from langchain_core.documents import Document
from bge_m3_embedder import BGEM3Embedding
 
# ---------------- CONFIG ----------------
EXCEL_FOLDER = "./app/data/knowledge"
VECTORSTORE_DIR = "./vectorstore_bot_b"
 
REQUIRED_COLUMNS = {"ERROR", "REASON", "RESOLUTION"}
 
# ---------------- SAFETY: wipe old store ----------------
if os.path.exists(VECTORSTORE_DIR):
    shutil.rmtree(VECTORSTORE_DIR)
 
# ---------------- Embedding ----------------
embedding = BGEM3Embedding()
 
# ---------------- Excel parsing ----------------
def extract_from_excel_files(folder_path):
    rows = []
 
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith(".xlsx"):
            continue
 
        full_path = os.path.join(folder_path, fname)
        print(f"[📥 Reading] {fname}")
 
        try:
            df = pd.read_excel(full_path)
 
            if not REQUIRED_COLUMNS.issubset(set(df.columns)):
                print(f"[⚠️ Skipped] {fname} (missing required columns)")
                continue
 
            for _, row in df.iterrows():
                if pd.notna(row["ERROR"]) and pd.notna(row["REASON"]) and pd.notna(row["RESOLUTION"]):
                    rows.append({
                        "error": str(row["ERROR"]).strip(),
                        "reason": str(row["REASON"]).strip(),
                        "resolution": str(row["RESOLUTION"]).strip(),
                        "category_id": str(row.get("CategoryID", "")).strip(),
                        "source_file": fname
                    })
 
        except Exception as e:
            print(f"[❌ Failed] {fname} | {e}")
 
    return rows
 
# ---------------- Build documents ----------------
def build_documents(rows):
    docs = []
 
    for i, row in enumerate(rows):
        content = (
            f"Error: {row['error']}\n"
            f"Reason: {row['reason']}\n"
            f"Resolution: {row['resolution']}"
        )
 
        metadata = {
            "type": "support_error",
            "source": row["source_file"],
            "CategoryID": row["category_id"],
            "ERROR": row["error"],
            "REASON": row["reason"],
            "RESOLUTION": row["resolution"],
        }
 
        docs.append(Document(page_content=content, metadata=metadata))
 
    return docs
 
# ---------------- Build vectorstore ----------------
if __name__ == "__main__":
    print("[📊 Scanning Excel folder]")
    rows = extract_from_excel_files(EXCEL_FOLDER)
 
    if not rows:
        print("❌ No valid error rows found. Aborting.")
        exit(1)
 
    print(f"[📄 Total error records] {len(rows)}")
    docs = build_documents(rows)
 
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embedding
    )
 
    batch_size = 10
    for i in range(0, len(docs), batch_size):
        vectorstore.add_documents(docs[i:i + batch_size])
        print(f"[✅ Embedded {i + 1} → {min(i + batch_size, len(docs))}]")
 
    print(f"\n🎉 Support Bot vectorstore built successfully at '{VECTORSTORE_DIR}'")
 