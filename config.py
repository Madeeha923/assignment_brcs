import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./appointments.db")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or os.getenv("SUPABASE_KEY", "")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# WhatsApp Cloud API Configuration
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")

# App Settings
DEBUG = os.getenv("APP_DEBUG", "True") == "True"
REMINDER_CHECK_INTERVAL = int(os.getenv("REMINDER_CHECK_INTERVAL", "60"))

# Features
USE_WHATSAPP = bool(WHATSAPP_ACCESS_TOKEN)
USE_TWILIO = bool(TWILIO_ACCOUNT_SID)
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
REMINDER_ENABLED = os.getenv("REMINDER_ENABLED", "True") == "True"
REMINDER_THRESHOLD_MINUTES = int(os.getenv("REMINDER_THRESHOLD_MINUTES", "60"))
