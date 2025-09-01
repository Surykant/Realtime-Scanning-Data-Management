from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.folderoperations import add_folder, list_folders, deactivate_folder
from app.services.watcher import FolderWatcherManager
from app.services.auth import get_current_user
from app.database.models import users, folders  # make sure Folder is imported

router = APIRouter(prefix="/folders", tags=["folders"])
manager: FolderWatcherManager | None = None  # will be set in main.py


class FolderIn(BaseModel):
    path: str
    scanner_id: str
    table_name: str


@router.post("/add")
def add_watch_folder(
    body: FolderIn,
    db: Session = Depends(get_db),
    user: users.User = Depends(get_current_user),
):
    folder = add_folder(db, body.path)
    if manager:
        manager.start(folder.id, folder.path)
    return {"id": folder.id, "path": folder.path, "active": folder.active}


@router.get("/list")
def list_watch_folders(
    db: Session = Depends(get_db),
    user: users.User = Depends(get_current_user),
):
    folders = list_folders(db)
    return [{"id": f.id, "path": f.path, "active": f.active} for f in folders]


@router.post("/{folder_id}/activate")
def activate_watch_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    user: users.User = Depends(get_current_user),
):
    folder = db.query(folders.Folder).filter_by(id=folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    folder.active = True
    db.commit()

    if manager:
        manager.start(folder.id, folder.path)

    return {"status": "activated", "folder_id": folder_id}


@router.post("/{folder_id}/deactivate")
def deactivate_watch_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    user: users.User = Depends(get_current_user),   # ✅ use your User model
):
    folder = db.query(folders.Folder).filter_by(id=folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # mark inactive in DB
    folder.active = False
    db.commit()

    # stop watcher if running
    if manager:
        manager.stop(folder_id)

    return {"status": "deactivated", "folder_id": folder_id}


