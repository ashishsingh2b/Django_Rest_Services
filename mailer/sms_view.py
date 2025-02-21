# sms_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .sms_services import send_sms

class SendSMSView(APIView):
    def post(self, request):
        """
        Send an SMS via POST request.
        
        Expected JSON payload:
        {
            "phone_number": "+14155238886",
            "message": "Hello, this is a test message!"
        }
        """
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')

        if not phone_number or not message:
            return Response(
                {"error": "Both 'phone_number' and 'message' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Send SMS
        success = send_sms(phone_number, message)

        if success:
            return Response(
                {"status": "SMS sent successfully!"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Failed to send SMS."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )