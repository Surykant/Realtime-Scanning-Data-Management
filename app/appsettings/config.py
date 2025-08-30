import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_NAME = os.getenv("DB_NAME", "fastapi_db")
    INGEST_CHUNK_SIZE = int(os.getenv("INGEST_CHUNK_SIZE", "5000"))
    FILE_GLOB = os.getenv("FILE_GLOB", "*.csv")

settings = Settings()
