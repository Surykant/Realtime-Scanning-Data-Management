import json
from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.connection import get_db

router = APIRouter(prefix="/tables", tags=["Dynamic Tables"])

TYPE_MAP = {
    "integer": "INT",
    "int": "INT",
    "number": "INT",
    "alphabet": "TEXT",
    "string": "VARCHAR(255)",
    "text": "TEXT",
    "bool": "TINYINT(1)",
    "boolean": "TINYINT(1)"
}

EXCLUDED_TABLES = {"folders", "processed_files", "users", "revokedtokens"}


@router.post("/create")
async def create_table_from_json(
    table_name: str = Form(...),
    table_schema: str = Form(...),  # renamed from `schema`
    db: Session = Depends(get_db)
):
    """
    Create a new table from a JSON schema.
    Example:
    table_schema = [
      {"slNo": "integer"},
      {"school_code": "alphabet"},
      {"frontsideimage": "alphabet"}
    ]
    """
    try:
        columns = json.loads(table_schema)

        if not isinstance(columns, list) or not columns:
            raise HTTPException(status_code=400, detail="Invalid schema format")

        col_defs = []
        for col in columns:
            for col_name, col_type in col.items():
                sql_type = TYPE_MAP.get(col_type.lower())
                if not sql_type:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported type '{col_type}' for column '{col_name}'"
                    )
                col_defs.append(f"`{col_name}` {sql_type}")

        # Add system columns
        col_defs.extend([
            "`ScannerID` INT",
            "`Processed` TINYINT(1) DEFAULT 0",
            "`CreatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP",
            "`CsvPath` VARCHAR(1024)"
        ])

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
            "message": f"Table `{table_name}` created with {len(columns)} custom columns + system columns"
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