def assign_to_cluster(new_embedding: np.ndarray, existing_clusters: list) -> dict:
    best_cluster_id = None
    highest_sim = -1.0

    v_vec = np.array(new_embedding, dtype=np.float32)
    norm_v = np.linalg.norm(v_vec)

    for cluster in existing_clusters:
        c_vec = np.array(cluster.centroid, dtype=np.float32)
        norm_c = np.linalg.norm(c_vec)

        if norm_c > 0 and norm_v > 0:
            sim = float(np.dot(v_vec, c_vec) / (norm_c * norm_v))
        else:
            sim = 0.0

        if sim > highest_sim:
            highest_sim = sim
            best_cluster_id = cluster.id

    if highest_sim > settings.CLUSTER_SIMILARITY_THRESHOLD:
        return {"assigned_cluster_id": best_cluster_id, "similarity": highest_sim, "is_new": False}
    else:
        return {"assigned_cluster_id": None, "similarity": highest_sim, "is_new": True}
