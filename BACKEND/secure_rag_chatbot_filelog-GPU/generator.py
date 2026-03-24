# generator.py
 
import re
import time
from langchain_ollama import OllamaLLM as Ollama
 
# ---------------------------
# LLM Configuration
# ---------------------------
llm = Ollama(
    base_url="http://127.0.0.1:11434",
    model="llama3",
    temperature=0.0,  # ❗ ZERO creativity (mandatory for standards)
    keep_alive="10m",
    verify=False

)
 
# ---------------------------
# Utility functions
# ---------------------------
def normalize_bullets(text: str) -> str:
    text = text.replace("- ", "\n- ")
    return "\n".join([line.strip() for line in text.splitlines() if line.strip()])
 
 
def clean_markdown_bold(text: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
 
 
# ---------------------------
# Intent detection
# ---------------------------
def detect_intent(question: str) -> str:
    q = question.lower().strip()
 
    if any(k in q for k in ["difference between", "compare", "vs", "versus"]):
        return "comparison"
 
    if q.startswith(("what is", "define", "definition of")):
        return "definition"
 
    if any(k in q for k in ["how does", "how do", "process", "flow", "lifecycle"]):
        return "process"
 
    if any(k in q for k in ["list", "enumerate", "what are", "which are"]):
        return "list"
 
    if any(k in q for k in ["why", "explain", "purpose"]):
        return "explanation"
 
    if any(k in q for k in ["issue", "problem", "error", "cannot", "fails"]):
        return "scenario"
 
    return "general"
 
 
 
# ---------------------------
# HARD STANDARDS EVIDENCE CHECK (NEW)
# ---------------------------
def has_explicit_835_evidence(context: str) -> bool:
    """
    Returns True ONLY if the context explicitly supports
    835 / X12 / HIPAA standards questions.
    """
    c = context.lower()
    return (
        "asc x12" in c and
        "835" in c
    )
 
 
# ---------------------------
# Safe LLM call
# ---------------------------
def safe_invoke(prompt: str, retries: int = 1, delay: int = 1) -> str:
    for attempt in range(retries + 1):
        try:
            raw = llm.invoke(prompt)
            if raw and raw.strip():
                return raw.strip()
        except Exception as e:
            print(f"[🔥 LLM failure] {e}")
        time.sleep(delay)
 
    return "The answer is not available in the current knowledge base."
 
 
# ---------------------------
# Answer generation (STRICT + GUARDED)
# ---------------------------
def generate_answer(question: str, context: str, bot_type: str = "A") -> str:
    # ---------------------------
    # HARD EVIDENCE GATE
    # ---------------------------
    if not context.strip() or len(context.split()) < 25:
        return "The answer is not available in the current knowledge base."
 
    intent = detect_intent(question)
 
    # ---------------------------
    # SUPPORT BOT (unchanged)
    # ---------------------------
    if bot_type == "B":
        prompt = f"""
You are Support Bot.
 
Rules:
- Use ONLY the provided context.
- Do NOT invent causes or resolutions.
- If unsure, respond exactly:
  "The answer is not available in the current knowledge base."
 
Format:
<strong>Conclusion:</strong>
- Summary from context
 
<strong>Reason:</strong>
- Evidence from context
 
<strong>Resolution:</strong>
- Actionable resolution from context
 
Context:
{context}
"""
        raw = safe_invoke(prompt)
        return normalize_bullets(clean_markdown_bold(raw))
 
    # ---------------------------
    # KNOWLEDGE BOT – HARD STANDARDS GATE (CRITICAL)
    # ---------------------------
    standards_triggers = [
        "hipaa",
        "transaction set",
        "x12",
        "835",
        "isa",
        "gs",
        "envelope",
        "implementation",
        "companion guide"
    ]
 
    if any(k in question.lower() for k in standards_triggers):
        if not has_explicit_835_evidence(context):
            return "The answer is not available in the current knowledge base."
 
    # ---------------------------
    # KNOWLEDGE BOT PROMPT (NON-NEGOTIABLE)
    # ---------------------------
    prompt = f"""
[SYSTEM – NON NEGOTIABLE RULES]
 
You are a retrieval-based Knowledge Bot.
 
ABSOLUTE RULES:
- Use ONLY the provided context.
- Do NOT use prior knowledge.
- Do NOT infer, assume, or generalize.
- Do NOT expand acronyms unless expansion appears verbatim in context.
- If the answer is not explicitly supported, respond EXACTLY:
  "The answer is not available in the current knowledge base."
 
INTENT FORMATS:
- DEFINITION → One concise paragraph.
- PROCESS → Bullet steps only.
- LIST → Bullet points only.
- EXPLANATION → Short factual paragraphs.
- COMPARISON →
  - You MUST describe BOTH items explicitly.
  - Each item must be supported verbatim by context.
  - If either side is missing → respond EXACTLY:
    "The answer is not available in the current knowledge base."
- SCENARIO → Cause → Impact → Resolution (ONLY if present in context).
 
Context:
{context}
 
User Question:
{question}
 
Answer:
"""
    raw = safe_invoke(prompt)
    return normalize_bullets(clean_markdown_bold(raw))
 
 
# ---------------------------
# HYDE helper (Knowledge Bot ONLY)
# ---------------------------
def generate_hypothetical_passage(prompt: str) -> str:
    return safe_invoke(prompt)
 