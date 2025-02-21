from .whatsapp_service import send_whatsapp_message
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Handles notifications when a WhatsApp message is sent or received.
    """

    @staticmethod
    def notify_user(event_type, sender_phone, recipient_phone, message, recipient_email=None):
        """
        Notify the recipient via WhatsApp and optionally via email.

        :param event_type: 'message_sent' or 'message_received'
        :param sender_phone: Sender's phone number
        :param recipient_phone: Recipient's phone number
        :param message: Message content
        :param recipient_email: Recipient's email (optional for email notification)
        :return: Notification status
        """
        notification_message = (
            f"📩 *New WhatsApp Message Notification*\n\n"
            f"🔹 *Event:* {event_type.replace('_', ' ').title()}\n"
            f"🔹 *From:* {sender_phone}\n"
            f"🔹 *To:* {recipient_phone}\n\n"
            f"📨 *Message:* {message}"
        )

        success_whatsapp = False
        success_email = False

        # Send WhatsApp notification
        try:
            success_whatsapp = send_whatsapp_message(recipient_phone, notification_message)
            if success_whatsapp:
                logger.info(f"WhatsApp notification sent to {recipient_phone}")
            else:
                logger.warning(f"Failed to send WhatsApp notification to {recipient_phone}")
        except Exception as e:
            logger.error(f"Error sending WhatsApp notification: {e}")

        # Send Email notification (if recipient email is provided)
        if recipient_email:
            try:
                send_mail(
                    subject="New WhatsApp Message Notification",
                    message=f"You have received a new message:\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                success_email = True
                logger.info(f"Email notification sent to {recipient_email}")
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")

        return {
            "whatsapp_sent": success_whatsapp,
            "email_sent": success_email if recipient_email else None,
            "status": "Notification sent successfully" if success_whatsapp or success_email else "Failed to send notification"
        }




























# from .email_services_api import SecureEmailService

# from .sms_services import send_sms  # Import your Twilio SMS function

# class NotificationService:

#     @staticmethod
#     def send_notification(notification_type, recipient_email=None, recipient_phone=None, subject=None, message=None):
#         success_email, success_sms = False, False
#         email_msg, sms_msg = None, None

#         # Send Email if selected
#         if notification_type in ["email", "both"] and recipient_email:
#             success_email, email_msg = SecureEmailService.send_email_secure(
#                 to_email=recipient_email,
#                 subject=subject,
#                 message=message
#             )

#         # Send SMS if selected
#         if notification_type in ["sms", "both"] and recipient_phone:
#             success_sms = send_sms(recipient_phone, message)  # Using your Twilio SMS function
#             sms_msg = "SMS sent successfully" if success_sms else "Failed to send SMS"

#         # Response Logic
#         if notification_type == "email":
#             return success_email, email_msg
#         elif notification_type == "sms":
#             return success_sms, sms_msg
#         else:
#             return success_email and success_sms, "Notification sent successfully!" if success_email and success_sms else "Failed to send notification."
