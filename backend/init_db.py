import os
import urllib.parse
from sqlalchemy import create_engine, text
from database import Base, SQLALCHEMY_DATABASE_URL
from models import *  # Ensure all models are imported

def init_db():
    print("Initializing database...")
    # Neon might have a default schema or permissions. 
    # Let's ensure pgvector is created.
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        print("Creating vector extension if not exists...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
