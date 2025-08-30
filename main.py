from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
from app.watcher import FolderWatcherManager
from routes import folder as folders_route

# Create DB tables
Base.metadata.create_all(bind=engine)

manager = FolderWatcherManager()
folders_route.manager = manager  # inject manager into router for start/stop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # start watchers for any already-registered active folders
    manager.start_for_all()
    try:
        yield
    finally:
        await manager.shutdown()

app = FastAPI(title="CSV Watcher API", lifespan=lifespan)

app.include_router(folders_route.router, prefix="/folders", tags=["Folders"])

@app.get("/")
def root():
    return {"status": "ok", "service": "CSV Watcher", "rule": "process previous CSV when a new one appears"}
