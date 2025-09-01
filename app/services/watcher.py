import os
import time
from threading import Thread
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.models.folders import Folder
from app.database.connection import SessionLocal
from app.database.models.processedFile import ProcessedFile
from app.services.ingestcsv import ingest_csv


class FolderWatcher(Thread):
    def __init__(self, folder_id: int, folder_path: str):
        super().__init__(daemon=True)
        self.folder_id = folder_id
        self.folder_path = folder_path
        self.stop_flag = False
        self.processed_files = set()

        # ✅ Load already processed files from DB at startup
        db: Session = SessionLocal()
        try:
            existing = db.query(ProcessedFile.full_path).filter_by(
                folder_id=folder_id, processed=True
            ).all()
            self.processed_files = {os.path.basename(row[0]) for row in existing}
            print(f"🔄 Loaded {len(self.processed_files)} already-processed files from DB for {self.folder_path}")
        finally:
            db.close()

    def run(self):
        print(f"👀 Watching folder: {self.folder_path}")
        while not self.stop_flag:
            try:
                # get all CSV files in the folder
                files = sorted(
                    [f for f in os.listdir(self.folder_path) if f.endswith(".csv")]
                )

                if not files:
                    time.sleep(5)
                    continue

                # process all EXCEPT the newest (last one)
                for fname in files[:-1]:
                    file_path = os.path.join(self.folder_path, fname)

                    # ✅ Double check with DB
                    db: Session = SessionLocal()
                    already_done = db.query(ProcessedFile).filter_by(
                        folder_id=self.folder_id,
                        full_path=file_path,
                        processed=True
                    ).first()
                    db.close()

                    if already_done:
                        continue  # skip, already processed

                    if fname not in self.processed_files:
                        if self.process_csv(file_path):
                            self.processed_files.add(fname)

            except Exception as e:
                print(f"⚠️ Error watching {self.folder_path}: {e}")

            time.sleep(5)  # check every 5 seconds

    def process_csv(self, file_path: str) -> bool:
        print(f"📂 Processing {file_path}")
        db: Session = SessionLocal()
        try:
            # 🔹 Fetch table_name and scanner_id from folders table
            folder = db.query(Folder).filter_by(id=self.folder_id).first()
            if not folder:
                raise ValueError(f"Folder {self.folder_id} not found in DB")

            table_name = folder.table_name   # assumes you added table_name column
            scanner_id = folder.scanner_id   # assumes you added scanner_id column

            if not table_name:
                raise ValueError(f"Folder {self.folder_id} has no table_name set")

            # 🔹 Call ingest_csv with table name + scanner_id
            total_inserted = ingest_csv(file_path, db, table_name, scanner_id)

            # ✅ Save/update record in DB
            pf = db.query(ProcessedFile).filter_by(
                folder_id=self.folder_id,
                full_path=file_path
            ).first()

            if not pf:
                pf = ProcessedFile(
                    folder_id=self.folder_id,
                    filename=os.path.basename(file_path),
                    full_path=file_path,
                    processed=True,
                    mtime=datetime.fromtimestamp(os.path.getmtime(file_path))
                )
                db.add(pf)
            else:
                pf.processed = True
                pf.mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

            db.commit()
            print(f"✅ Inserted {total_inserted} rows and marked as processed in DB: {file_path}")
            return True

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            db.rollback()
            return False
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
            print(f"✅ Started watcher for folder {folder_id}: {path}")

    def start_for_all(self):
        for folder_id, watcher in self.watchers.items():
            if not watcher.is_alive():
                watcher.start()
                print(f"▶️ Restarted watcher for folder {folder_id}")

    def stop(self, folder_id: int):
        """Stop a single watcher cleanly"""
        watcher = self.watchers.get(folder_id)
        if watcher:
            watcher.stop_flag = True
            print(f"🛑 Stopped watcher for folder {folder_id}")
            del self.watchers[folder_id]

    async def shutdown(self):
        for watcher in self.watchers.values():
            watcher.stop_flag = True
        self.watchers.clear()
        print("🛑 All watchers stopped")

