# embeddings.py
"""
Pluggable embeddings interface.
By default this file provides a deterministic pseudo-embedding for offline testing.
Replace `embed_text` implementation with a call to OpenAI or sentence-transformers for real embeddings.
"""
import os
import numpy as np
import hashlib

# default dimension used by pseudo embedding
EMBED_DIM = int(os.getenv("EMBED_DIM", 384))

def pseudo_embed(text: str) -> np.ndarray:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vec = np.zeros(EMBED_DIM, dtype="float32")
    for i in range(EMBED_DIM):
        vec[i] = h[i % len(h)] / 255.0
    vec /= (np.linalg.norm(vec) + 1e-9)
    return vec

# Example of how you'd plug-in sentence-transformers:
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer("all-MiniLM-L6-v2")
# def embed_text(text: str) -> np.ndarray:
#     return model.encode(text, convert_to_numpy=True).astype('float32')

# Export name used by other modules
embed_text = pseudo_embed
