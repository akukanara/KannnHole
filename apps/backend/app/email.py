from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(user):
    if not user.email or not user.email_token:
        return False

    app = current_app
    verify_url = f"{app.config['BASE_URL']}/verify_email/{user.email_token}"

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
    msg['From'] = app.config['MAIL_DEFAULT_SENDER'][1]
    msg['To'] = user.email

    msg.attach(MIMEText("Please verify your email address", "plain"))  # fallback
    msg.attach(MIMEText(html, "html"))  # actual content

    try:
        if app.config.get("MAIL_USE_SSL"):
            server = smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        else:
            server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            if app.config.get("MAIL_USE_TLS"):
                server.starttls()

        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        app.logger.error(f"[Email] Failed to send verification email: {e}")
        return False
