# vectorstore.py
"""
Small FAISS-backed vector store with JSON metadata persistence.
Meta is a list of dicts where position i corresponds to FAISS index i.
This is simple and good for single-node demo; for production use RedisVector/Milvus.
"""
import faiss
import numpy as np
import os
import json

INDEX_PATH = "data/faiss.index"
META_PATH = "data/meta.json"
DIM = int(os.getenv("EMBED_DIM", 384))

class SimpleVStore:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            try:
                self.index = faiss.read_index(INDEX_PATH)
                self.meta = json.load(open(META_PATH, "r", encoding="utf-8"))
            except Exception:
                # fallback to new index
                self.index = faiss.IndexFlatL2(DIM)
                self.meta = []
        else:
            self.index = faiss.IndexFlatL2(DIM)
            self.meta = []

    def add(self, vec: np.ndarray, metadata: dict):
        # vec must be (dim, ) float32
        if vec.dtype != np.float32:
            vec = vec.astype('float32')
        # id = current number of vectors
        idx = self.index.ntotal
        self.index.add(np.array([vec]).astype('float32'))
        self.meta.append(metadata)
        # persist
        faiss.write_index(self.index, INDEX_PATH)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)
        return idx

    def search(self, vec: np.ndarray, top_k: int = 4):
        if self.index.ntotal == 0:
            return []
        if vec.dtype != np.float32:
            vec = vec.astype('float32')
        D, I = self.index.search(np.array([vec]), top_k)
        hits = []
        for dist, idx in zip(D[0], I[0]):
            if int(idx) < 0:
                continue
            hits.append({"score": float(dist), "meta": self.meta[int(idx)], "idx": int(idx)})
        return hits

# single global instance for demo
vstore = SimpleVStore()
