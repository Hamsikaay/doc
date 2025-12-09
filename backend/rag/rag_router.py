# from fastapi import APIRouter, UploadFile, File, Depends
# import hashlib
# import redis
# from rag.celery_app import celery
# from celery.result import AsyncResult
# from pydantic import BaseModel
# from rag.tasks import process_file
# from rag.embeddings import embed_text
# from rag.vectorstore import vstore
# from rag.llm import generate_answer
# from rag.db import SessionLocal, Chunk
# from auth_dependencies import get_current_user

# router = APIRouter()

# REDIS_HOST = "localhost"
# r = redis.Redis(host=REDIS_HOST, port=6379, db=1, decode_responses=True)

# @router.post("/upload")
# async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
#     content = await file.read()
#     task = process_file.apply_async(args=[content, file.filename, user.id])
#     return {"task_id": task.id}

# @router.get("/status/{task_id}")
# def get_status(task_id: str):
#     res = AsyncResult(task_id, app=celery)
#     return {"id": task_id, "state": res.state, "result": res.result}

# class QueryIn(BaseModel):
#     question: str

# @router.post("/query")
# def query(q: QueryIn, user=Depends(get_current_user)):
#     qhash = hashlib.sha256(q.question.encode()).hexdigest()
#     cached = r.get(f"cache:query:{qhash}")

#     if cached:
#         return {"answer": cached, "cached": True}

#     qvec = embed_text(q.question)
#     hits = vstore.search(qvec, top_k=4)

#     context = "\n\n".join([h["meta"]["text_preview"] for h in hits])
#     answer = generate_answer(q.question, context)

#     r.setex(f"cache:query:{qhash}", 3600, answer)
#     return {"answer": answer, "hits": hits, "cached": False}

# @router.get("/chunk/{doc_id}/{chunk_index}")
# def get_chunk(doc_id: str, chunk_index: int, user=Depends(get_current_user)):
#     db = SessionLocal()
#     chunk = db.query(Chunk).filter(
#         Chunk.doc_id == doc_id,
#         Chunk.chunk_index == chunk_index
#     ).first()
#     db.close()

#     if not chunk:
#         return {"error": "not found"}

#     return {"doc_id": doc_id, "chunk_index": chunk_index, "text": chunk.text}

import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from celery.result import AsyncResult

from .celery_app import celery
from .tasks import process_file
from .embeddings import embed_text
from .vectorstore import vstore
from .llm import generate_answer

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()

    doc_id = str(uuid.uuid4())
    task = process_file.apply_async(args=[content, file.filename, None, doc_id])

    return {
        "task_id": task.id,
        "doc_id": doc_id,
        "filename": file.filename
    }

@router.get("/status/{task_id}")
def get_status(task_id: str):
    res = AsyncResult(task_id, app=celery)

    return {
        "id": task_id,
        "state": res.state,
        "result": res.result if res.ready() else None
    }

@router.post("/query")
def query(data: dict):
    print("Query data:", data)
    question = data.get("question")
    doc_id = data.get("doc_id")

    if not doc_id:
        raise HTTPException(400, "doc_id is required")

    qvec = embed_text(question)

    hits = vstore.search(qvec, doc_id=doc_id)

    context = "\n\n".join([h["meta"]["text"] for h in hits])

    answer = generate_answer(question, context)

    return {
        "answer": answer,
        "hits": hits,
        "doc_id": doc_id
    }
