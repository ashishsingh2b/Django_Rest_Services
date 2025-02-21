from rest_framework import serializers

class NotificationSerializer(serializers.Serializer):
    NOTIFICATION_TYPES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Both'),
    )

    notification_type = serializers.ChoiceField(choices=NOTIFICATION_TYPES)
    recipient_email = serializers.EmailField(required=False)
    recipient_phone = serializers.CharField(max_length=15, required=False)
    subject = serializers.CharField(max_length=255, required=False)
    message = serializers.CharField()

    def validate(self, data):
        if data['notification_type'] in ['email', 'both'] and not data.get('recipient_email'):
            raise serializers.ValidationError("Recipient email is required for email notifications.")
        if data['notification_type'] in ['sms', 'both'] and not data.get('recipient_phone'):
            raise serializers.ValidationError("Recipient phone number is required for SMS notifications.")
        return data
