from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import auth, employee, department
from app.routers import auth, employee, background, department


app = FastAPI()

app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(background.router)
app.include_router(department.router)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 테스트
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Employee API running"}