import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

import schemas
from controllers import employee_controller
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/get_all_employees",
    tags=["Employees"],
    response_model=list[schemas.EmployeeOut],
)
def list_employees(
    search: Optional[str] = Query(
        None,
        description="matches name, email or role",
    ),
    department: Optional[str] = None,
    status_: Optional[schemas.Status] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    try:
        return employee_controller.list_employees(
            db=db,
            search=search,
            department=department,
            status_=status_,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to list employees")
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch employees",
        ) from e


@router.get(
    "/getemployee_by_id/{employee_id}",
    tags=["Employees"],
    response_model=schemas.EmployeeOut,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    try:
        return employee_controller.get_employee(db, employee_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch employee")
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch employee",
        ) from e


@router.post(
    "/create_employee",
    tags=["Employees"],
    response_model=schemas.EmployeeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    payload: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
):
    try:
        employee = employee_controller.create_employee(db, payload)

        db.commit()
        db.refresh(employee)

        return employee
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Failed to create employee")
        raise HTTPException(
            status_code=500,
            detail="Unable to create employee",
        ) from e


@router.put(
    "/replace_employee/{employee_id}",
    tags=["Employees"],
    response_model=schemas.EmployeeOut,
)
def replace_employee(
    employee_id: int,
    payload: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
):
    try:
        employee = employee_controller.replace_employee(
            db,
            employee_id,
            payload,
        )

        db.commit()
        db.refresh(employee)

        return employee
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Failed to replace employee")
        raise HTTPException(
            status_code=500,
            detail="Unable to replace employee",
        ) from e


@router.patch(
    "/update_employee/{employee_id}",
    tags=["Employees"],
    response_model=schemas.EmployeeOut,
)
def update_employee(
    employee_id: int,
    payload: schemas.EmployeeUpdate,
    db: Session = Depends(get_db),
):
    try:
        employee = employee_controller.update_employee(
            db,
            employee_id,
            payload,
        )

        db.commit()
        db.refresh(employee)

        return employee
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Failed to update employee")
        raise HTTPException(
            status_code=500,
            detail="Unable to update employee",
        ) from e


@router.delete(
    "/delete_employee/{employee_id}",
    tags=["Employees"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    try:
        employee_controller.delete_employee(db, employee_id)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Failed to delete employee")
        raise HTTPException(
            status_code=500,
            detail="Unable to delete employee",
        ) from e


@router.get("/stats", tags=["Employees"])
def stats(db: Session = Depends(get_db)):
    try:
        return employee_controller.get_employee_stats(db)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch employee statistics")
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch employee statistics",
        ) from e