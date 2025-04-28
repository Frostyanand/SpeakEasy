import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get SMTP configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(to_email, subject, body):
    """
    Send an email using SMTP
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body text
        
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Raises:
        Exception: For any SMTP or connection errors
    """
    # Create email message
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    
    # Create secure SSL context
    context = ssl.create_default_context()
    
    # Send email
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
    
    return True

def send_booking_confirmation(user_email, speaker_email, session_details):
    """
    Send booking confirmation emails to both user and speaker
    
    Args:
        user_email (str): User's email address
        speaker_email (str): Speaker's email address
        session_details (dict): Details of the session including:
            - date: Session date
            - time: Session time
            - speaker_name: Full name of the speaker
            
    Returns:
        bool: True if both emails sent successfully, False otherwise
    """
    # Extract session details
    session_date = session_details.get("date")
    session_time = session_details.get("time")
    speaker_name = session_details.get("speaker_name")
    
    # Create email content for user
    user_subject = "Session Booking Confirmation - SpeakEasy"
    user_body = f"""Hi there,

This is a confirmation for your session booking.

Session Details:
Date: {session_date}
Time: {session_time}
Speaker: {speaker_name}

Thank you for using SpeakEasy!
"""
    
    # Create email content for speaker
    speaker_subject = "New Session Booking - SpeakEasy"
    speaker_body = f"""Hi {speaker_name},

You have a new session booking!

Session Details:
Date: {session_date}
Time: {session_time}

Please log in to your SpeakEasy account to view more details about the booking.

Thank you for using SpeakEasy!
"""
    
    # Send emails and catch any exceptions
    success = True
    
    try:
        # Send email to user
        send_email(user_email, user_subject, user_body)
    except Exception as e:
        print(f"Failed to send confirmation email to user: {e}")
        success = False
    
    try:
        # Send email to speaker
        send_email(speaker_email, speaker_subject, speaker_body)
    except Exception as e:
        print(f"Failed to send notification email to speaker: {e}")
        success = False
    
    return success 