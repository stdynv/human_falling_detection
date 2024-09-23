import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_password_reset_email(user_email, reset_token):
    sender = "Protect Care <ProtectCare@gmail.com>"
    receiver = user_email

    # Create the reset link (you can adjust the URL based on your frontend)
    reset_link = f"https://flask-ehpad-fde5f2fndkd0f2gk.eastus-01.azurewebsites.net/reset-password?token={reset_token}"

    # Create the email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Request"
    message["From"] = sender
    message["To"] = receiver

    # Plain text version of the message
    text = f"""\
    Hi,
    You requested to reset your password. Click the link below to reset it:
    {reset_link}
    
    If you did not request this, please ignore this email.
    """

    # HTML version of the message
    html = f"""\
    <html>
    <body>
        <p>Hi,<br>
           You requested to reset your password. Click the link below to reset it:<br>
           <a href="{reset_link}">Reset Password</a>
        </p>
        <p>If you did not request this, please ignore this email.</p>
    </body>
    </html>
    """

    # Attach both plain text and HTML to the email
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # Send the email using Mailtrap
    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.starttls()
        server.login("5ca23688855e9a", "8286793f7b04b1")
        server.sendmail(sender, receiver, message.as_string())

