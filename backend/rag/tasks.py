# tasks.py
"""
Celery tasks:
- process_file: extract text from uploaded bytes, store Document and Chunks in DB,
                then enqueue ingest_document to create embeddings and insert into FAISS.
- ingest_document: read chunks from DB, embed them, and add to vectorstore.
"""
# import io
# import uuid
# import time
# from rag.celery_app import celery
# from rag.db import SessionLocal, Document, Chunk
# from rag.chunker import chunk_text
# from rag.vectorstore import vstore
# from rag.embeddings import embed_text
# import pdfplumber

# @celery.task(name="rag.tasks.process_file")
# def process_file(content_bytes, filename: str ,user_id:int):
#     """
#     1. Extract text (PDF-aware)
#     2. Persist Document row
#     3. Chunk text and persist Chunk rows
#     4. Enqueue ingest_document for embeddings
#     Returns doc_id and ingestion task id (if created)
#     """
#     # 1) extract text
#     text = ""
#     if filename and filename.lower().endswith(".pdf"):
#         try:
#             with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
#                 pages = []
#                 for p in pdf.pages:
#                     pages.append(p.extract_text() or "")
#                 text = "\n".join(pages)
#         except Exception as e:
#             # fallback to try utf-8 text decode
#             try:
#                 text = content_bytes.decode("utf-8")
#             except:
#                 text = ""
#     else:
#         try:
#             text = content_bytes.decode("utf-8")
#         except:
#             text = ""

#     # 2) save Document
#     doc_id = str(uuid.uuid4())
#     db = SessionLocal()
#     doc = Document(doc_id=doc_id, filename=filename or "", text=text)
#     db.add(doc)
#     db.commit()

#     # 3) chunk and save chunks
#     num_chunks = 0
#     for i, ch in enumerate(chunk_text(text or "", chunk_size=1000, overlap=200)):
#         c = Chunk(doc_id=doc_id, chunk_index=i, text=ch)
#         db.add(c)
#         num_chunks = i + 1
#     db.commit()
#     db.close()

#     # 4) enqueue ingestion task to build embeddings + vector index
#     ingest_task = ingest_document.apply_async(args=[doc_id])

#     return {"doc_id": doc_id, "chunks": num_chunks, "ingest_task_id": ingest_task.id}

# @celery.task(bind=True)
# def ingest_document(self, doc_id: str):
#     """
#     Read chunks for doc_id, embed each chunk, add to FAISS vectorstore.
#     Returns number of added vectors.
#     """
#     db = SessionLocal()
#     chunks = db.query(Chunk).filter(Chunk.doc_id == doc_id).order_by(Chunk.chunk_index).all()
#     added = 0
#     for c in chunks:
#         vec = embed_text(c.text)
#         meta = {"doc_id": doc_id, "chunk_index": c.chunk_index, "text_preview": c.text[:300]}
#         vstore.add(vec, meta)
#         added += 1
#     db.close()
#     return {"doc_id": doc_id, "added": added}


import time
import uuid
from io import BytesIO

import pdfplumber

from .celery_app import celery
from .celery_metrics import (
    CELERY_TASK_LATENCY_SECONDS,
    CELERY_TASKS_TOTAL,
    start_metrics_server,
)
from .chunker import chunk_text
from .embeddings import embed_text
from .vectorstore import vstore

start_metrics_server(port=9100)


@celery.task(bind=True)
def process_file(
    self, content_bytes: bytes, filename: str, user_id: int = None, doc_id: str = None
):

    task_name = "rag.tasks.process_file"
    start = time.time()

    if doc_id is None:
        doc_id = str(uuid.uuid4())

    # ✅ FIX: Proper content extraction
    text = ""

    try:
        if filename.lower().endswith(".pdf"):
            with pdfplumber.open(BytesIO(content_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"

        else:
            # ✅ Normal text files
            try:
                text = content_bytes.decode("utf-8")
            except:
                text = content_bytes.decode("latin1", errors="ignore")

        if not text.strip():
            raise Exception("❌ No readable text found inside document")

        # ✅ Chunking
        chunks = list(chunk_text(text, chunk_size=1000, overlap=200))

        # ✅ Save embeddings PER DOCUMENT
        for i, chunk in enumerate(chunks):
            vec = embed_text(chunk)

            meta = {
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": i,
                "text_preview": chunk[:400],
                "text": chunk,
            }

            vstore.add(vec, meta, doc_id)

        CELERY_TASKS_TOTAL.labels(task_name=task_name, status="success").inc()

        return {"doc_id": doc_id, "filename": filename, "chunks_indexed": len(chunks)}

    except Exception as e:
        # failure metric
        CELERY_TASKS_TOTAL.labels(task_name=task_name, status="failure").inc()
        raise e

    finally:
        duration = time.time() - start
        CELERY_TASK_LATENCY_SECONDS.labels(task_name=task_name).observe(duration)
