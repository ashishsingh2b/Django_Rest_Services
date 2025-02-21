from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmailSerializer
from .email_services_api import SecureEmailService


class SendEmailAPIView(APIView):
    def post(self,request):
        serilizer=EmailSerializer(data=request.data)

        if serilizer.is_valid():
            data=serilizer.validated_data
            success, msg =SecureEmailService.send_email_secure(
                to_email=data['to_email'],
                subject=data['subject'],
                message=data.get('message',''),
                cc_emails=data.get('cc_emails',[])
            )
            if success:
                return Response({"message":msg},status=status.HTTP_200_OK)
            else:
                return Response({"error":msg},status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serilizer.errors,status=status.HTTP_400_BAD_REQUEST)
    