import os
import smtplib
import ssl
import uuid
from email.message import EmailMessage
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Get SMTP configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(to_email, subject, body, is_html=False, attachments=None):
    """
    Send an email using SMTP
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body (text or HTML)
        is_html (bool): Whether the body is HTML
        attachments (list, optional): List of attachment tuples (filename, content, mimetype)
        
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Raises:
        Exception: For any SMTP or connection errors
    """
    # Create email message
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    
    # Set UTF-8 encoding for the message
    msg.set_charset('utf-8')
    
    # Attach content
    if is_html:
        msg.attach(MIMEText(body, 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Add attachments if provided
    if attachments:
        for attachment in attachments:
            filename, content, mimetype = attachment
            part = MIMEBase(*mimetype.split('/'))
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
    
    # Create secure SSL context
    context = ssl.create_default_context()
    
    # Send email
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
    
    return True

def send_otp_email(user_email, otp_code, first_name):
    """
    Send OTP verification email to a user
    
    Args:
        user_email (str): User's email address
        otp_code (str): The OTP code to send
        first_name (str): User's first name
    
    Returns:
        bool: True if email sent successfully
    """
    subject = "SpeakEasy OTP Verification"
    
    body = f"""Hi {first_name},

Thank you for signing up on SpeakEasy!

Your One-Time Password (OTP) for account verification is: {otp_code}

This OTP is valid for 10 minutes.

Welcome aboard!
- SpeakEasy Team
"""
    
    try:
        send_email(user_email, subject, body)
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False

def generate_calendar_invite(session_details, speaker_name, user_name=None):
    """
    Generate an iCalendar (.ics) file for a booked session
    
    Args:
        session_details (dict): Details of the session including date and time
        speaker_name (str): Name of the speaker
        user_name (str, optional): Name of the user
        
    Returns:
        tuple: (filename, content, mimetype) or None if generation fails
    """
    try:
        # Extract session details
        session_date = session_details.get("date")
        session_time = session_details.get("time")
        
        # Convert date and time strings to datetime objects
        session_start = datetime.strptime(f"{session_date} {session_time}", "%Y-%m-%d %H:%M")
        session_end = session_start + timedelta(hours=1)  # 1-hour session
        
        # Format timestamps for iCalendar (in UTC format)
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        # Format local time with timezone designator
        dtstart = session_start.strftime("%Y%m%dT%H%M%S")
        dtend = session_end.strftime("%Y%m%dT%H%M%S")
        
        # Generate unique identifier
        uid = str(uuid.uuid4())
        
        # Format date for more readable filename
        formatted_date = session_start.strftime("%Y%m%d-%H%M")
        
        # Create descriptive summary and details
        summary = f"SpeakEasy Session with {speaker_name}"
        description = f"Your SpeakEasy session with {speaker_name}\nDate: {session_date}\nTime: {session_time}\n"
        if user_name:
            description += f"Participant: {user_name}\n"
        description += "\nThis is an automated calendar invite from SpeakEasy."
        
        # Create the iCalendar content with proper line endings (CRLF)
        # Escape newlines first
        escaped_description = description.replace('\n', '\\n')

        # Create the iCalendar content with proper line endings (CRLF)
        ical_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//SpeakEasy//Calendar//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:REQUEST",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{escaped_description}",
            "LOCATION:Online Meeting",
            "ORGANIZER;CN=SpeakEasy:mailto:no-reply@speakeasy.com",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "TRIGGER:-PT15M",
            "END:VALARM",
            "END:VEVENT",
            "END:VCALENDAR"
        ]
        
        # Join with proper line endings for calendar files
        ical_content = "\r\n".join(ical_lines)
        
        # Define a descriptive filename
        filename = f"SpeakEasy_Session_{formatted_date}.ics"
        
        return (filename, ical_content, "text/calendar")
    
    except Exception as e:
        print(f"Failed to generate calendar invite: {e}")
        return None

def send_booking_confirmation(user_email, speaker_email, session_details, user_name=None):
    """
    Send booking confirmation emails to both user and speaker using HTML templates
    
    Args:
        user_email (str): User's email address
        speaker_email (str): Speaker's email address
        session_details (dict): Details of the session including:
            - date: Session date
            - time: Session time
            - speaker_name: Full name of the speaker
        user_name (str, optional): Name of the user who made the booking
            
    Returns:
        bool: True if both emails sent successfully, False otherwise
    """
    # Extract session details
    session_date = session_details.get("date")
    session_time = session_details.get("time")
    speaker_name = session_details.get("speaker_name")
    
    # Read HTML templates
    try:
        with open("templates/emails/booking_confirmation_user.html", "r") as file:
            user_template = file.read()
        
        with open("templates/emails/booking_confirmation_speaker.html", "r") as file:
            speaker_template = file.read()
    except Exception as e:
        print(f"Failed to read email templates: {e}")
        return False
    
    # Replace placeholders in user template
    user_html = user_template.replace("{{ speaker_name }}", speaker_name)
    user_html = user_html.replace("{{ session_date }}", session_date)
    user_html = user_html.replace("{{ session_time }}", session_time)
    
    # Replace placeholders in speaker template
    speaker_html = speaker_template.replace("{{ speaker_name }}", speaker_name)
    speaker_html = speaker_html.replace("{{ session_date }}", session_date)
    speaker_html = speaker_html.replace("{{ session_time }}", session_time)
    speaker_html = speaker_html.replace("{{ user_name }}", user_name or "A user")
    speaker_html = speaker_html.replace("{{ user_email }}", user_email)
    
    # Create email subject lines
    user_subject = "Session Booking Confirmation - SpeakEasy"
    speaker_subject = "New Session Booking - SpeakEasy"
    
    # Generate calendar invites
    calendar_invite = generate_calendar_invite(session_details, speaker_name, user_name)
    
    # Send emails and catch any exceptions
    success = True
    
    try:
        # Send HTML email to user with calendar attachment
        attachments = [calendar_invite] if calendar_invite else None
        send_email(user_email, user_subject, user_html, is_html=True, attachments=attachments)
    except Exception as e:
        print(f"Failed to send confirmation email to user: {e}")
        success = False
    
    try:
        # Send HTML email to speaker with calendar attachment
        attachments = [calendar_invite] if calendar_invite else None
        send_email(speaker_email, speaker_subject, speaker_html, is_html=True, attachments=attachments)
    except Exception as e:
        print(f"Failed to send notification email to speaker: {e}")
        success = False
    
    return success

def send_feedback_confirmation(user_email, speaker_email, session_details, user_name, rating, feedback_text=None):
    """
    Send feedback confirmation emails to both user and speaker using HTML templates
    
    Args:
        user_email (str): User's email address
        speaker_email (str): Speaker's email address
        session_details (dict): Details of the session including:
            - date: Session date
            - time: Session time
            - speaker_name: Full name of the speaker
        user_name (str): Name of the user who submitted feedback
        rating (int): Rating from 1 to 5
        feedback_text (str, optional): Text feedback
            
    Returns:
        bool: True if both emails sent successfully, False otherwise
    """
    # Extract session details
    session_date = session_details.get("date")
    session_time = session_details.get("time")
    speaker_name = session_details.get("speaker_name")
    
    print(f"Preparing feedback emails with: User={user_name}, Speaker={speaker_name}, Rating={rating}")
    
    # Read HTML templates
    try:
        with open("templates/emails/feedback_confirmation.html", "r", encoding='utf-8') as file:
            user_template = file.read()
            print("Successfully loaded user feedback template")
        
        with open("templates/emails/feedback_confirmation_speaker.html", "r", encoding='utf-8') as file:
            speaker_template = file.read()
            print("Successfully loaded speaker feedback template")
    except Exception as e:
        print(f"Failed to read feedback email templates: {str(e)}")
        return False
    
    try:
        # Generate star rating HTML
        stars_html = "⭐" * rating
        rating_html = f'{stars_html} <span>({rating}/5)</span>'
        
        # Replace placeholders in user template
        user_html = user_template.replace("{{ recipient_name }}", user_name)
        user_html = user_html.replace("{{ speaker_name }}", speaker_name)
        user_html = user_html.replace("{{ session_date }}", session_date)
        user_html = user_html.replace("{{ session_time }}", session_time)
        user_html = user_html.replace("{{ rating }}", str(rating))
        user_html = user_html.replace('{% for i in range(rating) %}⭐{% endfor %}', stars_html)
        
        # Handle feedback text section
        if feedback_text:
            user_html = user_html.replace("{{ feedback_text }}", feedback_text)
            user_html = user_html.replace("{% if feedback_text %}", "")
            user_html = user_html.replace("{% endif %}", "")
        else:
            feedback_section_start = user_html.find("{% if feedback_text %}")
            feedback_section_end = user_html.find("{% endif %}") + len("{% endif %}")
            if feedback_section_start >= 0 and feedback_section_end > 0:
                feedback_section = user_html[feedback_section_start:feedback_section_end]
                user_html = user_html.replace(feedback_section, "")
        
        # Replace placeholders in speaker template
        speaker_html = speaker_template.replace("{{ speaker_name }}", speaker_name)
        speaker_html = speaker_html.replace("{{ session_date }}", session_date)
        speaker_html = speaker_html.replace("{{ session_time }}", session_time)
        speaker_html = speaker_html.replace("{{ user_name }}", user_name)
        speaker_html = speaker_html.replace("{{ rating }}", str(rating))
        speaker_html = speaker_html.replace('{% for i in range(rating) %}⭐{% endfor %}', stars_html)
        
        # Handle feedback text section in speaker template
        if feedback_text:
            speaker_html = speaker_html.replace("{{ feedback_text }}", feedback_text)
            speaker_html = speaker_html.replace("{% if feedback_text %}", "")
            speaker_html = speaker_html.replace("{% endif %}", "")
        else:
            feedback_section_start = speaker_html.find("{% if feedback_text %}")
            feedback_section_end = speaker_html.find("{% endif %}") + len("{% endif %}")
            if feedback_section_start >= 0 and feedback_section_end > 0:
                feedback_section = speaker_html[feedback_section_start:feedback_section_end]
                speaker_html = speaker_html.replace(feedback_section, "")
        
        print("Successfully processed templates and replaced placeholders")
    except Exception as e:
        print(f"Error processing template placeholders: {str(e)}")
        return False
    
    # Create email subject lines
    user_subject = "Feedback Confirmation - SpeakEasy"
    speaker_subject = "New Session Feedback - SpeakEasy"
    
    # Send emails and catch any exceptions
    success = True
    
    try:
        # Send HTML email to user
        print(f"Attempting to send feedback confirmation to user: {user_email}")
        send_email(user_email, user_subject, user_html, is_html=True)
        print("Successfully sent feedback confirmation to user")
    except Exception as e:
        print(f"Failed to send feedback confirmation email to user: {str(e)}")
        success = False
    
    try:
        # Send HTML email to speaker
        print(f"Attempting to send feedback notification to speaker: {speaker_email}")
        send_email(speaker_email, speaker_subject, speaker_html, is_html=True)
        print("Successfully sent feedback notification to speaker")
    except Exception as e:
        print(f"Failed to send feedback notification email to speaker: {str(e)}")
        success = False
    
    return success 