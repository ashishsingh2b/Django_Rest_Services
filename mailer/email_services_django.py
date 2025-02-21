import re
import dns.resolver
import smtplib
import socket
from typing import Tuple, Optional, List
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ImproperlyConfigured


class SecureEmailService:

    @staticmethod
    def validate_email_advanced(email: str) -> Tuple[bool, Optional[str]]:
        """Validates an email address with format & domain checks."""
        if '@' not in email:
            return False, "Invalid email format"
        
        local, domain = email.rsplit('@', 1)
        if len(local) > 64 or len(domain) > 255:
            return False, "Invalid email format (length issue)"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                return False, f"No mail server found for domain: {domain}"
            
            mx_record = sorted(mx_records, key=lambda x: x.preference)[0]
            mx_domain = mx_record.exchange.to_text().rstrip('.')
            
            with smtplib.SMTP(mx_domain, 25, timeout=10) as smtp:
                smtp.ehlo()
                return True, None
                
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout):
            return False, f"Domain does not exist: {domain}"
        except (socket.gaierror, socket.timeout, smtplib.SMTPException):
            return True, None  # Acceptable failure case
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def send_email_secure(
        to_email: str,
        subject: str,
        message: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        from_email: str = 'your-email@gmail.com',
        template_name: str = 'email_template.html',
        sender_ip: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Sends an email with a properly formatted HTML template.
        - If `jobs` is provided, it sends job listings.
        - If `message` is provided, it sends a normal email.
        """

        # Validate "To" email
        is_valid, error = SecureEmailService.validate_email_advanced(to_email)
        if not is_valid:
            return False, f'Invalid "To" email: {error}'

        # Validate CC emails
        validated_cc_emails = []
        if cc_emails:
            for cc in cc_emails:
                cc = cc.strip()
                if cc:
                    is_valid, error = SecureEmailService.validate_email_advanced(cc)
                    if is_valid:
                        validated_cc_emails.append(cc)
                    else:
                        return False, f'Invalid CC email: {cc} ({error})'

        # Render HTML template
        try:
            html_content = render_to_string(template_name, {
                'subject': subject,
                'message': message,
            })
        except Exception as e:
            return False, f"Template error: {str(e)}"

        text_content = strip_tags(html_content)  # Fallback for non-HTML email clients

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email],
            cc=validated_cc_emails,
        )
        email.attach_alternative(html_content, "text/html")

        try:
            if sender_ip:
                pass  # Optionally log sender IP
            
            email.send(fail_silently=False)
            return True, 'Email sent successfully!'
        
        except smtplib.SMTPException as e:
            return False, f'SMTP error: {str(e)}'
        except Exception as e:
            return False, f'Failed to send email: {str(e)}'
