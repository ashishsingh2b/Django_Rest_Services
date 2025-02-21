

# import re
# import dns.resolver
# import smtplib
# import socket
# import logging
# import bleach
# from typing import Tuple, Optional, List
# from datetime import datetime, timedelta
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.core.cache import cache
# from django.utils.crypto import get_random_string
# from email.utils import parseaddr
# import ssl

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class EmailSecurity:
#     # Rate limiting settings
#     MAX_EMAILS_PER_HOUR = 100
#     MAX_RECIPIENTS = 50
    
#     # Content limits
#     MAX_SUBJECT_LENGTH = 998  # RFC 2822
#     MAX_MESSAGE_LENGTH = 10485760  # 10MB
    
#     # Allowed HTML tags and attributes
#     ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'a']
#     ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

# class SecureEmailService:
#     def __init__(self):
#         self.email_security = EmailSecurity()
    
#     def rate_limit_check(self, sender_ip: str) -> bool:
#         """Check if sender has exceeded rate limits"""
#         cache_key = f"email_count_{sender_ip}"
#         current_count = cache.get(cache_key, 0)

#         if current_count >= self.email_security.MAX_EMAILS_PER_HOUR:
#             return False

#         cache.set(cache_key, current_count + 1, timeout=3600)  # 1 hour
#         return True

#     def sanitize_content(self, content: str) -> str:
#         """Sanitize HTML content to prevent XSS attacks"""
#         return bleach.clean(
#             content,
#             tags=self.email_security.ALLOWED_TAGS,
#             attributes=self.email_security.ALLOWED_ATTRIBUTES,
#             strip=True
#         )

#     def validate_email_advanced(self, email: str) -> Tuple[bool, Optional[str]]:
#         """Enhanced email validation with security checks"""
#         try:
#             # Basic validation
#             if not email or '@' not in email:
#                 return False, "Invalid email format"

#             # Parse email address
#             name, addr = parseaddr(email)
#             if not addr:
#                 return False, "Invalid email format"

#             # Length checks
#             local, domain = addr.split('@')
#             if len(local) > 64 or len(domain) > 255:
#                 return False, "Email length exceeds limits"

#             # Regex pattern for email format
#             pattern = r"^[a-zA-Z0-9.!#$%&*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
#             if not re.match(pattern, addr):
#                 return False, "Invalid email format"

#             # Domain validation
#             try:
#                 mx_records = dns.resolver.resolve(domain, 'MX')
#                 if not mx_records:
#                     return False, f"No mail server found for domain: {domain}"

#                 # Try SMTP connection with TLS
#                 mx_host = str(sorted(mx_records, key=lambda x: x.preference)[0].exchange)
#                 with smtplib.SMTP(mx_host, timeout=10) as smtp:
#                     smtp.starttls(context=ssl.create_default_context())
#                     smtp.ehlo()
#                     return True, None

#             except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
#                 return False, f"Domain does not exist: {domain}"
#             except Exception as e:
#                 logger.warning(f"SMTP check failed for {domain}: {str(e)}")
#                 return True, None  # Accept email if SMTP check fails

#         except Exception as e:
#             logger.error(f"Email validation error: {str(e)}")
#             return False, f"Validation error: {str(e)}"

#     def send_email_secure(
#         self,
#         to_email: str,
#         subject: str,
#         message: str,
#         cc_emails: Optional[List[str]] = None,
#         from_email: str = 'your-email@gmail.com',
#         template_name: str = 'email_template.html',
#         sender_ip: str = None
#     ) -> Tuple[bool, str]:
#         """
#         Secure email sending with comprehensive security measures
#         """
#         try:
#             # Generate tracking ID
#             tracking_id = get_random_string(32)
#             logger.info(f"Starting email send process. Tracking ID: {tracking_id}")

#             # Rate limiting
#             if sender_ip and not self.rate_limit_check(sender_ip):
#                 logger.warning(f"Rate limit exceeded for IP: {sender_ip}")
#                 return False, "Rate limit exceeded. Please try again later."

#             # Validate recipient count
#             cc_emails = cc_emails or []
#             if len(cc_emails) + 1 > self.email_security.MAX_RECIPIENTS:
#                 return False, f"Too many recipients. Maximum allowed: {self.email_security.MAX_RECIPIENTS}"

#             # Content length validation
#             if len(subject) > self.email_security.MAX_SUBJECT_LENGTH:
#                 return False, "Subject too long"
#             if len(message) > self.email_security.MAX_MESSAGE_LENGTH:
#                 return False, "Message too long"

#             # Validate primary recipient
#             is_valid, error = self.validate_email_advanced(to_email)
#             if not is_valid:
#                 logger.warning(f"Invalid primary recipient: {error}")
#                 return False, f'Invalid "To" email: {error}'

#             # Validate CC recipients
#             validated_cc_emails = []
#             for cc in cc_emails:
#                 cc = cc.strip()
#                 if cc:
#                     is_valid, error = self.validate_email_advanced(cc)
#                     if is_valid:
#                         validated_cc_emails.append(cc)
#                     else:
#                         logger.warning(f"Invalid CC recipient: {cc} - {error}")
#                         return False, f'Invalid CC email: {cc} ({error})'

#             # Sanitize and prepare content
#             subject = bleach.clean(subject, tags=[], strip=True)  # Remove any HTML from subject
#             message = bleach.clean(message, tags=[], strip=True)  # Clean the message body

#             # Ensure template rendering doesn't include any unwanted debug content
#             html_content = render_to_string(template_name, {'message': message})
#             html_content = self.sanitize_content(html_content)
#             text_content = strip_tags(html_content)  # Text version of the email body

#             # Create email message
#             email = EmailMultiAlternatives(
#                 subject=subject,
#                 body=text_content,  # Plain text version
#                 from_email=from_email,
#                 to=[to_email],
#                 cc=validated_cc_emails,
#                 headers={
#                     'X-Tracking-ID': tracking_id,
#                     'X-Priority': '3',
#                     'X-MSMail-Priority': 'Normal',
#                 }
#             )
#             email.attach_alternative(html_content, "text/html")  # Attach HTML version

#             # Send email with retry logic
#             max_retries = 3
#             for attempt in range(max_retries):
#                 try:
#                     email.send(fail_silently=False)
#                     logger.info(f"Email sent successfully. Tracking ID: {tracking_id}")
#                     return True, 'Email sent successfully!'
#                 except Exception as e:
#                     if attempt == max_retries - 1:
#                         logger.error(f"Final email send attempt failed: {str(e)}")
#                         return False, f'Failed to send email: {str(e)}'
#                     logger.warning(f"Email send attempt {attempt + 1} failed. Retrying...")

#         except Exception as e:
#             logger.error(f"Unexpected error in email service: {str(e)}")
#             return False, f'Email service error: {str(e)}'















# import re
# import dns.resolver
# import smtplib
# import socket
# from typing import Tuple, Optional, List
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags


# def validate_email_advanced(email: str) -> Tuple[bool, Optional[str]]:
#     """Validates an email address with format & domain checks."""
#     if '@' not in email:
#         return False, "Invalid email format"
    
#     local, domain = email.rsplit('@', 1)
#     if len(local) > 64 or len(domain) > 255:
#         return False, "Invalid email format (length issue)"
    
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     if not re.match(pattern, email):
#         return False, "Invalid email format"
    
#     try:
#         mx_records = dns.resolver.resolve(domain, 'MX')
#         if not mx_records:
#             return False, f"No mail server found for domain: {domain}"
        
#         mx_record = sorted(mx_records, key=lambda x: x.preference)[0]
#         mx_domain = mx_record.exchange.to_text().rstrip('.')
        
#         with smtplib.SMTP(mx_domain, 25, timeout=10) as smtp:
#             smtp.ehlo()
#             return True, None
            
#     except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout):
#         return False, f"Domain does not exist: {domain}"
#     except (socket.gaierror, socket.timeout, smtplib.SMTPException):
#         return True, None  # Acceptable failure case
#     except Exception as e:
#         return False, f"Validation error: {str(e)}"


# def send_email_secure(
#     to_email: str,
#     subject: str,
#     message: str,
#     cc_emails: Optional[List[str]] = None,  # Change parameter name to cc_emails
#     from_email: str = 'your-email@gmail.com',
#     template_name: str = 'email_template.html'
# ) -> Tuple[bool, str]:
#     """
#     Sends an email with multiple CC support.
#     """
#     # Validate primary recipient email
#     is_valid, error = validate_email_advanced(to_email)
#     if not is_valid:
#         return False, f'Invalid "To" email: {error}'

#     # Validate multiple CC emails
#     validated_cc_emails = []
#     if cc_emails:
#         for cc in cc_emails:
#             cc = cc.strip()  # Remove spaces
#             if cc:  # Ignore empty values
#                 is_valid, error = validate_email_advanced(cc)
#                 if is_valid:
#                     validated_cc_emails.append(cc)
#                 else:
#                     return False, f'Invalid CC email: {cc} ({error})'

#     try:
#         # Render HTML template
#         html_content = render_to_string(template_name, {'message': message})
#         text_content = strip_tags(html_content)

#         # Create email message
#         email = EmailMultiAlternatives(
#             subject=subject,
#             body=text_content,
#             from_email=from_email,
#             to=[to_email],
#             cc=validated_cc_emails,
#         )
#         email.attach_alternative(html_content, "text/html")
        
#         # Send email
#         email.send(fail_silently=False)
#         return True, 'Email sent successfully!'
        
#     except Exception as e:
#         return False, f'Failed to send email: {str(e)}'
