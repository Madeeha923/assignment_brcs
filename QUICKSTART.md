# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
The app works in **simulation mode** by default (no API keys needed for testing):

```bash
# Copy the template
cp .env .env.local

# Edit with your API credentials (optional)
# Leave blank to test in simulation mode
```

### 3. Run the Application
```bash
python app.py
```

You'll see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 4. Open in Browser
- **Book Appointment**: http://localhost:8000/
- **View Dashboard**: http://localhost:8000/dashboard

---

## 📝 API Examples

### Create Appointment
```bash
curl -X POST http://localhost:8000/api/appointments \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "customer_name=John+Doe&phone_number=%2B11234567890&appointment_time=2024-12-25T14:30:00"
```

### Get All Appointments
```bash
curl http://localhost:8000/api/appointments
```

### Send Manual Reminder
```bash
curl -X POST http://localhost:8000/api/reminders/1/send-now
```

---

## 🔧 Configuration

### Using WhatsApp (Meta Cloud API)
1. Get credentials from https://developers.facebook.com/
2. Edit `.env.local`:
```env
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_number_id_here
```

### Using Twilio SMS
1. Get credentials from https://www.twilio.com/
2. Edit `.env.local`:
```env
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

---

## 📁 File Structure

```
appointment-reminder/
├── app.py                    ← Main app (run this!)
├── config.py                 ← Settings
├── requirements.txt          ← Dependencies
├── .env                      ← Config template
│
├── templates/
│   ├── index.html           ← Booking form
│   └── dashboard.html       ← View appointments
│
├── static/
│   ├── style.css            ← Styling
│   └── script.js            ← Frontend logic
│
├── services/
│   ├── database_service.py  ← SQLite operations
│   └── message_service.py   ← WhatsApp/SMS
│
└── scheduler/
    └── reminder_scheduler.py ← Auto reminders
```

---

## 🧪 Testing

### Manual Testing
1. Book an appointment in the form
2. Check console output for simulated message
3. View dashboard to see all appointments
4. Test reminder sending with "Send Reminder" button

### API Testing
Use Postman, curl, or VS Code REST Client extension

---

## 🐛 Troubleshooting

**Port 8000 already in use?**
```bash
# Kill the process or use different port
python app.py --port 8080
```

**Database errors?**
```bash
# Reset database
rm appointments.db
python app.py
```

**Messages not working?**
- Check your API credentials in `.env`
- Verify phone number format: `+1234567890`
- Simulation mode is always active if APIs aren't configured

---

## 📚 Learn More

- Check `README.md` for full documentation
- Review code comments in `app.py`
- Explore API in `services/` folder

---

## 🎯 Next Steps

1. ✅ Test the app in simulation mode
2. 🔑 Add your API credentials (optional)
3. 📊 Try the dashboard filtering
4. 🚀 Deploy to Netlify/Vercel (frontend) + Heroku/Railway (backend)

Happy coding! 🎉
