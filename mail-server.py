import os
import logging
import threading
import csv
import re
from flask import Flask, request, jsonify, abort
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import datetime
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Suppress Flask's request log messages
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)  # Set to ERROR to avoid INFO-level request logs

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # Secret key for secure session management

# Configure rate limiting (e.g., 5 requests per minute per IP)
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

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

# Function to load users from CSV file
def load_user_data():
    users = []
    try:
        with open("data.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(row)
    except Exception as e:
        logger.error(f"Error loading users from CSV: {e}")
    return users

# Function to find the user by key
def get_user_by_key(key):
    users = load_user_data()
    for user in users:
        if user["key"] == key:
            return user
    return None

def log_email_to_file(request_id, sender_email, recipient, status):
    """Log email request details to a text file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"Request ID: {request_id}, Sender: {sender_email}, Recipient: {recipient}, Date: {now}, Status: {status}\n"
    with open("email_log.txt", "a") as log_file:
        log_file.write(log_message)

def send_email(subject, recipient, body, is_html, request_id, sender_email, sender_password):
    """Send an email and log the action in a text file."""
    try:
        # Prepare the email
        message = MIMEMultipart()
        message["From"] = sender_email
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

def handle_send_email_async(subject, recipient, body, is_html, request_id, sender_email, sender_password):
    """Wrapper to send the email in a separate thread."""
    thread = threading.Thread(target=send_email, args=(subject, recipient, body, is_html, request_id, sender_email, sender_password))
    thread.start()

def validate_email_data(data):
    """Validate the email data."""
    subject = data.get("subject")
    recipient = data.get("recipient")
    body = data.get("body")
    key = data.get("key")
    
    if not all([subject, recipient, body, key]):
        abort(400, description="Missing required fields")
    
    if not EMAIL_REGEX.match(recipient):
        abort(400, description="Invalid email format")
    
    if len(subject) > 255 or len(body) > 10000:
        abort(400, description="Subject or body exceeds character limits")

@app.route("/send-email", methods=["POST"])
@limiter.limit("5 per minute")
def handle_send_email():
    data = request.json
    validate_email_data(data)
    
    subject = data["subject"]
    recipient = data["recipient"]
    body = data["body"]
    is_html = data.get("is_html", False)
    key = data["key"]

    # Get user details by key
    user = get_user_by_key(key)
    if not user:
        return jsonify({"error": "Invalid key"}), 400

    # Get the email and password from the user data
    sender_email = user["email"]
    sender_password = user["app_password"]

    # Generate a unique request ID for this email request
    request_id = str(uuid.uuid4())

    # Send the email asynchronously using the sender's credentials
    handle_send_email_async(subject, recipient, body, is_html, request_id, sender_email, sender_password)

    return jsonify({"message": "Email request is being processed", "request_id": request_id}), 200

@app.route("/email-status/<request_id>", methods=["GET"])
def get_email_status(request_id):
    """Check the status of an email request."""
    status = email_status.get(request_id, "Request ID not found")
    return jsonify({"request_id": request_id, "status": status})

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)  # Disables automatic reloader logs
