# chunker.py
"""
Simple chunking utility: yields overlapping text chunks.
"""
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    start = 0
    L = len(text)
    if L == 0:
        return
    while start < L:
        end = start + chunk_size
        yield text[start:end]
        # advance start with overlap (ensure forward progress)
        start = end - overlap if (end - overlap) > start else end
