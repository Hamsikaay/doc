
import os
import numpy as np
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN missing in .env file")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

client = InferenceClient(
    model=EMBEDDING_MODEL,
    token=HF_TOKEN
)

def embed_text(text: str) -> np.ndarray:
    result = client.feature_extraction(text)

    # ✅ CASE 1: Already numpy array (YOUR CURRENT ERROR)
    if isinstance(result, np.ndarray):
        vec = result.astype("float32")

    # ✅ CASE 2: Flat list
    elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], float):
        vec = np.array(result, dtype="float32")

    # ✅ CASE 3: Nested list
    elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
        vec = np.array(result[0], dtype="float32")

    else:
        raise Exception(f"HF returned totally unknown format: {type(result)}")

    # ✅ FINAL GUARANTEE FOR FAISS
    if vec.ndim != 1:
        raise Exception(f"Embedding still not 1D: shape={vec.shape}")

    if vec.shape[0] != 384:
        raise Exception(f"Embedding dimension mismatch: got {vec.shape[0]}, expected 384")

    return vec
