# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_router import router as auth_router
from database import Base, engine
from rag.rag_router import router as rag_router

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Knowledge Assistant API")

# ⭐ Correct CORS setup
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,          # ❗ NOT CORS_MIDDLEWARE :=
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router, prefix="/auth")
app.include_router(rag_router, prefix="/rag")



@app.get("/")
def root():
    return {"message": "Knowledge Assistant Backend Running 🚀"}
