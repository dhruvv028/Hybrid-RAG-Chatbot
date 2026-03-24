import pandas as pd
from fuzzywuzzy import process 
from difflib import get_close_matches

# Load error knowledgebase at module-level
kb_path = "app/data/knowledge/unique.xlsx"
error_df = pd.read_excel(kb_path)

# Ensure required columns exist
REQUIRED_COLS = {"ERROR", "REASON", "RESOLUTION"}
if not REQUIRED_COLS.issubset(set(error_df.columns)):
    raise ValueError(f"Missing required columns in {kb_path}. Required: {REQUIRED_COLS}")

# Normalize for matching
error_df["ERROR_clean"] = error_df["ERROR"].astype(str).str.lower().str.strip()


def generate_answer_b(user_error: str, _: str = "") -> str:
    try:
        query = user_error.strip().lower()
        matches = get_close_matches(query, error_df["ERROR_clean"], n=1, cutoff=0.5)

        if not matches:
            return "The error is not recognized in the support database."

        matched_error = matches[0]
        match_row = error_df[error_df["ERROR_clean"] == matched_error].iloc[0]
        reason = match_row["REASON"]
        resolution = match_row["RESOLUTION"]

        return f"**Matched Error:** {match_row['ERROR']}\n\n**Reason:** {reason}\n\n**Resolution:** {resolution}"

    except Exception as e:
        print(f"[🔥 Error in generate_answer_b] {str(e)}")
        return "⚠️ Sorry, something went wrong generating the support response."