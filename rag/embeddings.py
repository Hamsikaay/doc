# embeddings.py
"""
Real embeddings using sentence-transformers for semantic search.
"""
import os
import numpy as np

# default dimension used by all-MiniLM-L6-v2 model
EMBED_DIM = int(os.getenv("EMBED_DIM", 384))

# Initialize sentence-transformers model
try:
    from sentence_transformers import SentenceTransformer
    print("Loading sentence-transformers model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✓ Model loaded successfully!")
    
    def embed_text(text: str) -> np.ndarray:
        """Generate real semantic embeddings using sentence-transformers."""
        return model.encode(text, convert_to_numpy=True).astype('float32')
    
except ImportError:
    print("WARNING: sentence-transformers not installed. Using pseudo-embeddings.")
    print("Install with: pip install sentence-transformers")
    
    # Fallback to pseudo embeddings
    import hashlib
    def pseudo_embed(text: str) -> np.ndarray:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = np.zeros(EMBED_DIM, dtype="float32")
        for i in range(EMBED_DIM):
            vec[i] = h[i % len(h)] / 255.0
        vec /= (np.linalg.norm(vec) + 1e-9)
        return vec
    
    embed_text = pseudo_embed
