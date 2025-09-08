from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException


def search_record(db: Session, table_name: str, column_name: str, search_value: str):
    valid_columns = get_table_columns(db, table_name)
    if column_name not in valid_columns:
        raise ValueError(f"Column '{column_name}' does not exist in table '{table_name}'")

    query = text(f"""
        SELECT * FROM `{table_name}`
        WHERE `{column_name}` LIKE :search
        LIMIT 100
    """)

    rows = db.execute(query, {"search": f"%{search_value}%"}).fetchall()
    if not rows:
        return []

    results = []
    for row in rows:
        row_dict = dict(row._mapping)

        results.append({
            "record": row_dict
        })

    return results




def get_table_columns(db: Session, table_name: str):
    """Fetch column names of a given table."""
    query = text(f"SHOW COLUMNS FROM `{table_name}`")
    cols = db.execute(query).fetchall()
    return [c[0] for c in cols]


def get_table_columns(db: Session, table_name: str) -> list[str]:
    try:
        query = text(f"SHOW COLUMNS FROM `{table_name}`")
        cols = db.execute(query).fetchall()
        return [c[0] for c in cols]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch columns: {e}")