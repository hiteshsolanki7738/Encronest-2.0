import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from config import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
    TWILIO_SID,
    TWILIO_AUTH,
    TWILIO_PHONE
)

# ---------------------------
# Generate 6-digit OTP
# ---------------------------
def generate_otp():
    return str(random.randint(100000, 999999))


# ---------------------------
# Send Email (FAST + SAFE)
# ---------------------------
def send_email_otp(to_email, message_text):
    try:
        if not to_email:
            return False

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = "ENCRONEST Secure Notification"

        msg.attach(MIMEText(message_text, "plain"))

        # Use timeout to prevent freeze
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=5)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        print("Email Error:", e)
        return False


# ---------------------------
# Send SMS (FAST + SAFE)
# ---------------------------
def send_sms_otp(to_phone, otp):
    try:
        if not to_phone:
            return False

        client = Client(TWILIO_SID, TWILIO_AUTH)

        client.messages.create(
            body=f"ENCRONEST OTP: {otp}",
            from_=TWILIO_PHONE,
            to=to_phone.strip()
        )

        return True

    except Exception as e:
        print("SMS Error:", e)
        return False


# ---------------------------
# Verify OTP
# ---------------------------
def verify_otp(user_otp, actual_otp):
    if not user_otp or not actual_otp:
        return False
    return user_otp.strip() == actual_otp.strip()