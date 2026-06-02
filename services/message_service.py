import requests
import json
from typing import Tuple
from config import (
    USE_WHATSAPP, USE_TWILIO,
    WHATSAPP_API_URL, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
)


class MessageService:
    """Service to send WhatsApp, Twilio SMS, or simulated messages"""

    @staticmethod
    def send_confirmation_message(phone_number: str, customer_name: str, appointment_time: str) -> Tuple[bool, str]:
        """Send appointment confirmation message"""
        message = f"Hi {customer_name}, your appointment has been confirmed for {appointment_time}. We look forward to seeing you!"

        if USE_WHATSAPP:
            return MessageService.send_whatsapp_message(phone_number, message)
        elif USE_TWILIO:
            return MessageService.send_twilio_sms(phone_number, message)
        else:
            # Simulate sending
            return MessageService.simulate_message_send(phone_number, message, "Confirmation")

    @staticmethod
    def send_reminder_message(phone_number: str, customer_name: str, appointment_time: str) -> Tuple[bool, str]:
        """Send appointment reminder message (within 1 hour)"""
        message = f"Reminder: {customer_name}, your appointment is coming up at {appointment_time}. See you soon!"

        if USE_WHATSAPP:
            return MessageService.send_whatsapp_message(phone_number, message)
        elif USE_TWILIO:
            return MessageService.send_twilio_sms(phone_number, message)
        else:
            # Simulate sending
            return MessageService.simulate_message_send(phone_number, message, "Reminder")

    @staticmethod
    def send_whatsapp_message(phone_number: str, message: str) -> Tuple[bool, str]:
        """Send message via WhatsApp Cloud API"""
        try:
            # Format phone number (remove +, ensure it's 10+ digits)
            formatted_phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")

            url = f"{WHATSAPP_API_URL}{WHATSAPP_PHONE_NUMBER_ID}/messages"

            headers = {
                "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            }

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code in [200, 201]:
                return True, "Message sent successfully via WhatsApp"
            else:
                error_msg = response.json().get("error", {}).get("message", str(response.text))
                return False, f"WhatsApp API Error: {error_msg}"

        except Exception as e:
            return False, f"Error sending WhatsApp message: {str(e)}"

    @staticmethod
    def send_twilio_sms(phone_number: str, message: str) -> Tuple[bool, str]:
        """Send message via Twilio SMS"""
        try:
            from twilio.rest import Client

            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            sms = client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )

            return True, f"SMS sent successfully via Twilio (SID: {sms.sid})"

        except Exception as e:
            return False, f"Error sending Twilio SMS: {str(e)}"

    @staticmethod
    def simulate_message_send(phone_number: str, message: str, message_type: str = "Message") -> Tuple[bool, str]:
        """Simulate sending a message (for testing without API credentials)"""
        # In production, this would actually send
        log_msg = f"\n{'='*60}\n{message_type} Simulation\n{'='*60}\nTo: {phone_number}\nMessage: {message}\n{'='*60}\n"
        print(log_msg)
        return True, f"{message_type} simulated successfully to {phone_number}"

    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        """Validate phone number format"""
        # Remove common formatting
        cleaned = phone_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")

        # Should be at least 10 digits
        return len(cleaned) >= 10 and cleaned.isdigit()

    @staticmethod
    def format_phone_number(phone_number: str) -> str:
        """Format phone number to E.164 format"""
        cleaned = phone_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")

        # If it starts with 1 (US), add + prefix
        if cleaned.startswith("1") and len(cleaned) == 11:
            return f"+{cleaned}"
        elif len(cleaned) >= 10:
            return f"+{cleaned}"
        else:
            return f"+{cleaned}"
