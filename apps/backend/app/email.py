from config import Config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger("uvicorn.error")

def send_verification_email(user):
    if not user.email or not user.email_token:
        return False

    verify_url = f"{Config.BASE_URL}/verify_email/{user.email_token}"

    # HTML template
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <h2 style="color: #dc3545;">Kana Tunnel - Email Verification</h2>
          <p>Hi <strong>{user.username}</strong>,</p>
          <p>Please verify your email address by clicking the button below:</p>
          <p style="text-align: center;">
            <a href="{verify_url}" style="display: inline-block; padding: 10px 20px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px;">Verify Email</a>
          </p>
          <p>If you didn’t create this account, just ignore this message.</p>
          <p style="font-size: 0.9em; color: #888;">© 2025 Kana Tunnel</p>
        </div>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg['Subject'] = 'Verify Your Email'
    msg['From'] = Config.MAIL_DEFAULT_SENDER[1]
    msg['To'] = user.email

    msg.attach(MIMEText("Please verify your email address", "plain"))  # fallback
    msg.attach(MIMEText(html, "html"))  # actual content

    try:
        if Config.MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT)
        else:
            server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
            if Config.MAIL_USE_TLS:
                server.starttls()

        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        logger.error(f"[Email] Failed to send verification email: {e}")
        return False
