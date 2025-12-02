# db.py
"""
PostgreSQL database using SQLAlchemy. Contains two tables:
- Document: raw extracted full text for each uploaded document (doc_id UUID)
- Chunk: chunked pieces for each document
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL connection - read from environment variable
DATABASE_URL = os.getenv("RAG_DATABASE_URL", "postgresql://myuser:root@localhost:5432/mydb")
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    filename = Column(String)
    text = Column(Text)
    user_id = Column(Integer, index=True, nullable=True)  # Added for user filtering
    created_at = Column(String, nullable=True)  # Added for sorting

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, index=True)
    chunk_index = Column(Integer, index=True)
    text = Column(Text)

# create tables
Base.metadata.create_all(bind=engine)
