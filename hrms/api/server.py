from fastapi import FastAPI
from ..persons.service import list_employees

app = FastAPI(title="HRMS CSV API")

@app.get("/employees")
def employees():
    return list_employees(only_active=True, limit=200)
