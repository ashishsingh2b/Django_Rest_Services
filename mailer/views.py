from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EmailForm
from .email_services_django import SecureEmailService
from django.views.generic import FormView


def home(request):
    return render(request, 'home.html')

def send_mail_page(request):
    form = EmailForm()
    return render(request, 'send_mail.html', {'form': form})

class SendMailView(FormView):
    template_name = 'send_mail.html'
    form_class = EmailForm
    success_url = '/'

    def form_valid(self, form):
        to_email = form.cleaned_data['to_email']
        cc_email_input = form.cleaned_data.get('cc_email', '')
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        cc_emails = [email.strip() for email in cc_email_input.split(',') if email.strip()]
        
        success, msg = SecureEmailService.send_email_secure(
            to_email=to_email,
            subject=subject,
            message=message,
            cc_emails=cc_emails
        )

        if success:
            messages.success(self.request, msg)
        else:
            messages.error(self.request, msg)

        return redirect(self.success_url)


















# from django.shortcuts import render, redirect

# from django.contrib import messages
# from .forms import EmailForm
# from .services import send_email_secure

# def home(request):
#     return render(request, 'home.html')

# def send_mail_page(request):
#     form = EmailForm()
#     return render(request, 'send_mail.html', {'form': form})

# def process_mail(request):
#     if request.method == 'POST':
#         form = EmailForm(request.POST)
#         if form.is_valid():
#             to_email = form.cleaned_data['to_email']
#             cc_email = form.cleaned_data.get('cc_email')  # Use .get() to avoid KeyError
#             subject = form.cleaned_data['subject']
#             message = form.cleaned_data['message']

#             # Send email using service
#             success, msg = send_email_secure(
#                 to_email=to_email,
#                 subject=subject,
#                 message=message,
#                 cc_email=cc_email
#             )

#             if success:
#                 messages.success(request, msg)
#             else:
#                 messages.error(request, msg)

#             return redirect('home')

#     return redirect('send_mail_page')
