from fastapi import FastAPI , Depends , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.api_routes import doctors_availability, appointments_book, chat , check_patient_record ,email_routes ,voice
app =FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/Health")
async def Healthcheck():
    return {"staus" : "Healthy"}

@app.get("/check_database_connection")
async def check_db_connection(db:Session=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException (status_code= 500 , detail= f"database connection Failed {e}")
    
# API routes :::::
app.include_router(doctors_availability.router)
app.include_router(check_patient_record.router)
app.include_router(appointments_book.router)
app.include_router(chat.router)
app.include_router(email_routes.router)
app.include_router(voice.router)


