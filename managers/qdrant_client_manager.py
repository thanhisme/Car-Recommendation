import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

class QdrantClientManager:
    def __init__(self, path: str = None, collection_name: str = None, dim: int = 1536):
        self.path = path or os.getenv("QDRANT_PATH", "qdrant_storage/collection/cars/storage.sqlite")
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "cars")
        self.dim = dim
        self.qdrant = QdrantClient(path=self.path)
        self._init_collection()

    def _init_collection(self):
        # Create collection only if it does not exist
        try:
            collections_resp = self.qdrant.get_collections()
            existing = [c.name for c in getattr(collections_resp, "collections", [])]
            if self.collection_name not in existing:
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
                )
        except Exception:
            # Fallback: try create, ignore error if already exists
            try:
                self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.dim, distance=Distance.COSINE)
                )
            except Exception:
                pass

    def collection_has_data(self) -> bool:
        """Return True if the collection exists and has at least one point."""
        # Prefer count API; fallback to scroll 1
        try:
            count_resp = self.qdrant.count(collection_name=self.collection_name, exact=True)
            total = getattr(count_resp, "count", 0)
            return bool(total and total > 0)
        except Exception:
            try:
                scroll_res = self.qdrant.scroll(collection_name=self.collection_name, limit=1)
                points = scroll_res[0] if isinstance(scroll_res, (list, tuple)) else []
                return bool(points)
            except Exception:
                return False

    def upsert(self, points):
        self.qdrant.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, top_k=10, query_filter=None):
        return self.qdrant.search(collection_name=self.collection_name, query_vector=query_vector, limit=top_k,
                                   query_filter=query_filter)
