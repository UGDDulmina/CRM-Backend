from fastapi import FastAPI


app = FastAPI(
    title = "CRM Backend API",
    version="1.0.0"
)

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
