# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_router import router as auth_router
from database import Base, engine
from rag.rag_router import router as rag_router


# Create all tables
Base.metadata.create_all(bind=engine)






app = FastAPI(title="Knowledge Assistant API")


# Allow frontend to access backend
app.add_middleware(
    CORS_MIDDLEWARE := CORSMiddleware,
    allow_origins=["*"],     # change later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_router)
app.include_router(rag_router, prefix="/rag")




@app.get("/")
def root():
    return {"message": "Knowledge Assistant Backend Running 🚀"}
