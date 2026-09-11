import numpy as np
from app.services.clustering import assign_to_cluster
from app.config import settings

class MockCluster:
    def __init__(self, c_id, centroid):
        self.id = c_id
        self.centroid = np.array(centroid)

def test_assign_to_cluster_match():
    new_emb = np.array([1.0, 0.0, 0.0])
    clusters = [MockCluster("c1", [0.99, 0.1, 0.0])]
    
    result = assign_to_cluster(new_emb, clusters)
    assert result["assigned_cluster_id"] == "c1"
    assert not result["is_new"]
    assert result["similarity"] > settings.CLUSTER_SIMILARITY_THRESHOLD

def test_assign_to_cluster_no_match():
    new_emb = np.array([1.0, 0.0, 0.0])
    clusters = [MockCluster("c1", [0.0, 1.0, 0.0])]
    
    result = assign_to_cluster(new_emb, clusters)
    assert result["assigned_cluster_id"] is None
    assert result["is_new"]