from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List
import logging
import os
from contextlib import asynccontextmanager

from services.database_service import DatabaseService
from services.message_service import MessageService
from scheduler.reminder_scheduler import ReminderScheduler
from config import DEBUG, REMINDER_THRESHOLD_MINUTES

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances (initialized at startup)
db_service = None
reminder_scheduler = None

# Pydantic models
class AppointmentCreate(BaseModel):
    customer_name: str
    phone_number: str
    appointment_time: str


class AppointmentResponse(BaseModel):
    id: int
    customer_name: str
    phone_number: str
    appointment_time: str
    created_at: str
    reminder_sent: bool
    confirmation_sent: bool
    status: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    global db_service, reminder_scheduler
    try:
        logger.info("Initializing services...")
        db_service = DatabaseService()
        reminder_scheduler = ReminderScheduler()
        
        logger.info("Starting Appointment Reminder System...")
        reminder_scheduler.start()
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Appointment Reminder System...")
    try:
        if reminder_scheduler:
            reminder_scheduler.stop()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


# FastAPI app with lifespan
app = FastAPI(title="Appointment Reminder System", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Routes
@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the appointment form page"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the dashboard page"""
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/appointments")
async def create_appointment(
    customer_name: str = Form(...),
    phone_number: str = Form(...),
    appointment_time: str = Form(...)
):
    """Create a new appointment and send confirmation message"""
    try:
        # Validate phone number
        if not MessageService.validate_phone_number(phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")

        # Validate appointment time format
        try:
            datetime.fromisoformat(appointment_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid appointment time format")

        # Create appointment in database
        appointment = db_service.create_appointment(customer_name, phone_number, appointment_time)

        # Send confirmation message
        success, message = MessageService.send_confirmation_message(
            phone_number, customer_name, appointment_time
        )

        # Log the message attempt
        db_service.log_message(appointment["id"], "confirmation", "sent" if success else "failed")

        # Mark confirmation as sent if successful
        if success:
            db_service.mark_confirmation_sent(appointment["id"])
            logger.info(f"Appointment created and confirmation sent: {message}")
        else:
            logger.warning(f"Appointment created but confirmation failed: {message}")

        return {
            "success": True,
            "appointment": appointment,
            "message": message,
            "confirmation_sent": success
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/appointments", response_model=List[AppointmentResponse])
async def get_appointments():
    """Get all appointments"""
    try:
        appointments = db_service.get_all_appointments()
        return appointments
    except Exception as e:
        logger.error(f"Error retrieving appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: int):
    """Get a specific appointment"""
    try:
        appointment = db_service.get_appointment(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int):
    """Delete an appointment"""
    try:
        success = db_service.delete_appointment(appointment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return {"success": True, "message": "Appointment deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reminders/{appointment_id}/send-now")
async def send_reminder_now(appointment_id: int):
    """Manually trigger a reminder for an appointment"""
    try:
        appointment = db_service.get_appointment(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        phone_number = appointment["phone_number"]
        customer_name = appointment["customer_name"]
        appointment_time = appointment["appointment_time"]

        success, message = MessageService.send_reminder_message(
            phone_number, customer_name, appointment_time
        )

        db_service.log_message(appointment_id, "reminder", "sent" if success else "failed")

        if success:
            db_service.mark_reminder_sent(appointment_id)

        return {
            "success": success,
            "message": message,
            "appointment_id": appointment_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending reminder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "reminder_threshold": REMINDER_THRESHOLD_MINUTES
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=DEBUG)
