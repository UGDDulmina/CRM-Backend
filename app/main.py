from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import engine
from app.api.customers import router as customer_router
from app.api.companies import router as company_router
from app.api.lead import router as lead_router
from app.api.activities import router as activity_router
from app.api.tasks import router as task_router

app = FastAPI(
    title = "CRM Backend API",
    version="1.0.0"
)

app.include_router(customer_router)
app.include_router(company_router)
app.include_router(lead_router)
app.include_router(activity_router)
app.include_router(task_router)

@app.get("/")
def root():
    return {
        "message":"CRM Backend API",
        "status": "running"
    }

@app.get("/api/v1/health")
def health_check():
    return {
        "status":"healthy",
        "service":"crm-backend"
    }

@app.get("/api/v1/info")
def info():
    return {
                "name": "CRM Backend",
                "version": "1.0.0",
                "environment": "development",
                "modules": [
                    "customers",
                    "companies",
                    "leads",
                    "activities",
                    "tasks"
                ]
        }

@app.get("/api/v1/health/database")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

        return {
            "status" : "healthy",
            "database" : "connected"
        }


