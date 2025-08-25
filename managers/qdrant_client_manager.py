import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, FieldCondition, MatchValue, Filter

class QdrantClientManager:
    def __init__(self, path: str = None, collection_name: str = None, dim: int = 1536):
        self.path = path or os.getenv("QDRANT_PATH", ":memory:")
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "cars")
        self.dim = dim
        self.qdrant = QdrantClient(path=self.path)
        self._init_collection()

    def _init_collection(self):
        self.qdrant.recreate_collection(collection_name=self.collection_name,
                                        vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE))

    def upsert(self, points):
        self.qdrant.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, top_k=10, query_filter=None):
        return self.qdrant.search(collection_name=self.collection_name, query_vector=query_vector, limit=top_k,
                                   query_filter=query_filter)
