"""
Test script to verify PostgreSQL connection for RAG module
"""
import os
import sys

# Add parent directory to path to import rag modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variable before importing
os.environ['RAG_DATABASE_URL'] = 'postgresql://myuser:root@localhost:5432/mydb'

try:
    from rag.db import engine, Base, Document, Chunk, SessionLocal
    
    print("✓ Successfully imported database modules")
    
    # Test connection
    with engine.connect() as conn:
        print("✓ Successfully connected to PostgreSQL")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✓ Successfully created tables (if they didn't exist)")
    
    # Test basic CRUD operations
    session = SessionLocal()
    try:
        # Create a test document
        test_doc = Document(
            doc_id="test-123",
            filename="test.txt",
            text="This is a test document"
        )
        session.add(test_doc)
        session.commit()
        print("✓ Successfully created test document")
        
        # Query the document
        retrieved = session.query(Document).filter_by(doc_id="test-123").first()
        if retrieved:
            print(f"✓ Successfully retrieved document: {retrieved.filename}")
        
        # Create a test chunk
        test_chunk = Chunk(
            doc_id="test-123",
            chunk_index=0,
            text="This is a test chunk"
        )
        session.add(test_chunk)
        session.commit()
        print("✓ Successfully created test chunk")
        
        # Clean up test data
        session.delete(test_chunk)
        session.delete(test_doc)
        session.commit()
        print("✓ Successfully cleaned up test data")
        
    finally:
        session.close()
    
    print("\n" + "="*50)
    print("✅ All tests passed! PostgreSQL migration successful!")
    print("="*50)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
