from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

import models
import schemas


def get_or_404(db: Session, employee_id: int) -> models.Employee:
    employee = db.get(models.Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    return employee


def email_taken(
    db: Session,
    email: str,
    ignore_id: Optional[int] = None,
) -> bool:
    query = db.query(models.Employee).filter(
        models.Employee.email == email
    )

    if ignore_id is not None:
        query = query.filter(models.Employee.id != ignore_id)

    return query.first() is not None


def list_employees(
    db: Session,
    search: Optional[str] = None,
    department: Optional[str] = None,
    status_: Optional[schemas.Status] = None,
) -> list[models.Employee]:
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
        query = query.filter(
            models.Employee.department == department
        )

    if status_:
        query = query.filter(models.Employee.status == status_)

    return query.order_by(models.Employee.name).all()


def get_employee(
    db: Session,
    employee_id: int,
) -> models.Employee:
    return get_or_404(db, employee_id)


def create_employee(
    db: Session,
    payload: schemas.EmployeeCreate,
) -> models.Employee:
    if email_taken(db, payload.email):
        raise HTTPException(
            status_code=409,
            detail="This email is already in use",
        )

    employee = models.Employee(**payload.model_dump())
    db.add(employee)

    return employee


def replace_employee(
    db: Session,
    employee_id: int,
    payload: schemas.EmployeeCreate,
) -> models.Employee:
    employee = get_or_404(db, employee_id)

    if email_taken(db, payload.email, ignore_id=employee_id):
        raise HTTPException(
            status_code=409,
            detail="This email is already in use",
        )

    for field, value in payload.model_dump().items():
        setattr(employee, field, value)

    return employee


def update_employee(
    db: Session,
    employee_id: int,
    payload: schemas.EmployeeUpdate,
) -> models.Employee:
    employee = get_or_404(db, employee_id)
    changes = payload.model_dump(exclude_unset=True)

    if "email" in changes and email_taken(
        db,
        changes["email"],
        ignore_id=employee_id,
    ):
        raise HTTPException(
            status_code=409,
            detail="This email is already in use",
        )

    for field, value in changes.items():
        setattr(employee, field, value)

    return employee


def delete_employee(
    db: Session,
    employee_id: int,
) -> None:
    employee = get_or_404(db, employee_id)
    db.delete(employee)


def get_employee_stats(db: Session) -> dict:
    employee = models.Employee

    total = db.query(func.count(employee.id)).scalar()

    average_salary = (
        db.query(func.avg(employee.salary))
        .filter(employee.status != "Resigned")
        .scalar()
    )

    by_status = dict(
        db.query(employee.status, func.count(employee.id))
        .group_by(employee.status)
        .all()
    )

    by_department = dict(
        db.query(employee.department, func.count(employee.id))
        .group_by(employee.department)
        .all()
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