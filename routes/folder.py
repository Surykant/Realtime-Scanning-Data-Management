from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import add_folder, list_folders, deactivate_folder
from app.watcher import FolderWatcherManager

router = APIRouter()
manager: FolderWatcherManager | None = None  # will be set in main.py

class FolderIn(BaseModel):
    path: str

@router.post("/add")
def add_watch_folder(body: FolderIn, db: Session = Depends(get_db)):
    folder = add_folder(db, body.path)
    if manager:
        manager.start(folder.id, folder.path)
    return {"id": folder.id, "path": folder.path, "active": folder.active}



@router.get("/list")
def list_watch_folders(db: Session = Depends(get_db)):
    folders = list_folders(db)
    return [{"id": f.id, "path": f.path, "active": f.active} for f in folders]

@router.post("/{folder_id}/deactivate")
def deactivate_watch_folder(folder_id: int, db: Session = Depends(get_db)):
    deactivate_folder(db, folder_id)
    if manager and folder_id in manager.tasks:
        manager.stop(folder_id)
    return {"status": "deactivated", "folder_id": folder_id}
