import random
from datetime import datetime

# Configured Admin Mobile Number for alerts
ADMIN_MOBILE_NUMBER = "+15550199"

def generate_otp() -> str:
    """Generates a random 6-digit numeric OTP code."""
    return f"{random.randint(100000, 999999)}"

def send_sms(to_mobile: str, message: str) -> bool:
    """
    Mock SMS gateway delivery. Logs the message clearly to the console log/terminal.
    Returns True indicating successful delivery.
    """
    border = "=" * 60
    # Use ASCII for standard print to avoid UnicodeEncodeError in Windows consoles
    console_msg = (
        f"\n{border}\n"
        f"[MOCK SMS GATEWAY] OUTBOUND SMS\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"To: {to_mobile}\n"
        f"Message: {message}\n"
        f"{border}\n"
    )
    print(console_msg)
    
    # Emojis are safe to write to file with explicit utf-8 encoding
    log_msg = (
        f"\n{border}\n"
        f"📱 [MOCK SMS GATEWAY] OUTBOUND SMS\n"
        f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"📤 To: {to_mobile}\n"
        f"💬 Message: {message}\n"
        f"{border}\n"
    )
    try:
        with open("sms_gateway_log.txt", "a", encoding="utf-8") as f:
            f.write(log_msg)
    except Exception:
        pass
    return True

def send_otp(to_mobile: str, otp: str) -> bool:
    """Sends the OTP code to the provided mobile number."""
    message = f"Your TaskTracker Pro security code is: {otp}. This code is valid for 5-10 minutes. Please do not share it."
    return send_sms(to_mobile, message)

def send_admin_new_registration_notification(new_user_name: str, email: str, mobile: str) -> bool:
    """Sends an alert to the Admin Mobile Number regarding a new registration."""
    message = (
        f"[ADMIN ALERT] New Registration Submitted!\n"
        f"- Full Name: {new_user_name}\n"
        f"- Email/Username: {email}\n"
        f"- Mobile: {mobile}\n"
        f"- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    return send_sms(ADMIN_MOBILE_NUMBER, message)
