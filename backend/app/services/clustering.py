import numpy as np
from app.config import settings

def assign_to_cluster(new_embedding: np.ndarray, existing_clusters: list) -> dict:
    """
    Compares a new message embedding against existing cluster centroids.
    Returns the best match if above threshold, or signals to create a new cluster.
    """
    best_cluster_id = None
    highest_sim = -1.0

    for cluster in existing_clusters:
        # Compute cosine similarity
        centroid_arr = np.array(cluster.centroid, dtype=np.float32)
        norm_c = np.linalg.norm(centroid_arr)
        sim = float(np.dot(new_embedding, centroid_arr) / (norm_c if norm_c > 0 else 1.0))
        if sim > highest_sim:
            highest_sim = sim
            best_cluster_id = cluster.id

    if highest_sim > settings.CLUSTER_SIMILARITY_THRESHOLD:
        return {"assigned_cluster_id": best_cluster_id, "similarity": highest_sim, "is_new": False}
    else:
        return {"assigned_cluster_id": None, "similarity": highest_sim, "is_new": True}
