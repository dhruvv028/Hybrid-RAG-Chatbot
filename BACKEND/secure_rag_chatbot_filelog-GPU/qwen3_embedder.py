from typing import List
from langchain_core.embeddings import Embeddings
from transformers import AutoTokenizer, AutoModel
from transformers.utils import logging
import torch
import torch.nn.functional as F

class Qwen3HFEmbedding(Embeddings):
    def __init__(self,
                 model_name: str = "Qwen/Qwen3-Embedding-8B",
                 max_length: int = 8192,
                 task: str = "Given a web search query, retrieve relevant passages that answer the query",
                 device: str = None):

        # ✅ Suppress Hugging Face warning spam
        logging.set_verbosity_error()
        local_files_only = True  # 🔒 Force offline mode

        # 🔐 Load model/tokenizer strictly from local cache
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            padding_side="left",
            local_files_only=local_files_only
        )

        self.model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else None,
            local_files_only=local_files_only
        )

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

        self.max_length = max_length
        self.task = task

    def _last_token_pool(self, last_hidden_states, attention_mask):
        # Support left or right padding token pooling
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
        if left_padding:
            return last_hidden_states[:, -1]
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]

    def _encode(self, texts: List[str]) -> List[List[float]]:
        batch = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**batch)
            embeddings = self._last_token_pool(outputs.last_hidden_state, batch["attention_mask"])
            embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings.cpu().tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._encode(texts)

    def embed_query(self, text: str) -> List[float]:
        formatted_query = f"Instruct: {self.task}\nQuery:{text}"
        return self._encode([formatted_query])[0]
