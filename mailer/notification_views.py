from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .notification_serializer import NotificationSerializer
from .notification_service import NotificationService

class SendNotificationAPIView(APIView):
    """
    API View to send notifications via Email, SMS, or Both.
    """

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            success, msg = NotificationService.send_notification(
                notification_type=data['notification_type'],
                recipient_email=data.get('recipient_email'),
                recipient_phone=data.get('recipient_phone'),
                subject=data.get('subject'),
                message=data['message']
            )

            if success:
                return Response({"message": msg}, status=status.HTTP_200_OK)
            else:
                return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
