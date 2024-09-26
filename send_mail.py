import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_password_reset_email(user_email, reset_token):
    sender = "Protect Care <ProtectCare@gmail.com>"
    receiver = user_email

    reset_link = f"http://localhost:8000/reset-password?token={reset_token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Request"
    message["From"] = sender
    message["To"] = receiver

    # Plain text version
    text = f"""
    Hi,
    You requested to reset your password. Click the link below to reset it:
    {reset_link}

    If you did not request this, please ignore this email.
    """

    # Modern HTML version
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px; text-align: center;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #2c3e50;">Réinitialisation du mot de passe</h2>
            <p style="color: #34495e; font-size: 16px;">
                Hello,<br><br>
                Vous avez demandé à changer votre mot de passe. Cliquez sur le bouton ci dessous et suivez les instructions:
            </p>
            <a href="{reset_link}" style="display: inline-block; padding: 12px 24px; background-color: #3498db; color: #ffffff; text-decoration: none; border-radius: 5px; margin: 20px 0; font-size: 16px;">Reset Password</a>
            <p style="color: #7f8c8d; font-size: 14px;">
                Si vous n'avez émis aucune demande, ignorez ce mail.
            </p>
        </div>
        <footer style="margin-top: 20px; color: #95a5a6; font-size: 12px;">
            Protect Care &copy; 2024
        </footer>
    </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.starttls()
        server.login("5ca23688855e9a", "8286793f7b04b1")
        server.sendmail(sender, receiver, message.as_string())
