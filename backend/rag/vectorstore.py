import json
import os

import faiss
import numpy as np

BASE_DATA_DIR = "data"
EMBED_DIM = int(os.getenv("EMBED_DIM", 384))


def _ensure_doc_dir(doc_id: str):
    if not doc_id:
        raise ValueError("doc_id must not be None")

    folder = os.path.join(BASE_DATA_DIR, str(doc_id))
    os.makedirs(folder, exist_ok=True)
    return folder


def _paths_for_doc(doc_id: str):
    folder = _ensure_doc_dir(doc_id)
    return (
        os.path.join(folder, "faiss.index"),
        os.path.join(folder, "meta.json"),
    )


class SimpleVStore:
    def __init__(self):
        os.makedirs(BASE_DATA_DIR, exist_ok=True)

    def _load_index_and_meta(self, doc_id: str):
        index_path, meta_path = _paths_for_doc(doc_id)

        if os.path.exists(index_path) and os.path.exists(meta_path):
            index = faiss.read_index(index_path)
            meta = json.load(open(meta_path, "r", encoding="utf-8"))

            # ✅ Safety check if model changes
            if index.d != EMBED_DIM:
                index = faiss.IndexFlatL2(EMBED_DIM)
                meta = []
        else:
            index = faiss.IndexFlatL2(EMBED_DIM)
            meta = []

        return index, meta, index_path, meta_path

    # ✅ doc_id is REQUIRED (no default None anymore)
    def add(self, vec: np.ndarray, metadata: dict, doc_id: str):
        if not doc_id:
            raise ValueError("doc_id is required when adding vectors")

        if vec.dtype != np.float32:
            vec = vec.astype("float32")

        if vec.shape[0] != EMBED_DIM:
            raise ValueError(
                f"Embedding length mismatch: {vec.shape[0]} vs {EMBED_DIM}"
            )

        index, meta, index_path, meta_path = self._load_index_and_meta(doc_id)

        index.add(np.array([vec], dtype="float32"))
        meta.append(metadata)

        faiss.write_index(index, index_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def search(self, vec: np.ndarray, doc_id: str, top_k: int = 10):
        if not doc_id:
            raise ValueError("doc_id is required for searching")

        index, meta, _, _ = self._load_index_and_meta(doc_id)

        if index.ntotal == 0:
            return []

        if vec.dtype != np.float32:
            vec = vec.astype("float32")

        D, I = index.search(np.array([vec], dtype="float32"), top_k)

        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue

            results.append(
                {
                    "score": float(score),
                    "meta": meta[int(idx)],
                    "idx": int(idx),
                }
            )

        return results


# ✅ SINGLE GLOBAL INSTANCE
vstore = SimpleVStore()


def delete_document_from_vectorstore(doc_id: str):
    folder = os.path.join(BASE_DATA_DIR, str(doc_id))

    if os.path.exists(folder):
        import shutil

        shutil.rmtree(folder)
        print(f"[Vectorstore] Deleted vectorstore for doc_id={doc_id}")
