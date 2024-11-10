import os
import logging
import re
from flask import Flask, request, jsonify, abort
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv, set_key
from datetime import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor
import commands  # Import the custom commands file
import threading

# Suppress Flask's request log messages
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Set to ERROR to avoid INFO-level request logs

# Suppress Flask's 'Serving Flask app' and 'Debug mode' messages
flask_log = logging.getLogger('flask')
flask_log.setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # Secret key for secure session management

# Configure logging to a file
logging.basicConfig(
    filename="email_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()

# Dictionary to track the status of email requests
email_status = {}

# Email validation pattern
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

# Create a thread pool executor to manage the email sending asynchronously
executor = ThreadPoolExecutor(max_workers=5)

def log_email_to_file(request_id, sender_email, recipient, status):
    """Log email request details to a text file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"Request ID: {request_id}, Sender: {sender_email}, Recipient: {recipient}, Date: {now}, Status: {status}\n"
    # Buffer logs or write periodically
    with open("email_log.txt", "a") as log_file:
        log_file.write(log_message)

def send_email(subject, recipient, body, is_html, request_id, sender_email, sender_password, sender_name):
    """Send an email and log the action in a text file."""
    try:
        # Prepare the email
        message = MIMEMultipart()
        message["From"] = f"{sender_name} <{sender_email}>"
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "html" if is_html else "plain"))

        # Send the email
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)

        # Log success to the file
        log_email_to_file(request_id, sender_email, recipient, "sent")
        email_status[request_id] = "sent"  # Update the status
    except Exception as e:
        # Log failure to the file
        log_email_to_file(request_id, sender_email, recipient, f"failed ({e})")
        email_status[request_id] = f"failed ({e})"  # Update the status

def validate_email_data(data):
    """Validate the email data."""
    subject = data.get("subject")
    recipient = data.get("recipient")
    body = data.get("body")
    
    if not all([subject, recipient, body]):
        abort(400, description="Missing required fields")
    
    if not EMAIL_REGEX.match(recipient):
        abort(400, description="Invalid email format")
    
    if len(subject) > 255 or len(body) > 10000:
        abort(400, description="Subject or body exceeds character limits")

def check_and_set_credentials():
    """Check if the email credentials are set in the .env file, else prompt the user."""
    # Check if the necessary credentials are already in the environment
    if not os.getenv("USER_EMAIL"):
        user_email = input("Enter your email address: ")
        set_key('.env', 'USER_EMAIL', user_email)

    if not os.getenv("USER_APP_PASSWORD"):
        user_password = input("Enter your app password (use app-specific password if using Gmail): ")
        set_key('.env', 'USER_APP_PASSWORD', user_password)

    if not os.getenv("EMAIL_FROM_NAME"):
        from_name = input("Enter your email's sender name: ")
        set_key('.env', 'EMAIL_FROM_NAME', from_name)

@app.route("/send-email", methods=["POST"])
def handle_send_email():
    data = request.json
    validate_email_data(data)
    
    subject = data["subject"]
    recipient = data["recipient"]
    body = data["body"]
    is_html = data.get("is_html", False)

    # Get the email, password, and sender name from the environment variables
    sender_email = os.getenv("USER_EMAIL")
    sender_password = os.getenv("USER_APP_PASSWORD")
    sender_name = os.getenv("EMAIL_FROM_NAME")

    if not sender_email or not sender_password:
        return jsonify({"error": "Missing user credentials in .env"}), 400

    # Generate a unique request ID for this email request
    request_id = str(uuid.uuid4())

    # Send the email asynchronously using the thread pool
    executor.submit(send_email, subject, recipient, body, is_html, request_id, sender_email, sender_password, sender_name)

    return jsonify({"message": "Email request processed", "request_id": request_id}), 200

@app.route("/email-status/<request_id>", methods=["GET"])
def get_email_status(request_id):
    """Check the status of an email request."""
    status = email_status.get(request_id, "Request ID not found")
    return jsonify({"request_id": request_id, "status": status})

def interactive_terminal():
    """Interactive terminal to control server settings and view logs."""
    commands.interactive_terminal()  # Call the interactive terminal from commands.py

if __name__ == "__main__":
    # Check and set credentials if they don't exist in the .env file
    check_and_set_credentials()

    # Start the Flask server in a separate thread
    threading.Thread(target=lambda: app.run(debug=False, use_reloader=False)).start()
    
    # Call the interactive terminal for managing commands
    interactive_terminal()
