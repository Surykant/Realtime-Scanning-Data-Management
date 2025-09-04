import json
from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.connection import get_db
from pydantic import BaseModel
from app.services.recordsearch import search_record

router = APIRouter(prefix="/tables", tags=["Dynamic Tables"])

TYPE_MAP = {
    "integer": "INT",
    "int": "INT",
    "number": "INT",
    "alphabet": "TEXT",
    "string": "VARCHAR(255)",
    "text": "TEXT",
    "bool": "TINYINT(1)",
    "boolean": "TINYINT(1)",
}

EXCLUDED_TABLES = {"folders", "processed_files", "users", "revokedtokens"}


class TableSchemaRequest(BaseModel):
    table_name: str
    table_schema: list[dict[str, str]]


@router.post("/create")
async def create_table_from_json(
    body: TableSchemaRequest, db: Session = Depends(get_db)
):
    try:
        columns = body.table_schema
        table_name = body.table_name

        if not isinstance(columns, list) or not columns:
            raise HTTPException(status_code=400, detail="Invalid schema format")

        col_defs = []
        for col in columns:
            for col_name, col_type in col.items():
                sql_type = TYPE_MAP.get(col_type.lower())
                if not sql_type:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported type '{col_type}' for column '{col_name}'",
                    )
                col_defs.append(f"`{col_name}` {sql_type}")

        # Add system columns
        col_defs.extend(
            [
                "`ScannerID` TEXT",
                "`Processed` TINYINT(1) DEFAULT 0",
                "`CreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP",
                "`CsvPath` VARCHAR(1024)",
            ]
        )

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {", ".join(col_defs)}
        ) ENGINE=InnoDB;
        """

        db.execute(text(create_table_sql))
        db.commit()

        return {
            "success": True,
            "message": f"Table `{table_name}` created with {len(columns)} custom columns",
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
def get_all_tables(db: Session = Depends(get_db)):
    try:
        # Fetch all tables in the current database
        result = db.execute(text("SHOW TABLES;"))
        tables = [row[0] for row in result.fetchall()]

        # Exclude unwanted tables
        filtered = [t for t in tables if t.lower() not in EXCLUDED_TABLES]

        return {"success": True, "tables": filtered}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{table_name}")
async def delete_table(table_name: str, db: Session = Depends(get_db)):
    try:
        # Prevent deleting system tables
        if table_name.lower() in EXCLUDED_TABLES:
            raise HTTPException(
                status_code=400,
                detail=f"Deletion of system table '{table_name}' is not allowed.",
            )

        # Check if table exists
        check_sql = f"SHOW TABLES LIKE '{table_name}'"
        result = db.execute(text(check_sql)).fetchone()
        if not result:
            raise HTTPException(
                status_code=404, detail=f"Table '{table_name}' does not exist"
            )

        # Drop the table
        drop_sql = f"DROP TABLE `{table_name}`"
        db.execute(text(drop_sql))
        db.commit()

        return {
            "success": True,
            "message": f"Table `{table_name}` deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/searchrecord")
def search_in_table(
    table_name: str,
    search: str,
    db: Session = Depends(get_db)
):
    try:
        results = search_record(db, table_name, search)
        if not results:
            raise HTTPException(status_code=404, detail="No matching records found")
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))