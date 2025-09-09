from sqlalchemy.orm import Session
from app.database.models.users import User
from sqlalchemy import text
from datetime import datetime
from collections import defaultdict


EXCLUDED_TABLES = {"folders", "processed_files", "users", "revokedtokens"}

def get_total_users(db: Session) -> int:
    return db.query(User).count()

def get_active_users(db: Session) -> int:
    return db.query(User).filter(User.is_active == True).count()

def get_total_data_rows(db: Session) -> int:
    tables_query = text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = DATABASE()
    """)

    result = db.execute(tables_query).fetchall()
    all_tables = [row[0] for row in result]

    target_tables = [t for t in all_tables if t not in EXCLUDED_TABLES]

    total_count = 0

    for table in target_tables:
        try:
            count_query = text(f"SELECT COUNT(*) FROM `{table}`")
            count_result = db.execute(count_query).fetchone()
            table_rows = count_result[0] if count_result else 0
            total_count += table_rows
        except Exception as e:
            print(f"Skipping table {table} due to error: {e}")

    return total_count


def get_todays_data_rows(db: Session) -> int:
    today_date = datetime.now().date().isoformat()  # Format: 'YYYY-MM-DD'

    # Get all user tables from the database
    tables_query = text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = DATABASE()
    """)
    
    result = db.execute(tables_query).fetchall()
    all_tables = [row[0] for row in result]

    target_tables = [t for t in all_tables if t not in EXCLUDED_TABLES]

    total_count = 0

    for table in target_tables:
        try:
            # Assume every user table has a 'CreatedAt' column
            count_query = text(f"""
                SELECT COUNT(*) FROM `{table}`
                WHERE DATE(`CreatedAt`) = :today_date
            """)
            count_result = db.execute(count_query, {"today_date": today_date}).fetchone()
            table_rows = count_result[0] if count_result else 0
            total_count += int(table_rows)
        except Exception as e:
            # Skip tables where 'CreatedAt' column is missing
            print(f"Skipping table {table} due to error: {e}")

    return total_count

def get_total_rows_per_scanner(
    db: Session,
    start_date: str | None = None,
    end_date: str | None = None
) -> dict:
    tables_query = text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = DATABASE()
    """)

    result = db.execute(tables_query).fetchall()
    all_tables = [row[0] for row in result]
    target_tables = [t for t in all_tables if t not in EXCLUDED_TABLES]

    scanner_counts = defaultdict(int)

    for table in target_tables:
        try:
            where_clause = ""
            params = {}

            if start_date and end_date:
                where_clause = "WHERE DATE(CreatedAt) BETWEEN :start_date AND :end_date"
                params = {"start_date": start_date, "end_date": end_date}
            elif start_date:
                where_clause = "WHERE DATE(CreatedAt) >= :start_date"
                params = {"start_date": start_date}
            elif end_date:
                where_clause = "WHERE DATE(CreatedAt) <= :end_date"
                params = {"end_date": end_date}

            count_query = text(f"""
                SELECT ScannerID, COUNT(*) as cnt FROM `{table}`
                {where_clause}
                GROUP BY ScannerID
            """)

            rows = db.execute(count_query, params).fetchall()
            for row in rows:
                scanner_id, cnt = row
                scanner_counts[scanner_id] += int(cnt)

        except Exception as e:
            print(f" Skipping table {table} due to error: {e}")

    return dict(scanner_counts)

def get_todays_rows_per_scanner(db: Session) -> dict:
    today_date = datetime.now().date().isoformat()

    tables_query = text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = DATABASE()
    """)
    
    result = db.execute(tables_query).fetchall()
    all_tables = [row[0] for row in result]
    target_tables = [t for t in all_tables if t not in EXCLUDED_TABLES]

    scanner_counts = defaultdict(int)

    for table in target_tables:
        try:
            count_query = text(f"""
                SELECT ScannerID, COUNT(*) as cnt FROM `{table}`
                WHERE DATE(CreatedAt) = :today_date
                GROUP BY ScannerID
            """)
            rows = db.execute(count_query, {"today_date": today_date}).fetchall()
            for row in rows:
                scanner_id, cnt = row
                scanner_counts[scanner_id] += int(cnt)
        except Exception as e:
            print(f" Skipping table {table} due to error: {e}")

    return dict(scanner_counts)
