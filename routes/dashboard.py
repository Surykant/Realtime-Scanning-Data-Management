from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.dashboard import get_total_users, get_active_users, get_total_data_rows,get_todays_data_rows,get_total_rows_per_scanner,get_todays_rows_per_scanner
from app.services.auth import get_current_user
from app.database.models.users import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/totalusers")
def total_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = get_total_users(db)
    return {"success": True, "total_users": total}

@router.get("/activeusers")
def active_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    active = get_active_users(db)
    return {"success": True, "active_users": active}

@router.get("/totalfilescanned")
def total_data_rows(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_rows = get_total_data_rows(db)
    return {"success": True, "total_data_rows": total_rows}
    

@router.get("/todaysfilescanned")
def todays_data_rows(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_rows = get_todays_data_rows(db)
    return {"success": True, "todays_data_rows": total_rows}

@router.get("/totaldatascannerwise")
def total_rows_scannerwise(
    start_date: str | None,
    end_date: str | None ,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = get_total_rows_per_scanner(db, start_date, end_date)
    return {
        "success": True,
        "total_rows_per_scanner": result
    }

@router.get("/todaysdatascannerwise")
def todays_rows_scannerwise(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = get_todays_rows_per_scanner(db)
    return {"success": True, "todays_data_per_scanner": result}