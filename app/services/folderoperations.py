import os
from datetime import datetime
from glob import glob
from pathlib import Path
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.database.models.processedFile import ProcessedFile
from app.database.models.folders import Folder
from app.appsettings.config import settings

def add_folder(db: Session, path: str, scanner_id: str, table_name: str) -> Folder:
    p = str(Path(path).resolve())
    folder = db.execute(select(Folder).where(Folder.path == p)).scalar_one_or_none()
    if folder:
        folder.active = True
        folder.scanner_id = scanner_id
        folder.table_name = table_name
        db.commit()
        db.refresh(folder)
        return folder

    folder = Folder(path=p, active=True, scanner_id=scanner_id, table_name=table_name)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    seed_folder_files(db, folder)
    return folder


def seed_folder_files(db: Session, folder: Folder) -> None:
    pattern = os.path.join(folder.path, settings.FILE_GLOB)
    for fp in sorted(glob(pattern)):
        upsert_file_record(db, folder.id, fp)

def upsert_file_record(db: Session, folder_id: int, full_path: str) -> ProcessedFile:
    full_path = str(Path(full_path).resolve())
    filename = Path(full_path).name
    mtime = datetime.fromtimestamp(Path(full_path).stat().st_mtime)

    pf = db.execute(
        select(ProcessedFile).where(
            ProcessedFile.folder_id == folder_id,
            ProcessedFile.full_path == full_path
        )
    ).scalar_one_or_none()

    if pf:
        # Keep earliest mtime we saw? For ordering we set to actual file mtime
        pf.mtime = mtime
        db.commit()
        db.refresh(pf)
        return pf

    pf = ProcessedFile(
        folder_id=folder_id,
        filename=filename,
        full_path=full_path,
        processed=False,
        mtime=mtime
    )
    db.add(pf)
    db.commit()
    db.refresh(pf)
    return pf

def list_folders(db: Session):
    return db.execute(select(Folder)).scalars().all()

def deactivate_folder(db: Session, folder_id: int):
    db.execute(update(Folder).where(Folder.id == folder_id).values(active=False))
    db.commit()

def mark_processed(db: Session, pf_id: int, error: str | None = None):
    db.execute(
        update(ProcessedFile).where(ProcessedFile.id == pf_id).values(
            processed=(error is None), error=error
        )
    )
    db.commit()
