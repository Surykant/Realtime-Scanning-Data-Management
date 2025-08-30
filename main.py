from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.connection import Base, engine
from app.services.watcher import FolderWatcherManager
from routes import folder as folder_router,auth as auth_router, user as users_router
from fastapi.middleware.cors import CORSMiddleware



# Create DB tables
Base.metadata.create_all(bind=engine)

manager = FolderWatcherManager()
folder_router.manager = manager  # inject manager into router for start/stop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # start watchers for any already-registered active folders
    manager.start_for_all()
    try:
        yield
    finally:
        await manager.shutdown()

app = FastAPI(title="Realtime Scanning Data Management", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(folder_router.router)

@app.get("/")
def root():
    return {"status": "ok"}
