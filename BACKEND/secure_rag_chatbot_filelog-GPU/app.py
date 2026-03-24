from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import os
import json
import time
from uuid import uuid4
from datetime import datetime
from config import Config
from utils.lazy_loader import load_embedding_model
from hybrid_retriever import retrieve_hybrid
from generator import generate_answer
from greetings import is_greeting
from optimized_image_retriever import get_filtered_images_from_hits  

# ---------------- CHAT HISTORY LOGGER ---------------- #
def get_history_file():
    today = datetime.now().strftime("%Y-%m-%d")
    history_dir = "chat_history"
    os.makedirs(history_dir, exist_ok=True)
    return os.path.join(history_dir, f"{today}_all_chat_history.json")

def log_chat_message(chat_id, role, bot, request_text, response_text, time_taken, images=None, documents=None):
    file_path = get_history_file()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = {}

    if chat_id not in history:
        history[chat_id] = []

    history[chat_id].append({
        "role": role,
        "bot": bot,
        "request": request_text,
        "response": response_text,
        "time_taken": time_taken,
        "timestamp": datetime.now().isoformat(),
        "images": images or [],
        "documents": documents or []
    })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

# ---------------- In-memory chat sessions ---------------- #
chat_sessions = {}  # {chat_id: [{"role": "user"/"assistant", "content": "..."}]}

# ---------------- Logger Setup ---------------- #
logger = logging.getLogger("rag-bot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler = logging.FileHandler("chatbot_interactions.log", mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ---------------- Config & Embeddings ---------------- #
config = Config()
embedding_model = load_embedding_model(config.embedding_model_name)

# ---------------- FastAPI App ---------------- #
app = FastAPI(title="RAG Chatbot API")
app.mount("/static", StaticFiles(directory="app/data/images"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # ---------------- Bot Processing ---------------- #
# def process_bot(query: str, bot_type: str):
#     logger.info(f"[BOT-{bot_type}] Query: {query}")
#     hits = retrieve_hybrid(query, use_hyde=config.use_hyde, bot=bot_type)
#     logger.info(f"[BOT-{bot_type}] Hits: {len(hits)}")

#     if not hits:
#         return "No relevant answer found in the knowledge base.", []

#     context_parts = []

#     for _, doc, meta in hits:
#         context_parts.append(doc)
#         logger.info(f"[META DEBUG] {meta}")

#         if bot_type == "B":
#             # ... keep your Bot B logic unchanged ...

#             # Replace the image extraction with optimized filtering
#             relevant_images = get_filtered_images_from_hits(
#                 query=query,
#                 hits=hits,
#                 min_similarity=0.75,  # Adjust this threshold as needed
#                 max_images=3
#             )

#     # ----------------- Truth source collection -----------------
#     source_links = set()
#     for _, _, meta in hits:
#         pdf_file = meta.get("source", None)
#         page_no = meta.get("page", None)
#         if pdf_file:
#             # Make sure your PDFs are in app/data/knowledge
#             link = f"http://127.0.0.1:8000/static/knowledge/{pdf_file}"
#             if page_no:
#                 link += f"#page={page_no}"
#             display_text = f"{pdf_file}"
#             if page_no:
#                 display_text += f" - Page {page_no}"
#             source_links.add(f"[{display_text}]({link})")

#     if not context_parts:
#         return "No relevant answer found in the knowledge base.", []

#     # ----------------- Generate answer -----------------
#     context = "\n\n".join(context_parts)
#     answer = generate_answer(query, context, bot_type)

#     # Append truth sources at the end
#     if source_links:
#         answer += "\n\n**Sources:** " + ", ".join(source_links)

#     return answer, list(relevant_images)

# ---------------- Bot Processing ---------------- #
def process_bot(query: str, bot_type: str):
    logger.info(f"[BOT-{bot_type}] Query: {query}")
    hits = retrieve_hybrid(query, use_hyde=config.use_hyde, bot=bot_type)
    logger.info(f"[BOT-{bot_type}] Hits: {len(hits)}")

    if not hits:
        return "No relevant answer found in the knowledge base.", []

    context_parts = []

    for _, doc, meta in hits:
        context_parts.append(doc)
        logger.info(f"[META DEBUG] {meta}")

        if bot_type == "B":
            reason = meta.get("Reason", "").strip()
            resolution = meta.get("Resolution", "").strip()
            if reason:
                context_parts.append(f"Reason: {reason}")
            if resolution:
                context_parts.append(f"Resolution: {resolution}")

    # ✅ IMAGE FILTERING - Place OUTSIDE the loop, AFTER processing all hits
    relevant_images = get_filtered_images_from_hits(
        query=query,
        hits=hits,
        min_similarity=0.75,  # Adjust this threshold as needed
        max_images=3
    )

    # ----------------- Truth source collection -----------------
    source_links = set()
    for _, _, meta in hits:
        pdf_file = meta.get("source", None)
        #page_no = meta.get("page", None)
        if pdf_file:
            # Make sure your PDFs are in app/data/knowledge
            link = f"http://127.0.0.1:8000/static/knowledge/{pdf_file}"
            # if page_no:
            #     link += f"#page={page_no}"
            # display_text = f"{pdf_file}"
            # if page_no:
            #     display_text += f" - Page {page_no}"
            # source_links.add(f"[{display_text}]({link})")

    if not context_parts:
        return "No relevant answer found in the knowledge base.", []

    # ----------------- Generate answer -----------------
    context = "\n\n".join(context_parts)
    answer = generate_answer(query, context, bot_type)

    # Append truth sources at the end
    if source_links:
        answer += "\n\n**Sources:** " + ", ".join(source_links)

    return answer, relevant_images  # ✅ Return the filtered images

# ---------------- Pydantic Request ---------------- #
class ChatRequest(BaseModel):
    question: str
    bot_type: str = "knowledge"
    chat_id: str | None = None

# ---------------- Helper Log Function ---------------- #
LOG_FILE = os.path.join(os.path.dirname(__file__), "chatbot_interactions.log")
def log_to_file(entry: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

# ---------------- Chat Endpoint ---------------- #
@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    query = req.question.strip()
    bot = req.bot_type.lower()

    if not query:
        return JSONResponse(content={"error": "Question is required"}, status_code=400)

    chat_id = request.query_params.get("chat_id") or str(uuid4())
    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = []

    greetings = {"hi", "hello", "hey", "good morning", "good evening", "good night"}
    if query.lower() in greetings or (len(query.split()) == 1 and len(query) <= 20):
        logger.info(f"[SKIPPED] Query='{query}' | Bot={bot}")
        log_to_file(f"[SKIPPED] Query='{query}' | Bot={bot} | ChatID={chat_id}")
        return {"bot": bot.capitalize() + " Bot", "text": "⚠️ Query skipped: greeting or too short.", "images": [], "chat_id": chat_id, "skip": True}

    chat_sessions[chat_id].append({"role": "user", "content": query})
    start_time = time.time()

    if bot == "knowledge":
        text, images = process_bot(query, "A")
        chat_sessions[chat_id].append({"role": "assistant", "content": text})
    elif bot == "support":
        text, images = process_bot(query, "B")
        chat_sessions[chat_id].append({"role": "assistant", "content": text})
    elif bot == "both":
        kb_text, kb_images = process_bot(query, "A")
        sb_text, sb_images = process_bot(query, "B")
        chat_sessions[chat_id].append({"role": "assistant", "content": f"[KB] {kb_text}\n[Support] {sb_text}"})
        elapsed = round(time.time() - start_time, 2)
        log_to_file(
            f"[Both Bots] ChatID={chat_id} | Query='{query}' | Time={elapsed}s | KB='{kb_text[:80]}...' | KB_Images={kb_images} | Support='{sb_text[:80]}...' | Support_Images={sb_images}"
        )
        log_chat_message(chat_id, "user", "Knowledge Bot", query, kb_text, f"{elapsed}s", images=kb_images)
        log_chat_message(chat_id, "user", "Support Bot", query, sb_text, f"{elapsed}s", images=sb_images)
        return {"responses": [{"bot": "Knowledge Bot", "text": kb_text, "images": kb_images}, {"bot": "Support Bot", "text": sb_text, "images": sb_images}], "chat_id": chat_id}

    elapsed = round(time.time() - start_time, 2)
    log_to_file(f"[{bot.capitalize()} Bot] ChatID={chat_id} | Query='{query}' | Time={elapsed}s | Response='{text[:120]}...' | Images={images}")
    log_chat_message(chat_id, "user", bot.capitalize() + " Bot", query, text, f"{elapsed}s", images=images)
    return {"bot": bot.capitalize() + " Bot", "text": text, "images": images, "chat_id": chat_id}

# ---------------- New Chat Endpoint ---------------- #
@app.post("/new-chat")
async def new_chat():
    new_id = str(uuid4())
    chat_sessions[new_id] = []
    return {"chat_id": new_id}

# ---------------- Chat History Endpoints ---------------- #
@app.post("/chat/{chat_id}")
async def add_message(chat_id: str, message: dict):
    if chat_id not in chat_sessions:
        chat_sessions[chat_id] = []
    chat_sessions[chat_id].append(message)
    return {"status": "Message stored", "chat_id": chat_id, "messages": chat_sessions[chat_id]}

@app.get("/chat-history/{chat_id}")
async def get_chat_history(chat_id: str):
    try:
        file_path = get_history_file()
        if not os.path.exists(file_path):
            return JSONResponse(content={"error": "No history found yet"}, status_code=404)

        with open(file_path, "r", encoding="utf-8") as f:
            history = json.load(f)

        if chat_id not in history:
            return JSONResponse(content={"error": "Chat not found"}, status_code=404)

        messages = [
            {
                "id": str(idx),
                "role": msg.get("role", "user"),
                "bot": msg.get("bot", "Knowledge Bot"),
                "request": msg.get("request", ""),
                "response": msg.get("response", ""),
                "timeTaken": msg.get("time_taken", ""),
                "timestamp": msg.get("timestamp", ""),
                "images": [img if img.startswith("http") else f"http://127.0.0.1:8000/static/{img}" for img in msg.get("images", [])],
                "documents": msg.get("documents", [])
            }
            for idx, msg in enumerate(history.get(chat_id, []))
        ]
        return {"messages": messages}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ---------------- List All Chat Sessions ---------------- #
@app.get("/list-chats")
async def list_chats():
    """
    Return a list of all chat_ids and a summary (latest message & timestamp) for sidebar.
    """
    file_path = get_history_file()
    if not os.path.exists(file_path):
        return {"chats": []}

    with open(file_path, "r", encoding="utf-8") as f:
        history = json.load(f)

    chats_summary = []
    for chat_id, messages in history.items():
        for idx, msg in enumerate(messages):
            chats_summary.append({
                "id": f"{chat_id}_{idx}",  # unique id per message
                "title": msg.get("request", "New Chat"),
                "timestamp": msg.get("timestamp", ""),
                "originalPrompt": msg.get("request", "")
            })

    # sort by timestamp descending
    chats_summary.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"chats": chats_summary}

# ---------------- Run ---------------- #
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
