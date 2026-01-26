import random
import string
from django.conf import settings
from django.core.mail import send_mail


def generate_verification_code(length=6):
    """Generate a random verification code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def send_sms_verification(phone_number, verification_code):
    """
    Send SMS verification using a service like Twilio
    This is a placeholder implementation
    """
    # In a real implementation, use a service like Twilio
    # For now, just print the code to console
    print(f"SMS verification code {verification_code} sent to {phone_number}")
    
    # Example with Twilio (uncomment when Twilio is configured):
    # if hasattr(settings, 'TWILIO_ACCOUNT_SID'):
    #     from twilio.rest import Client
    #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    #     
    #     message = client.messages.create(
    #         body=f'Your verification code is: {verification_code}',
    #         from_=settings.TWILIO_PHONE_NUMBER,
    #         to=phone_number
    #     )
    #     return message.sid
    # else:
    #     # Fallback: print to console
    #     print(f"SMS verification code {verification_code} sent to {phone_number}")