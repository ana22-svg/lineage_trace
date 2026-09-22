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
                if "/" not in model_name and not model_name.startswith("BAAI/"):
                    model_name = f"BAAI/{model_name}"
                self._embedding_model = ("fastembed", TextEmbedding(model_name=model_name))
            except Exception:
                from sentence_transformers import SentenceTransformer
                model_name = (settings.EMBEDDING_MODEL or "").strip() or "paraphrase-multilingual-MiniLM-L12-v2"
                self._embedding_model = ("st", SentenceTransformer(model_name))
        return self._embedding_model

    def _fit_vector_dimension(self, vector: np.ndarray) -> np.ndarray:
        vector = np.asarray(vector, dtype=np.float32)
        # 1. Always L2-normalize the raw model output first
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        current = vector.shape[-1]
        if current == TARGET_EMBEDDING_DIMENSIONS:
            return vector
        if current > TARGET_EMBEDDING_DIMENSIONS:
            fitted = vector[:TARGET_EMBEDDING_DIMENSIONS]
            f_norm = np.linalg.norm(fitted)
            return fitted / f_norm if f_norm else fitted

        # 2. Pad normalized vector with zeros to 768 dimensions
        return np.pad(vector, (0, TARGET_EMBEDDING_DIMENSIONS - current))

    def embed(self, text: str) -> np.ndarray:
        kind, model = self._model()
        if kind == "fastembed":
            vector = list(model.embed([text]))[0]
            norm = np.linalg.norm(vector)
            vector = vector / norm if norm else vector
        else:
            vector = model.encode(text, normalize_embeddings=True)
        return self._fit_vector_dimension(vector)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, TARGET_EMBEDDING_DIMENSIONS), dtype=np.float32)

        kind, model = self._model()
        if kind == "fastembed":
            vectors = list(model.embed(texts))
        else:
            vectors = model.encode(texts, normalize_embeddings=True)

        return np.vstack([self._fit_vector_dimension(vector) for vector in vectors])


embedding_service = EmbeddingService()
