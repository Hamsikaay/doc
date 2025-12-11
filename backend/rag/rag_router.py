import uuid

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from rag.db import Chunk, Document, get_db
from rag.vectorstore import delete_document_from_vectorstore
from sqlalchemy.orm import Session

from .celery_app import celery
from .embeddings import embed_text
from .llm import generate_answer
from .redis_client import redis_client
from .tasks import process_file
from .utils import question_to_key
from .vectorstore import vstore

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()

    # Generate UUID for this document
    doc_id = str(uuid.uuid4())

    # 1️⃣ Save document entry immediately (empty text for now)
    doc = Document(
        doc_id=doc_id, filename=file.filename, text=""  # text will be filled by Celery
    )
    db.add(doc)
    db.commit()

    # 2️⃣ Queue Celery task
    task = process_file.apply_async(args=[content, file.filename, None, doc_id])

    return {"task_id": task.id, "doc_id": doc_id, "filename": file.filename}


@router.get("/status/{task_id}")
def get_status(task_id: str):
    res = AsyncResult(task_id, app=celery)

    return {
        "id": task_id,
        "state": res.state,
        "result": res.result if res.ready() else None,
    }

@router.get("/documents/list")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [
        {
            "doc_id": d.doc_id,
            "filename": d.filename,
            "text": d.text
        }
        for d in docs
    ]   


@router.post("/query")
def query(data: dict):
    print("Query data:", data)

    question = data.get("question")
    doc_id = data.get("doc_id")

    if not question:
        raise HTTPException(400, "question is required")

    if not doc_id:
        raise HTTPException(400, "doc_id is required")

    # ✅ 1. CREATE REDIS KEY (QUESTION + DOC ID SAFE)
    cache_key = question_to_key(f"{doc_id}:{question}")

    # ✅ 2. CHECK REDIS FIRST
    cached_answer = redis_client.get(cache_key)
    if cached_answer:
        return {
            "source": "redis_cache",
            "answer": cached_answer,
            "doc_id": doc_id,
            "hits": [],
        }

    # ✅ 3. EMBED QUESTION
    qvec = embed_text(question)

    # ✅ 4. VECTOR SEARCH
    hits = vstore.search(qvec, doc_id=doc_id)

    context = "\n\n".join([h["meta"]["text"] for h in hits])

    # ✅ 5. LLM GENERATION
    answer = generate_answer(question, context)

    # ✅ 6. STORE ANSWER IN REDIS (24 HOURS)
    redis_client.setex(cache_key, 60 * 60 * 24, answer)  # 24 hours TTL

    return {"source": "llm", "answer": answer, "hits": hits, "doc_id": doc_id}


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):

    print("DELETE CALLED WITH:", repr(doc_id))  # shows whitespace too

    docs = db.query(Document).all()
    print("DB DOC_IDS:", [repr(d.doc_id) for d in docs])

    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    print("RESULT OF QUERY:", doc)

    if not doc:
        raise HTTPException(404, "Document not found")

    # delete vectorstore
    delete_document_from_vectorstore(doc_id)

    # delete chunks
    db.query(Chunk).filter(Chunk.doc_id == doc_id).delete()

    # delete doc entry
    db.delete(doc)
    db.commit()

    return {"status": "success"}

