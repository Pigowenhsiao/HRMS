from fastapi import FastAPI
from ..persons.service import list_employees
from .auth_routes import router as auth_router
from .personal_info_routes import router as personal_info_router
from .education_routes import router as education_router
from .report_routes import router as report_router

app = FastAPI(title="HRMS Multi-Backend API")

# 包含認證相關路由
app.include_router(auth_router)

# 包含個人訊息相關路由
app.include_router(personal_info_router)

# 包含教育經歷相關路由
app.include_router(education_router)

# 包含報表相關路由
app.include_router(report_router)

@app.get("/employees")
def employees():
    return list_employees(only_active=True, limit=200)

@app.get("/")
def read_root():
    return {"message": "Welcome to HRMS API"}
