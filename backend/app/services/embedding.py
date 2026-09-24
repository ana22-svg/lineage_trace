import numpy as np
from app.config import settings

TARGET_EMBEDDING_DIMENSIONS = 768


class EmbeddingService:
    def __init__(self):
        self._embedding_model = None
    def _model(self):
        if self._embedding_model is None:
            try:
                from fastembed import TextEmbedding
                model_name = (settings.EMBEDDING_MODEL or "").strip() or "BAAI/bge-small-en-v1.5"
                self._embedding_model = ("fastembed", TextEmbedding(model_name=model_name))
            except ImportError:
                from sentence_transformers import SentenceTransformer
                model_name = (settings.EMBEDDING_MODEL or "").strip() or "paraphrase-multilingual-MiniLM-L12-v2"
                self._embedding_model = ("st", SentenceTransformer(model_name))
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
        kind, model = self._model()
        if kind == "fastembed":
            # FastEmbed returns a generator of numpy arrays
            vector = list(model.embed([text]))[0]
            # Normalize vector to unit length
            norm = np.linalg.norm(vector)
            vector = vector / norm if norm else vector
        else:
            vector = model.encode(text, normalize_embeddings=True)
        return self._fit_vector_dimension(vector)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, TARGET_EMBEDDING_DIMENSIONS), dtype=np.float32)

        model = self._model()
        vectors = list(model.embed(texts))
        return np.vstack([self._fit_vector_dimension(vector) for vector in vectors])


embedding_service = EmbeddingService()
