# WhatsApp Appointment Reminder System

A modern, full-stack appointment reminder system that sends automatic confirmations and reminders via WhatsApp or SMS.

## Features

✅ **Appointment Booking**: Simple form to schedule appointments  
✅ **Automatic Confirmations**: Send confirmation messages immediately after booking  
✅ **Smart Reminders**: Automatic reminder messages within 1 hour of appointment  
✅ **Live Dashboard**: Real-time view of all appointments with filtering  
✅ **Multi-Channel**: Support for WhatsApp Cloud API, Twilio SMS, or simulated mode  
✅ **Database**: Supabase for persistent storage  
✅ **Responsive Design**: Works on desktop, tablet, and mobile  

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- Supabase (Database)
- APScheduler (Background job scheduling)

**Frontend:**
- HTML5
- CSS3 (Modern responsive design)
- Vanilla JavaScript (No dependencies)

**Messaging:**
- WhatsApp Cloud API
- Twilio SMS API
- Simulated mode for testing

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Steps

1. **Clone or download the project**
   ```bash
   cd appointment-reminder
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env .env.local
   # Edit .env.local with your API credentials
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to: `http://localhost:8000`

## Configuration

### Using WhatsApp Cloud API

1. Get your credentials from [Meta for Developers](https://developers.facebook.com/)
2. Update `.env`:
   ```env
   WHATSAPP_API_URL=https://graph.instagram.com/v18.0/
   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
   WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
   WHATSAPP_ACCESS_TOKEN=your_access_token_here
   ```

### Using Twilio SMS

1. Sign up at [Twilio](https://www.twilio.com/)
2. Update `.env`:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### Testing Mode (No API Required)

The system will automatically simulate message sending if no API credentials are configured. Messages are logged to the console.

## Project Structure

```
appointment-reminder/
│
├── app.py                    # Main FastAPI application
├── config.py                 # Configuration and settings
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (template)
│
├── templates/
│   ├── index.html           # Appointment booking form
│   └── dashboard.html       # Appointments dashboard
│
├── static/
│   ├── style.css            # Styling
│   └── script.js            # Frontend logic
│
├── services/
│   ├── database_service.py  # Database operations
│   └── message_service.py   # WhatsApp/SMS sending
│
├── scheduler/
│   └── reminder_scheduler.py # Automatic reminder scheduler
│
└── README.md               # This file
```

## API Endpoints

### Appointments

- `GET /` - Booking form page
- `GET /dashboard` - Dashboard page
- `POST /api/appointments` - Create appointment
- `GET /api/appointments` - Get all appointments
- `GET /api/appointments/{id}` - Get specific appointment
- `DELETE /api/appointments/{id}` - Delete appointment
- `POST /api/reminders/{id}/send-now` - Send manual reminder

### Health

- `GET /api/health` - Health check

## How It Works

### 1. Booking Flow
```
User fills form → Submit → API creates appointment → 
Send confirmation message → Show success page → 
Redirect to dashboard
```

### 2. Automatic Reminder Flow
```
APScheduler checks every 60 seconds → 
Find appointments within 1 hour → 
Send reminder message → 
Mark as sent in database
```

### 3. Data Flow
```
Frontend (HTML/JS) → FastAPI Backend → Database (Supabase)
                 → Message Service (WhatsApp/SMS)
Frontend (Dashboard) ← API (JSON) ← Database
```

## Usage

### Book an Appointment
1. Go to the home page
2. Fill in your name, phone number, and appointment time
3. Click "Book Appointment"
4. Receive confirmation via WhatsApp/SMS
5. Get automatic reminder 1 hour before

### View Dashboard
1. Click "View Dashboard"
2. See all appointments with their status
3. Filter by name, phone, or status
4. Send manual reminders if needed
5. Delete appointments

## Development

### Adding New Features

**Database Changes:**
- Edit `services/database_service.py`
- Update `init_db()` method

**API Routes:**
- Add new routes in `app.py`
- Use existing services for database/messaging

**Frontend Changes:**
- Update `templates/*.html` for markup
- Modify `static/style.css` for styling
- Update `static/script.js` for interactivity

### Running in Development

```bash
# With auto-reload
uvicorn app:app --reload

# Or run directly
python app.py
```

## Troubleshooting

### Messages not sending
- Check `.env` file for correct API credentials
- Verify phone number format (include country code)
- Check console for error messages
- Try simulated mode first (just comment out credentials)

### Database errors
- Delete `appointments.db` to reset database
- Ensure write permissions in directory

### Port already in use
```bash
# Change port in app.py or use:
python app.py --port 8080
```

## Performance & Scalability

**Current Setup:**
- Supabase database (suitable for production and serverless deployments)
- APScheduler (in-memory job scheduler)
- Single-threaded FastAPI server

**For Production:**
- Migrate to PostgreSQL
- Use Celery + Redis for job queue
- Deploy with Gunicorn/Docker
- Add caching layer (Redis)

## Security Considerations

- Keep API tokens secure (use `.env` file, never commit to git)
- Validate all user inputs
- Use HTTPS in production
- Implement rate limiting
- Add authentication for admin endpoints

## License

MIT License - Feel free to use and modify

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check console logs for errors

## Future Enhancements

- [ ] SMS as fallback when WhatsApp fails
- [ ] Appointment cancellation/rescheduling
- [ ] Email notifications
- [ ] Calendar integration
- [ ] Multi-language support
- [ ] Admin dashboard
- [ ] Analytics and reporting
- [ ] Appointment duration/notes
- [ ] Customer feedback system
- [ ] Integration with booking platforms

---

**Built with ❤️ using FastAPI and modern web technologies**
