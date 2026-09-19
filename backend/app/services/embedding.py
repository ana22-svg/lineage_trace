import numpy as np
from app.config import settings

TARGET_EMBEDDING_DIMENSIONS = 768


class EmbeddingService:
    def __init__(self):
        # Load the ONNX model only when ingestion actually needs it.
        # This keeps API startup and read-only dashboard routes lightweight.
        self._embedding_model = None

    def _model(self):
        if self._embedding_model is None:
            from fastembed import TextEmbedding
           # Line 16 in backend/app/services/embedding.py:
            model_name = (settings.EMBEDDING_MODEL or "").strip() or "BAAI/bge-small-en-v1.5"
            if "/" not in model_name:
                model_name = f"sentence-transformers/{model_name}"
            self._embedding_model = TextEmbedding(model_name=model_name)
        return self._embedding_model

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
        model = self._model()
        vector = next(model.embed([text]))
        return self._fit_vector_dimension(vector)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, TARGET_EMBEDDING_DIMENSIONS), dtype=np.float32)
        model = self._model()
        vectors = list(model.embed(texts))
        return np.vstack([self._fit_vector_dimension(vector) for vector in vectors])

embedding_service = EmbeddingService()

