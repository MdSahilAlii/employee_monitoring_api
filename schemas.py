from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Status = Literal["Active", "On Leave", "Resigned"]


class EmployeeBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    department: str = Field(min_length=2, max_length=50)
    role: str = Field(min_length=2, max_length=80)
    salary: float = Field(gt=0, description="Monthly salary, must be positive")
    status: Status = "Active"
    join_date: date

    @field_validator("name", "department", "role")
    @classmethod
    def strip_spaces(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("must have at least 2 characters")
        return value

    @field_validator("join_date")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("join date cannot be in the future")
        return value


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    """For PATCH: every field optional, only what the client sends is changed."""

    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(default=None, min_length=2, max_length=50)
    role: Optional[str] = Field(default=None, min_length=2, max_length=80)
    salary: Optional[float] = Field(default=None, gt=0)
    status: Optional[Status] = None
    join_date: Optional[date] = None


class EmployeeOut(EmployeeBase):
    id: int

    # lets Pydantic read straight from a SQLAlchemy object
    model_config = ConfigDict(from_attributes=True)
