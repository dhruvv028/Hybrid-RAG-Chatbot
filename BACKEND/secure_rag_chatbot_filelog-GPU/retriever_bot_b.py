import pandas as pd
import os
from difflib import get_close_matches

# Load error knowledgebase at module-level
kb_path = "app/data/knowledge/Unique.xlsx"

error_df = pd.DataFrame()

try:
    if os.path.exists(kb_path) and kb_path.endswith(".xlsx"):
        error_df = pd.read_excel(kb_path)

        # Ensure required columns exist
        REQUIRED_COLS = {"ERROR", "REASON", "RESOLUTION"}
        if not REQUIRED_COLS.issubset(set(error_df.columns)):
            raise ValueError(f"Missing required columns in {kb_path}. Required: {REQUIRED_COLS}")

        # Normalize for matching
        error_df["ERROR_clean"] = error_df["ERROR"].str.lower().str.strip()
    else:
        print(f"[⚠️ Warning] Knowledge base file not found at: {kb_path}. Bot B will return default response.")
except Exception as load_err:
    print(f"[🔥 Error loading knowledge base] {str(load_err)}")
    error_df = pd.DataFrame()

def generate_answer_b(user_error: str, _: str = "", top_n: int = 3) -> dict:
    try:
        query = user_error.strip().lower()
        matches = get_close_matches(query, error_df["ERROR_clean"], n=top_n, cutoff=0.5)

        if not matches:
            return {"matches": []}

        suggestions = []
        for match in matches:
            row = error_df[error_df["ERROR_clean"] == match].iloc[0]
            suggestions.append({
                "error": row["ERROR"],
                "reason": row["REASON"],
                "resolution": row["RESOLUTION"],
                "image": f"app/images/{row.get('IMAGE', '').strip()}" if 'IMAGE' in row else ""
            })

        return {"matches": suggestions}

    except Exception as e:
        print(f"[🔥 Error in generate_answer_b] {str(e)}")
        return {"matches": []}

# ✅ Minimal passthrough function required by main.py
def retrieve_contexts_b(user_input: str) -> str:
    return user_input
