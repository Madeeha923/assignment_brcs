from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from config import REMINDER_CHECK_INTERVAL, REMINDER_THRESHOLD_MINUTES, REMINDER_ENABLED
from services.database_service import DatabaseService
from services.message_service import MessageService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db_service = DatabaseService()

    def start(self):
        """Start the reminder scheduler"""
        if not REMINDER_ENABLED:
            logger.info("Reminder scheduler is disabled")
            return

        # Add job to check for pending reminders
        self.scheduler.add_job(
            self.check_and_send_reminders,
            IntervalTrigger(seconds=REMINDER_CHECK_INTERVAL),
            id='reminder_job',
            name='Check and send appointment reminders',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info(f"Reminder scheduler started (check interval: {REMINDER_CHECK_INTERVAL}s)")

    def stop(self):
        """Stop the reminder scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Reminder scheduler stopped")

    def check_and_send_reminders(self):
        """Check for appointments within reminder threshold and send reminders"""
        try:
            pending_reminders = self.db_service.get_pending_reminders(REMINDER_THRESHOLD_MINUTES)

            for appointment in pending_reminders:
                self.send_reminder(appointment)

        except Exception as e:
            logger.error(f"Error checking reminders: {str(e)}")

    def send_reminder(self, appointment: dict):
        """Send reminder for a specific appointment"""
        try:
            phone_number = appointment['phone_number']
            customer_name = appointment['customer_name']
            appointment_time = appointment['appointment_time']
            appointment_id = appointment['id']

            # Send the reminder message
            success, message = MessageService.send_reminder_message(
                phone_number, customer_name, appointment_time
            )

            # Log the attempt
            self.db_service.log_message(
                appointment_id,
                "reminder",
                "sent" if success else "failed"
            )

            # Mark as sent if successful
            if success:
                self.db_service.mark_reminder_sent(appointment_id)
                logger.info(f"Reminder sent for appointment {appointment_id}: {message}")
            else:
                logger.warning(f"Failed to send reminder for appointment {appointment_id}: {message}")

        except Exception as e:
            logger.error(f"Error sending reminder: {str(e)}")


# Global scheduler instance
reminder_scheduler = ReminderScheduler()
