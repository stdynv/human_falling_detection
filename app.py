from flask import Flask, render_template, request, flash, redirect, url_for, current_app
from flask_cors import CORS
import socket
from extensions import db, socketio
import logging
from config import Config  # Ensure this path is correct as per your project structure
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import send_mail as mail

from itsdangerous import URLSafeTimedSerializer
# Configure logging
logging.basicConfig(level=logging.INFO)


app = Flask(__name__)


app.config.from_object(
    Config
)

app.secret_key = 'your-unique-secret-key'


def generate_password_reset_token(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user.email, salt='password-reset-salt')

def verify_password_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return User.query.filter_by(email=email).first()


# Initialize the SQLAlchemy extension with the Flask app
db.init_app(app) 

socketio.init_app(
    app,
    cors_allowed_origins="*",
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
)
CORS(app)  # Enable CORS

# Blueprint imports and registration
from routes.rooms import rooms_bp
from routes.incidents import incidents_bp
from routes.staff import staff_bp
from routes.auth import auth_bp , token_required

from models import Ehpad as User



# Register the Blueprints with the Flask app
app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
app.register_blueprint(incidents_bp, url_prefix='/api/incidents')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/')
def login_page():
    return render_template('auth-login-basic.html')

@app.route('/auth-forgot-password-basic', methods=['GET'])
def forgot_password_page():
    return render_template('auth-forgot-password-basic.html')


@app.route('/auth-forgot-password-basic', methods=['POST'])
def forgot_password():
    email = request.form.get('email')

    if not email:
        flash('Please enter a valid email address', 'danger')
        return redirect(url_for('auth-forgot-password-basic'))

    user = User.query.filter_by(email=email).first()
    if user:
        token = generate_password_reset_token(user)
        mail.send_password_reset_email(user.email, token)
        flash('Password reset link has been sent to your email.', 'success')
    else:
        flash('No user with that email found.', 'danger')

    return redirect(url_for('login_page'))


@app.route('/chambres')
def chambres_page():
    
    return render_template('chambres.html')


@app.route('/chambre/<string:room_number>')
def chambre_page(room_number):
    room = Room.query.filter_by(room_number=room_number).first()
    if room is None:
        return "Room not found", 404
    return render_template('chambre.html', room=room)



@app.route('/tables-basic')
def tables_page():
    hostname = socket.gethostname()
    # return render_template("main.html", socket_url=hostname)
    return render_template('tables-basic.html',socket_url=hostname)

import smtplib
@app.route('/contact-submit', methods=['POST'])
def contact_submit():
    # Extract form data
    name = request.form['name']
    email = request.form['email']
    room = request.form['room']
    subject = request.form['subject']
    message_content = request.form['message']
    priority = request.form['priority']

    # Sender and Receiver
    sender = f"Protect Care <{email}>"
    receiver = "nabilhatri8@gmail.com"

    # Create a multipart email (to handle both plain text and HTML)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    # Create the plain-text and HTML version of your message
    text = f"""
    Nouvelle réclamation reçue
    Nom: {name}
    Email: {email}
    Chambre concernée: {room}
    Sujet: {subject}
    Niveau de priorité: {priority}
    Message:
    {message_content}
    """
    
    html = f"""\ 
    <html>
        <body>
            <h2>Nouvelle réclamation reçue</h2>
            <p><strong>Nom:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Chambre concernée:</strong> {room}</p>
            <p><strong>Sujet:</strong> {subject}</p>
            <p><strong>Niveau de priorité:</strong> {priority}</p>
            <p><strong>Message:</strong></p>
            <p>{message_content}</p>
            <br>
            <p>Merci,</p>
            <p><em>Protect Care - Détection de Chute</em></p>
        </body>
    </html>
    """

    # Attach both plain-text and HTML versions to the email
    part1 = MIMEText(text, "plain", "utf-8")
    part2 = MIMEText(html, "html", "utf-8")
    
    msg.attach(part1)
    msg.attach(part2)

    # Send the email via Mailtrap
    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.starttls()
        server.login("5ca23688855e9a", "8286793f7b04b1")
        server.sendmail(sender, receiver, msg.as_string())

    return "Email sent successfully!"

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    
    if request.method == 'POST':
        # Handle the password reset logic
        new_password = request.form.get('new_password')
        user = verify_password_reset_token(token)  # Define this function
        if user:
            user.set_password(new_password)  # Assuming you have a set_password method
            db.session.commit()
            flash('Your password has been reset!', 'success')
            return redirect(url_for('login_page'))
        else:
            flash('The reset link is invalid or has expired.', 'danger')
    
    return render_template('auth-reset-password.html', token=token)



from models import Room
@app.route('/contact')
def contact_page():
    rooms = Room.query.all()  # Récupère toutes les chambres
    return render_template('contact.html', rooms=rooms)


# Run the app using eventlet
if __name__ == "__main__":
    # Ensure eventlet works properly with other libraries
    socketio.run(app, debug=True, host="0.0.0.0",port=8000)
