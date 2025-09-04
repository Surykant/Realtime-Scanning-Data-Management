import os
import csv
from sqlalchemy import Table, insert
from sqlalchemy.orm import Session
from app.database.connection import Base, engine
import chardet

BATCH_SIZE = 1  # commit every 5000 rows for speed & memory efficiency


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

        print(
            f"✅ Inserted {total_inserted} rows into table `{table_name}` from {file_path}"
        )
        return total_inserted
