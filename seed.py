"""Run once: python seed.py  -> adds a few sample employees."""
from datetime import date

from database import Base, SessionLocal, engine
from models import Employee

Base.metadata.create_all(bind=engine)

people = [
    ("Riya Deshmukh", "riya.d@acme.in", "Engineering", "Backend Developer", 85000, "Active", date(2022, 6, 13)),
    ("Aman Kulkarni", "aman.k@acme.in", "Engineering", "Frontend Developer", 78000, "Active", date(2023, 1, 9)),
    ("Sneha Patil", "sneha.p@acme.in", "HR", "HR Executive", 52000, "On Leave", date(2021, 11, 1)),
    ("Karan Mehta", "karan.m@acme.in", "Sales", "Account Manager", 61000, "Active", date(2020, 3, 16)),
    ("Divya Nair", "divya.n@acme.in", "Finance", "Accountant", 58000, "Resigned", date(2019, 8, 5)),
]

with SessionLocal() as db:
    if db.query(Employee).count() == 0:
        for n, e, d, r, s, st, j in people:
            db.add(Employee(name=n, email=e, department=d, role=r, salary=s, status=st, join_date=j))
        db.commit()
        print("Seeded", len(people), "employees")
    else:
        print("Table already has data, skipping")
