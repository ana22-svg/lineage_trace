import numpy as np
from app.config import settings

class EmbeddingService:
    def __init__(self):
        # Load the large transformer only when ingestion actually needs it.
        # This keeps API startup and read-only dashboard routes lightweight.
        self.model = None

    def _model(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self.model

    def embed(self, text: str) -> np.ndarray:
        return self._model().encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        return self._model().encode(texts, normalize_embeddings=True, batch_size=32)

embedding_service = EmbeddingService()
