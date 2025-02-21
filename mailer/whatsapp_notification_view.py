from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .notification_service import NotificationService
from email_service import settings

class WhatsAppNotificationView(APIView):
    def post(self, request):
        """
        API to send a WhatsApp message and notify the recipient.
        
        Expected JSON payload:
        {
            "recipient_phone": "+918487840633",
            "message": "Hello, you have a new message!",
            "recipient_email": "recipient@example.com"
        }
        """
        recipient_phone = request.data.get('recipient_phone')
        message = request.data.get('message')
        recipient_email = request.data.get('recipient_email')

        if not recipient_phone or not message:
            return Response(
                {"error": "Both 'recipient_phone' and 'message' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Send message and trigger notification
        result = NotificationService.notify_user(
            event_type="message_sent",
            sender_phone=settings.TWILIO_WHATSAPP_NUMBER,
            recipient_phone=recipient_phone,
            message=message,
            recipient_email=recipient_email
        )

        return Response(result, status=status.HTTP_200_OK if result["whatsapp_sent"] else status.HTTP_500_INTERNAL_SERVER_ERROR)
