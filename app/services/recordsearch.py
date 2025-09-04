import base64
import os
from sqlalchemy import text
from sqlalchemy.orm import Session


def search_record(db: Session, table_name: str, search_string: str):
    # 🔹 Build search query
    query = text(f"""
        SELECT * FROM `{table_name}`
        WHERE CONCAT_WS(' ', {", ".join(["`" + col + "`" for col in get_table_columns(db, table_name)])})
        LIKE :search
        LIMIT 10
    """)

    rows = db.execute(query, {"search": f"%{search_string}%"}).fetchall()
    if not rows:
        return []

    results = []
    for row in rows:
        row_dict = dict(row._mapping)  # ✅ Correct way in SQLAlchemy 2.x

        csv_path = row_dict.get("CsvPath")
        img_path = row_dict.get("Front-Side-Image") or row_dict.get("Front_side_Image")

        image_base64 = None
        new_image_path = None

        if csv_path and img_path:
            try:
                # Base dir = directory containing the CSV
                base_dir = os.path.dirname(csv_path)
                parent_dir = os.path.dirname(base_dir)

                # Take last 2 parts of image path
                img_relative = "\\".join(img_path.split("\\")[-2:])

                # Construct new path
                new_image_path = os.path.join(parent_dir, img_relative)

                if os.path.exists(new_image_path):
                    with open(new_image_path, "rb") as img_file:
                        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

            except Exception as e:
                print(f"⚠️ Error processing image path: {e}")

        results.append({
            "record": row_dict,
            "image_path": new_image_path,
            "image_base64": image_base64
        })

    return results



def get_table_columns(db: Session, table_name: str):
    """Fetch column names of a given table."""
    query = text(f"SHOW COLUMNS FROM `{table_name}`")
    cols = db.execute(query).fetchall()
    return [c[0] for c in cols]
