import os,logging
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
    folder = add_folder(db, body.path, body.scanner_id, body.table_name)
    if manager:
        manager.start(folder.id, folder.path)
    return {"id": folder.id, "path": folder.path, "active": folder.active}


@router.get("/list")
def list_watch_folders(
    db: Session = Depends(get_db),
    user: users.User = Depends(get_current_user),
):
    folders = list_folders(db)
    return [{"id": f.id, "path": f.path, "active": f.active, "scanner_id":f.scanner_id,"table_name":f.table_name} for f in folders]


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
    user: users.User = Depends(get_current_user),  # ✅ auth
):
    folder = db.query(folders.Folder).filter_by(id=folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    if not manager or folder_id not in manager.watchers:
        raise HTTPException(status_code=400, detail="Watcher not running for this folder")

    watcher = manager.watchers[folder_id]

    # ✅ Process all remaining CSVs synchronously before stopping
    try:
        files = sorted([f for f in os.listdir(folder.path) if f.endswith(".csv")])

        for fname in files:
            file_path = os.path.join(folder.path, fname)
            if fname not in watcher.processed_files:
                watcher.process_csv(file_path)
                watcher.processed_files.add(fname)

    except Exception as e:
        logging.error(f"⚠️ Error while processing remaining files for folder {folder_id}: {e}")
    
    finally:
        # ✅ Always deactivate in DB
        folder.active = False
        db.commit()

    # ✅ Stop watcher
    manager.stop(folder_id)

    return {
        "status": "deactivated",
        "folder_id": folder_id,
        "message": "All CSVs processed and watcher stopped."
    }



@router.delete("/delete/{folder_id}")
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    user: users.User = Depends(get_current_user)
):
    # Find folder in DB
    folder = db.query(folders.Folder).filter_by(id=folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Stop watcher if running
    if manager and folder_id in manager.watchers:
        manager.watchers[folder_id].stop_flag = True
        manager.watchers.pop(folder_id, None)
        logging.info(f"🛑 Watcher stopped for folder {folder_id}")

    # Delete from DB
    db.delete(folder)
    db.commit()

    return {"success": True, "message": f"Folder deleted successfully"}

