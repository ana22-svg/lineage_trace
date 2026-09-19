import numpy as np
from app.config import settings

TARGET_EMBEDDING_DIMENSIONS = 768


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

    def _fit_vector_dimension(self, vector: np.ndarray) -> np.ndarray:
        vector = np.asarray(vector, dtype=np.float32)
        current = vector.shape[-1]
        if current == TARGET_EMBEDDING_DIMENSIONS:
            return vector
        if current > TARGET_EMBEDDING_DIMENSIONS:
            fitted = vector[:TARGET_EMBEDDING_DIMENSIONS]
            norm = np.linalg.norm(fitted)
            return fitted / norm if norm else fitted
        return np.pad(vector, (0, TARGET_EMBEDDING_DIMENSIONS - current))

    def embed(self, text: str) -> np.ndarray:
        return self._fit_vector_dimension(self._model().encode(text, normalize_embeddings=True))

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        vectors = self._model().encode(texts, normalize_embeddings=True, batch_size=32)
        return np.vstack([self._fit_vector_dimension(vector) for vector in vectors])

embedding_service = EmbeddingService()
