import numpy as np
import torch
from app.config import settings

TARGET_EMBEDDING_DIMENSIONS = 768


class EmbeddingService:
    def __init__(self):
        # Load the transformer only when ingestion actually needs it.
        # This keeps API startup and read-only dashboard routes lightweight.
        self.model = None

    def _model(self):
        if self.model is None:
            torch.set_num_threads(1)
            from sentence_transformers import SentenceTransformer
            model_name = (settings.EMBEDDING_MODEL or "").strip() or "paraphrase-multilingual-MiniLM-L12-v2"
            self.model = SentenceTransformer(model_name)
            self.model.eval()
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
        with torch.inference_mode():
            raw = self._model().encode(text, normalize_embeddings=True)
        return self._fit_vector_dimension(raw)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        with torch.inference_mode():
            vectors = self._model().encode(texts, normalize_embeddings=True, batch_size=32)
        return np.vstack([self._fit_vector_dimension(vector) for vector in vectors])

embedding_service = EmbeddingService()
