# # db.py
# """
# Simple SQLite database using SQLAlchemy. Contains two tables:
# - Document: raw extracted full text for each uploaded document (doc_id UUID)
# - Chunk: chunked pieces for each document
# """
# from sqlalchemy import create_engine, Column, Integer, String, Text
# from sqlalchemy.orm import declarative_base, sessionmaker
#
# # SQLite file
# engine = create_engine("sqlite:///./data/docs.db", connect_args={"check_same_thread": False})
# Base = declarative_base()
# SessionLocal = sessionmaker(bind=engine)
#
# class Document(Base):
#     __tablename__ = "documents"
#     id = Column(Integer, primary_key=True, index=True)
#     doc_id = Column(String, unique=True, index=True)
#     filename = Column(String)
#     text = Column(Text)
#
# class Chunk(Base):
#     __tablename__ = "chunks"
#     id = Column(Integer, primary_key=True, index=True)
#     doc_id = Column(String, index=True)
#     chunk_index = Column(Integer, index=True)
#     text = Column(Text)
#
# # create tables
# Base.metadata.create_all(bind=engine)
#
#

# db.py
"""
Simple SQLite database using SQLAlchemy. Contains two tables:
- Document: raw extracted full text for each uploaded document (doc_id UUID)
- Chunk: chunked pieces for each document
"""
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite file
engine = create_engine(
    "sqlite:///./data/docs.db", connect_args={"check_same_thread": False}
)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    filename = Column(String)
    text = Column(Text)


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, index=True)
    chunk_index = Column(Integer, index=True)
    text = Column(Text)


# FastAPI dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables if not present
Base.metadata.create_all(bind=engine)
