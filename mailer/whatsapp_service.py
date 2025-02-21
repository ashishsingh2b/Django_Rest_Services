from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to_phone_number, message):
    """
    Send a WhatsApp message using Twilio API.
    
    :param to_phone_number: Recipient's WhatsApp number (e.g., '+14155238886')
    :param message: Message content
    :return: True if message sent successfully, False otherwise
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',  
            body=message,
            to=f'whatsapp:{to_phone_number}'  
        )
        print(f"Message sent: {msg.sid}")
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
        return False
