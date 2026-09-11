import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbeddingService:
    def __init__(self):
        # paraphrase-multilingual-mpnet-base-v2 handles 50+ languages natively
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True, batch_size=32)

embedding_service = EmbeddingService()