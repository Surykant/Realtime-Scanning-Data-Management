import os
import csv
from sqlalchemy import Table, insert
from sqlalchemy.orm import Session
from app.database.connection import Base, engine

BATCH_SIZE = 1  # commit every 5000 rows for speed & memory efficiency


def ingest_csv(file_path: str, db: Session, table_name: str, scanner_id: int):
    """
    Reads a CSV file and inserts data into the given table in batches.
    Adds ScannerID and Processed fields automatically.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    # Reflect the given table from DB
    metadata = Base.metadata
    metadata.reflect(bind=engine, only=[table_name])
    if table_name not in metadata.tables:
        raise ValueError(f"Table '{table_name}' does not exist in the database")

    table: Table = metadata.tables[table_name]

    with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        rows_to_insert = []
        total_inserted = 0

        for row in reader:
            # Keep only keys that match actual table columns
            filtered_row = {
                k.strip().lower(): v for k, v in row.items()
                if k.strip().lower() in table.columns.keys()
            }

            # Add system fields
            filtered_row["scannerid"] = scanner_id
            filtered_row["processed"] = 0

            rows_to_insert.append(filtered_row)

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

        print(f"✅ Inserted {total_inserted} rows into table `{table_name}` from {file_path}")
        return total_inserted