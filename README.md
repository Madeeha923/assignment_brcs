# WhatsApp Appointment Reminder System

A modern, full-stack appointment reminder system that sends automatic confirmations and reminders via WhatsApp or SMS.

## Features

**Appointment Booking**: Simple form to schedule appointments  
**Automatic Confirmations**: Send confirmation messages immediately after booking  
**Smart Reminders**: Automatic reminder messages within 1 hour of appointment  
**Live Dashboard**: Real-time view of all appointments with filtering  
**Multi-Channel**: Support for WhatsApp Cloud API, Twilio SMS, or simulated mode  
**Database**: Supabase for persistent storage  
**Responsive Design**: Works on desktop, tablet, and mobile  

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- Supabase (Database)
- APScheduler (Background job scheduling)

**Frontend:**
- HTML5
- CSS3 
- JavaScript 

## Render Deployment

### Prerequisites
- Render account (https://render.com)
- Git repository (GitHub)
- Environment variables configured

### Environment Variables
Set these variables in Render dashboard:

```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_KEY=your_anon_key
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
WHATSAPP_API_URL=https://graph.instagram.com/v18.0/
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_ACCESS_TOKEN=your_access_token
APP_DEBUG=False
REMINDER_ENABLED=True
REMINDER_CHECK_INTERVAL=60
REMINDER_THRESHOLD_MINUTES=60
```

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Select your GitHub repository
   - Fill in the following:
     - **Name**: appointment-reminder (or your preferred name)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

3. **Configure Environment Variables**
   - In Render dashboard, go to Service → Environment
   - Add all environment variables from the list above
   - Set `Python Version` to `3.11` (optional, in Advanced settings)

4. **Deploy**
   - Render will automatically deploy when you connect
   - Monitor deployment in the "Logs" tab

### Important Notes

- **Background Scheduler**: The APScheduler runs within the FastAPI service and will be active as long as the service is running. Note that Render may restart services periodically, which will restart the scheduler.

- **Production Database**: Use Supabase PostgreSQL for production deployments instead of SQLite

- **Static Files**: Static files are served from the `static/` directory automatically

- **Templates**: HTML templates are served from the `templates/` directory

- **Health Check**: Use the `/api/health` endpoint to monitor service status

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run application
python app.py
# or
uvicorn app:app --reload
```

### Troubleshooting

- **Port Issues**: Render dynamically assigns port via `$PORT` environment variable (handled by render.yaml)
- **Static files not found**: Ensure paths in templates are absolute or relative to project root
- **Database connection**: Verify DATABASE_URL is correct in Render environment
- **Module import errors**: Check that all service modules are in correct directories
- **Reminders not running**: Verify REMINDER_ENABLED=True in environment variables

### File Structure

```
appointment/
├── api/
│   └── index.py          # Backward compatibility
├── services/
│   ├── __init__.py
│   ├── database_service.py
│   └── message_service.py
├── scheduler/
│   ├── __init__.py
│   └── reminder_scheduler.py
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   ├── index.html
│   └── dashboard.html
├── app.py                # Main FastAPI application
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
├── render.yaml          # Render configuration
├── .gitignore
├── .env.example
└── README.md
```

### Monitoring and Logs

- Monitor your deployment in Render dashboard: https://dashboard.render.com
- View logs in the "Logs" tab of your service
- Use `/api/health` endpoint to verify service is running

### Custom Domain

To add a custom domain:
1. Go to Render dashboard → Your Service → Settings
2. Under "Custom Domain", enter your domain
3. Follow DNS configuration instructions
4. Wait for SSL certificate generation (usually instant)
 



