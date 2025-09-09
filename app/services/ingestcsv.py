import os
import csv,shutil
from sqlalchemy import Table, insert
from sqlalchemy.orm import Session
from app.database.connection import Base, engine
import chardet,logging
from app.appsettings.config import settings

BATCH_SIZE = 1000  


def get_encoding(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read(10000)  # check first 10k bytes
    result = chardet.detect(raw_data)
    return result["encoding"]


def ingest_csv(file_path: str, db: Session, table_name: str, scanner_id: str):
    encoding = get_encoding(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    # Reflect the given table from DB
    metadata = Base.metadata
    metadata.reflect(bind=engine, only=[table_name])
    if table_name not in metadata.tables:
        raise ValueError(f"Table '{table_name}' does not exist in the database")

    table: Table = metadata.tables[table_name]

    # Build a mapping of normalized DB columns
    col_map = {col.lower().replace(" ", "_"): col for col in table.columns.keys()}

    with open(file_path, mode="r", newline="", encoding=encoding, errors="ignore") as csvfile:
        reader = csv.DictReader(csvfile)

        rows_to_insert = []
        total_inserted = 0

        for row in reader:
            mapped_row = {}

            for k, v in row.items():
                norm_key = k.strip().lower().replace(" ", "_")
                if norm_key in col_map:
                    mapped_row[col_map[norm_key]] = v

            # Add system fields
            mapped_row["ScannerID"] = scanner_id
            mapped_row["Processed"] = 0
            mapped_row["CsvPath"] = file_path

            rows_to_insert.append(mapped_row)

            if len(rows_to_insert) >= BATCH_SIZE:
                db.execute(insert(table), rows_to_insert)
                db.commit()
                total_inserted += len(rows_to_insert)
                rows_to_insert.clear()

        # Insert remaining rows
        if rows_to_insert:
            db.execute(insert(table), rows_to_insert)
            db.commit()
            total_inserted += len(rows_to_insert)

        logging.info(
            f"Inserted {total_inserted} rows into table `{table_name}` from {file_path}"
        )
    try:
        filename = os.path.basename(file_path)
        parent_folder = os.path.basename(os.path.dirname(file_path))  

        relative_part = os.path.join(parent_folder, filename)  
        
        dest_path = os.path.join(settings.COPY_FILE_PATH, relative_part)
        dest_dir = os.path.dirname(dest_path)
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(file_path, dest_path)

        logging.info(f"CSV copied to {dest_path}")

    except Exception as e:
        logging.error(f"Failed to copy CSV: {e}")
        
    return total_inserted
