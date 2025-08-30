# watcher.py
import os
import time
from threading import Thread
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ProcessedFile
from app.ingest import ingest_csv
from datetime import datetime


class FolderWatcher(Thread):
    def __init__(self, folder_id: int, folder_path: str):
        super().__init__(daemon=True)
        self.folder_id = folder_id
        self.folder_path = folder_path
        self.stop_flag = False
        self.processed_files = set()

    def run(self):
        print(f"👀 Watching folder: {self.folder_path}")
        while not self.stop_flag:
            try:
                # get all CSV files
                files = sorted(
                    [f for f in os.listdir(self.folder_path) if f.endswith(".csv")]
                )

                if not files:
                    time.sleep(5)
                    continue

                # pick the oldest file that is NOT yet processed
                for fname in files[:-1]:  # ✅ leave the newest one unprocessed
                    if fname not in self.processed_files:
                        file_path = os.path.join(self.folder_path, fname)
                        self.process_csv(file_path)
                        self.processed_files.add(fname)

            except Exception as e:
                print(f"⚠️ Error watching {self.folder_path}: {e}")

            time.sleep(5)  # check every 5 seconds


    def process_csv(self, file_path: str):
        print(f"📂 Processing {file_path}")
        db: Session = SessionLocal()
        try:
            csv_sno = int(time.time())
            ingest_csv(file_path, db, csv_sno)

            existing = db.query(ProcessedFile).filter_by(
                folder_id=self.folder_id,
                full_path=file_path
            ).first()

            if existing:
                # ✅ Update existing record
                existing.processed = True
                existing.error = None
                existing.mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                db.commit()
                print(f"🔄 Updated ProcessedFile record for {file_path}")
            else:
                # ✅ Insert new record
                processed = ProcessedFile(
                    filename=os.path.basename(file_path),
                    full_path=file_path,
                    folder_id=self.folder_id,
                    processed=True,
                    mtime=datetime.fromtimestamp(os.path.getmtime(file_path))
                )
                db.add(processed)
                db.commit()
                print(f"✅ Inserted ProcessedFile record for {file_path}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            db.rollback()
        finally:
            db.close()






class FolderWatcherManager:
    def __init__(self):
        self.watchers: dict[int, FolderWatcher] = {}

    def start(self, folder_id: int, path: str):
        if folder_id not in self.watchers:
            watcher = FolderWatcher(folder_id, path)
            self.watchers[folder_id] = watcher
            watcher.start()
        else:
            print(f"Watcher already running for folder {folder_id}")

    def stop(self, folder_id: int):
        watcher = self.watchers.get(folder_id)
        if watcher:
            watcher.stop_flag = True
            watcher.join()
            del self.watchers[folder_id]
            print(f"🛑 Stopped watcher for folder {folder_id}")

    def start_for_all(self):
        """Start watchers for all active folders in DB at startup."""
        from app.crud import list_folders
        db: Session = SessionLocal()
        try:
            folders = list_folders(db)
            for f in folders:
                if f.active:
                    self.start(f.id, f.path)
        finally:
            db.close()

    async def shutdown(self):
        """Stop all watchers gracefully on app shutdown."""
        for folder_id in list(self.watchers.keys()):
            self.stop(folder_id)
