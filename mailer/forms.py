from django import forms

class EmailForm(forms.Form):
    to_email = forms.EmailField(label="Recipient Email", required=True)
    cc_email = forms.CharField(
        label="CC Emails (comma-separated)", 
        required=False, 
        help_text="Enter multiple CC emails separated by commas"
    )
    subject = forms.CharField(label="Subject", max_length=255, required=True)
    message = forms.CharField(label="Message", widget=forms.Textarea, required=True)
