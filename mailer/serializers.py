from rest_framework import serializers
from .email_services_api import SecureEmailService

class EmailSerializer(serializers.Serializer):
    to_email = serializers.EmailField()
    cc_emails= serializers.ListField(
        child=serializers.EmailField(), required=False
    )
    subject=serializers.CharField(max_length=255)
    message=serializers.CharField(allow_blank=True)

class ProductSerializer(serializers.Serializer):
    pass