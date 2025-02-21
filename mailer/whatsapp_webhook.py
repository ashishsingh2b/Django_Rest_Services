from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .notification_service import NotificationService

@csrf_exempt
def whatsapp_webhook(request):
    """
    Handles incoming WhatsApp messages from Twilio Webhook.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            sender_phone = data.get("From", "").replace("whatsapp:", "")
            recipient_phone = data.get("To", "").replace("whatsapp:", "")
            message_body = data.get("Body", "")

            # Notify sender that their message was received
            NotificationService.notify_user(
                event_type="message_received",
                sender_phone=sender_phone,
                recipient_phone=recipient_phone,
                message=message_body
            )

            return JsonResponse({"status": "Message received and notification sent"}, status=200)
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return JsonResponse({"error": "Failed to process webhook"}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=405)
