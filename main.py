from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, engine
from routers.employee_router import router as employee_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee_router)