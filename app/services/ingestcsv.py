import os
import csv
from sqlalchemy.orm import Session
from app.database.models.folders import Upcs

BATCH_SIZE = 1  # commit every 5000 rows for speed & memory efficiency


def ingest_csv(file_path: str, db: Session, csv_sno: int):
    """
    Reads a CSV file and inserts data into the 'upcs' table in batches.
    Each file is processed only once, and rows are committed in chunks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows_to_insert = []
        total_inserted = 0

        for row in reader:
            record = Upcs(
                csvSno=row.get("Sr. No"),
                Leitho=row.get("leitho"),
                Booklet1=row.get("booklet1"),
                Subject=row.get("subject"),
                Roll=row.get("roll"),

                Q1=row.get("Q1"),
                Q2=row.get("Q2"),
                Q3=row.get("Q3"),
                Q4=row.get("Q4"),
                Q5=row.get("Q5"),
                Q6=row.get("Q6"),
                Q7=row.get("Q7"),
                Q8=row.get("Q8"),
                Q9=row.get("Q9"),
                Q10=row.get("Q10"),
                Q11=row.get("Q11"),
                Q12=row.get("Q12"),
                Q13=row.get("Q13"),
                Q14=row.get("Q14"),
                Q15=row.get("Q15"),
                Q16=row.get("Q16"),
                Q17=row.get("Q17"),
                Q18=row.get("Q18"),
                Q19=row.get("Q19"),
                Q20=row.get("Q20"),
                Q21=row.get("Q21"),
                Q22=row.get("Q22"),
                Q23=row.get("Q23"),
                Q24=row.get("Q24"),
                Q25=row.get("Q25"),
                Q26=row.get("Q26"),
                Q27=row.get("Q27"),
                Q28=row.get("Q28"),
                Q29=row.get("Q29"),
                Q30=row.get("Q30"),
                Q31=row.get("Q31"),
                Q32=row.get("Q32"),
                Q33=row.get("Q33"),
                Q34=row.get("Q34"),
                Q35=row.get("Q35"),
                Q36=row.get("Q36"),
                Q37=row.get("Q37"),
                Q38=row.get("Q38"),
                Q39=row.get("Q39"),
                Q40=row.get("Q40"),
                Q41=row.get("Q41"),
                Q42=row.get("Q42"),
                Q43=row.get("Q43"),
                Q44=row.get("Q44"),
                Q45=row.get("Q45"),
                Q46=row.get("Q46"),
                Q47=row.get("Q47"),
                Q48=row.get("Q48"),
                Q49=row.get("Q49"),
                Q50=row.get("Q50"),
                Q51=row.get("Q51"),
                Q52=row.get("Q52"),
                Q53=row.get("Q53"),
                Q54=row.get("Q54"),
                Q55=row.get("Q55"),
                Q56=row.get("Q56"),
                Q57=row.get("Q57"),
                Q58=row.get("Q58"),
                Q59=row.get("Q59"),
                Q60=row.get("Q60"),

                csvPath=file_path
            )

            rows_to_insert.append(record)

            # Bulk insert in batches
            if len(rows_to_insert) >= BATCH_SIZE:
                db.bulk_save_objects(rows_to_insert)
                db.commit()
                total_inserted += len(rows_to_insert)
                rows_to_insert.clear()

        # Insert remaining rows
        if rows_to_insert:
            db.bulk_save_objects(rows_to_insert)
            db.commit()
            total_inserted += len(rows_to_insert)

        print(f"✅ Inserted {total_inserted} rows from {file_path}")
        return total_inserted
