import numpy as np
from app.config import settings

def construct_edges(current_message, candidate_parents: list) -> dict:
    best_parent = None
    lowest_decay = float('inf')
    best_sim = 0.0

    current_emb = np.array(current_message.embedding, dtype=np.float32)
    norm_c = np.linalg.norm(current_emb)
    if norm_c > 0:
        current_emb = current_emb / norm_c

    for parent in candidate_parents:
        parent_emb = np.array(parent.embedding, dtype=np.float32)
        norm_p = np.linalg.norm(parent_emb)
        if norm_p > 0:
            parent_emb = parent_emb / norm_p

        sim = float(np.dot(current_emb, parent_emb))
        decay = 1.0 - sim

        if decay < lowest_decay:
            lowest_decay = decay
            best_parent = parent
            best_sim = sim
    if not best_parent:
        return None

    is_flagged = lowest_decay > settings.EDGE_DECAY_THRESHOLD

    return {
        "parent_id": best_parent.id,
        "child_id": current_message.id,
        "similarity_score": best_sim,
        "similarity_decay": lowest_decay,
        "is_flagged_gap": is_flagged # Never fabricate a false edge
    }
