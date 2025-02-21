from django.urls import path
from . import views
from .views import SendMailView
from .email_view import SendEmailAPIView
from .sms_view import SendSMSView
from .notification_views import SendNotificationAPIView
from .whatsapp_notification_view import WhatsAppNotificationView
from .whatsapp_webhook import whatsapp_webhook
from .search_view import search_product_view







urlpatterns = [
    path('', views.home, name='home'),
    path('send-mail/', views.send_mail_page, name='send_mail_page'),
    path('send-mail/process/', SendMailView.as_view(), name='process_mail'),
    path('api/send-email/',SendEmailAPIView.as_view(),name='send-email'),
    path('send-sms/', SendSMSView.as_view(), name='send-sms'),
    path('api/send-notification/', SendNotificationAPIView.as_view(), name='send-notification'),
    path('api/send-whatsapp-notification/', WhatsAppNotificationView.as_view(), name='send_whatsapp_notification'),
    path('api/send-whatsapp-message/', WhatsAppNotificationView.as_view(), name='send_whatsapp_message'),
    path('api/whatsapp-webhook/', whatsapp_webhook, name='whatsapp_webhook'),
    path("api/search/", search_product_view, name="search-products"),





    
    
]