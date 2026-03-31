import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = r"F:\University of information technology's Courses\CS431_DL\T_RAG_for_Video_Retrieval\data\vector_store\database.db"

conn = sqlite3.connect(db_path)
c = conn.cursor()

for table in ['videos', 'chunks', 'video_chunks']:
    print(f"\n=== TABLE: {table} ===")
    c.execute(f"PRAGMA table_info({table})")
    for col in c.fetchall():
        print(f"  {col}")
    c.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  Row count: {c.fetchone()[0]}")
    c.execute(f"SELECT * FROM {table} LIMIT 1")
    rows = c.fetchall()
    for row in rows:
        print(f"  Sample: {str(row)[:500]}")

conn.close()

# ChromaDB
print("\n=== CHROMA DB ===")
chroma_path = r"F:\University of information technology's Courses\CS431_DL\T_RAG_for_Video_Retrieval\data\vector_store\chroma_langchain"
chroma_db = os.path.join(chroma_path, "chroma.sqlite3")
print("Size:", os.path.getsize(chroma_db), "bytes")

conn2 = sqlite3.connect(chroma_db)
c2 = conn2.cursor()
c2.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", c2.fetchall())

c2.execute("SELECT * FROM collections")
print("Collections:", c2.fetchall())

c2.execute("SELECT COUNT(*) FROM embeddings")
print("Embedding count:", c2.fetchone()[0])

# Check embedding dimension
c2.execute("SELECT COUNT(*) FROM embedding_metadata")
print("Metadata count:", c2.fetchone()[0])

c2.execute("SELECT * FROM embedding_metadata LIMIT 3")
for row in c2.fetchall():
    print(f"  Meta sample: {str(row)[:300]}")

conn2.close()
