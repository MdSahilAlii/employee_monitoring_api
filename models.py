from datetime import date

from sqlalchemy import Date, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    department: Mapped[str] = mapped_column(String(50), index=True)
    role: Mapped[str] = mapped_column(String(80))
    salary: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="Active")
    join_date: Mapped[date] = mapped_column(Date)
