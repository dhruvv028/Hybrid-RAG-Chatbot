import os

class Config:
    def __init__(self):
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "bge-m3")
        self.vectorstore_path = os.getenv("VECTORSTORE_PATH", "./vectorstore")
        self.log_path = os.getenv("LOG_FILE", "chatbot_interactions.log")
        self.image_model_name = os.getenv("IMAGE_EMBEDDER", "clip-ViT-B-32")

        # to support Streamlit toggle for HYDE
        self.use_hyde = os.getenv("USE_HYDE", "true").lower() == "true"