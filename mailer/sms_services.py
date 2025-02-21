# sms_services.py

from twilio.rest import Client
from django.conf import settings

def send_sms(to_phone_number, message):
    """
    Send an SMS using Twilio.
    
    :param to_phone_number: The recipient's phone number (e.g., '+14155238886')
    :param message: The SMS message to send
    :return: True if successful, False otherwise
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False