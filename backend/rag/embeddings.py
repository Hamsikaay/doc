# # embeddings.py
# """
# Pluggable embeddings interface.
# By default this file provides a deterministic pseudo-embedding for offline testing.
# Replace `embed_text` implementation with a call to OpenAI or sentence-transformers for real embeddings.
# """
# import os
# import numpy as np
# import hashlib

# # default dimension used by pseudo embedding
# EMBED_DIM = int(os.getenv("EMBED_DIM", 384))

# def pseudo_embed(text: str) -> np.ndarray:
#     h = hashlib.sha256(text.encode("utf-8")).digest()
#     vec = np.zeros(EMBED_DIM, dtype="float32")
#     for i in range(EMBED_DIM):
#         vec[i] = h[i % len(h)] / 255.0
#     vec /= (np.linalg.norm(vec) + 1e-9)
#     return vec

# # Example of how you'd plug-in sentence-transformers:
# # from sentence_transformers import SentenceTransformer
# # model = SentenceTransformer("all-MiniLM-L6-v2")
# # def embed_text(text: str) -> np.ndarray:
# #     return model.encode(text, convert_to_numpy=True).astype('float32')

# # Export name used by other modules
# embed_text = pseudo_embed
# embeddings.py
# import os
# import requests
# import numpy as np
# from dotenv import load_dotenv
# load_dotenv()

# HF_API_KEY = os.getenv("HF_API_KEY")

# # Use a GOOD embedding model
# EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# # NEW correct HuggingFace Router endpoint
# HF_API_URL = "https://router.huggingface.co/v1/embeddings"

# HEADERS = {
#     "Authorization": f"Bearer {HF_API_KEY}",
#     "Content-Type": "application/json"
# }

# def embed_text(text: str):
#     payload = {
#         "model": EMBEDDING_MODEL,  # REQUIRED
#         "input": text              # REQUIRED, not "inputs"
#     }

#     response = requests.post(HF_API_URL, headers=HEADERS, json=payload)

#     if response.status_code != 200:
#         raise Exception(f"HF Embedding API Error: {response.text}")

#     data = response.json()

#     # HF returns {"data": [{"embedding": [...] }]}
#     emb = data["data"][0]["embedding"]

#     return np.array(emb, dtype="float32")

# import os
# import numpy as np
# from huggingface_hub import InferenceClient
# from dotenv import load_dotenv

# load_dotenv()

# HF_TOKEN = os.getenv("HF_TOKEN")

# client = InferenceClient(
#     provider="hf-inference",
#     api_key=HF_TOKEN,
# )

# EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"

# def embed_text(text: str):
#     # HF inference API returns a single embedding directly as a list of floats
#     embedding = client.feature_extraction(
#         text,
#         model=EMBEDDING_MODEL
#     )

#     # Return as float32 np array
#     return np.array(embedding, dtype="float32")


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
