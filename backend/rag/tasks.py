import time
import uuid
from io import BytesIO

import pdfplumber
from rag.db import Chunk, Document, get_db

from .celery_app import celery
from .celery_metrics import CELERY_TASK_LATENCY_SECONDS, CELERY_TASKS_TOTAL
from .chunker import chunk_text
from .embeddings import embed_text
from .vectorstore import vstore


@celery.task(bind=True)
def process_file(
    self, content_bytes: bytes, filename: str, user_id: int = None, doc_id: str = None
):
    from rag.db import Chunk, Document, SessionLocal

    task_name = "rag.tasks.process_file"
    start = time.time()

    db = SessionLocal()

    try:
        # Extract text
        text = ""

        if filename.lower().endswith(".pdf"):
            with pdfplumber.open(BytesIO(content_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        else:
            try:
                text = content_bytes.decode("utf-8")
            except:
                text = content_bytes.decode("latin1", errors="ignore")

        if not text.strip():
            raise Exception("No readable text found.")

        # 2️⃣ Save full text in Document
        doc = db.query(Document).filter(Document.doc_id == doc_id).first()
        if doc:
            doc.text = text
            db.commit()

        # 3️⃣ Chunking
        chunks = list(chunk_text(text, chunk_size=1000, overlap=200))

        for i, chunk in enumerate(chunks):
            # Create vector
            vec = embed_text(chunk)

            # Metadata
            metadata = {
                "doc_id": doc_id,
                "chunk_index": i,
                "filename": filename,
                "text": chunk,
            }

            # Save vector
            vstore.add(vec, metadata, doc_id)

            # 4️⃣ Save chunk into DB
            db.add(Chunk(doc_id=doc_id, chunk_index=i, text=chunk))

        db.commit()

        # Success
        CELERY_TASKS_TOTAL.labels(task_name=task_name, status="success").inc()

        return {"doc_id": doc_id, "filename": filename, "chunks_indexed": len(chunks)}

    except Exception as e:
        CELERY_TASKS_TOTAL.labels(task_name=task_name, status="failure").inc()
        raise e

    finally:
        db.close()
        duration = time.time() - start
        CELERY_TASK_LATENCY_SECONDS.labels(task_name=task_name).observe(duration)
