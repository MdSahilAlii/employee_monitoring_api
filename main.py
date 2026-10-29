from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)  # creates employees.db + table on first run

app = FastAPI(title="Employee Tracker API")

#connecting frontend with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_or_404(db: Session, employee_id: int) -> models.Employee:
    employee = db.get(models.Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


def email_taken(db: Session, email: str, ignore_id: Optional[int] = None) -> bool:
    query = db.query(models.Employee).filter(models.Employee.email == email)
    if ignore_id is not None:
        query = query.filter(models.Employee.id != ignore_id)
    return query.first() is not None


@app.get("/employees", response_model=list[schemas.EmployeeOut])
def list_employees(
    search: Optional[str] = Query(None, description="matches name, email or role"),
    department: Optional[str] = None,
    status_: Optional[schemas.Status] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Employee)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                models.Employee.name.ilike(like),
                models.Employee.email.ilike(like),
                models.Employee.role.ilike(like),
            )
        )
    if department:
        query = query.filter(models.Employee.department == department)
    if status_:
        query = query.filter(models.Employee.status == status_)
    return query.order_by(models.Employee.name).all()


@app.get("/employees/{employee_id}", response_model=schemas.EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, employee_id)


@app.post(
    "/employees",
    response_model=schemas.EmployeeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    if email_taken(db, payload.email):
        raise HTTPException(status_code=409, detail="This email is already in use")
    employee = models.Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@app.put("/employees/{employee_id}", response_model=schemas.EmployeeOut)
def replace_employee(
    employee_id: int, payload: schemas.EmployeeCreate, db: Session = Depends(get_db)
):
    """PUT = replace the whole record, so every field is required."""
    employee = get_or_404(db, employee_id)
    if email_taken(db, payload.email, ignore_id=employee_id):
        raise HTTPException(status_code=409, detail="This email is already in use")
    for field, value in payload.model_dump().items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


@app.patch("/employees/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee(
    employee_id: int, payload: schemas.EmployeeUpdate, db: Session = Depends(get_db)
):
    """PATCH = change only the fields that were sent."""
    employee = get_or_404(db, employee_id)
    changes = payload.model_dump(exclude_unset=True)
    if "email" in changes and email_taken(db, changes["email"], ignore_id=employee_id):
        raise HTTPException(status_code=409, detail="This email is already in use")
    for field, value in changes.items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = get_or_404(db, employee_id)
    db.delete(employee)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    E = models.Employee
    total = db.query(func.count(E.id)).scalar()
    average_salary = db.query(func.avg(E.salary)).filter(E.status != "Resigned").scalar()
    by_status = dict(db.query(E.status, func.count(E.id)).group_by(E.status).all())
    by_department = dict(
        db.query(E.department, func.count(E.id)).group_by(E.department).all()
    )
    return {
        "total": total,
        "active": by_status.get("Active", 0),
        "on_leave": by_status.get("On Leave", 0),
        "resigned": by_status.get("Resigned", 0),
        "average_salary": round(average_salary or 0, 2),
        "departments": sorted(by_department),
        "by_department": by_department,
    }
