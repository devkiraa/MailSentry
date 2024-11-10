import threading
import os
import signal
from flask import Flask
import psutil
from datetime import datetime
from dotenv import load_dotenv, set_key

# Load the .env file
load_dotenv()

# Assuming you have the Flask app object already initialized in your main script
app = Flask(__name__)

# Define the status of the email queue
email_status = {}

# Initialize email sending state (global variable)
email_sending_paused = False

def get_latest_logs():
    """Read and return the last 5 logs."""
    try:
        with open("email_log.txt", "r") as log_file:
            logs = log_file.readlines()
        return "".join(logs[-5:])  # Return the last 5 logs
    except FileNotFoundError:
        return "Log file not found."

def view_all_logs():
    """Display all logs from the email log file."""
    with open("email_log.txt", "r") as log_file:
        logs = log_file.readlines()
    return "".join(logs)

def change_ip_port():
    """Change the IP and port of the server."""
    print("Suggested IP and Port options:")
    print("1. 127.0.0.1:5001")
    print("2. 127.0.0.1:5002")
    print("3. 127.0.0.1:5003")
    print("4. 127.0.0.1:5004")
    
    new_ip = input("Enter new IP address (default 127.0.0.1): ").strip() or "127.0.0.1"
    new_port = input("Enter new port (suggested: 5001, 5002, 5003, 5004): ").strip() or "5001"
    
    try:
        new_port = int(new_port)
        print(f"Server will restart with IP: {new_ip} and Port: {new_port}")
        
        # Close the current Flask thread and start a new one with new settings
        threading.Thread(target=lambda: app.run(debug=False, host=new_ip, port=new_port, use_reloader=False)).start()
        
    except ValueError:
        print("Invalid port number.")

def shutdown_server():
    """Shut down the Flask server programmatically."""
    print("Shutting down the server...")
    os.kill(os.getpid(), signal.SIGINT)  # Simulate a CTRL+C to stop the Flask server

def check_pending_emails():
    """Check and display all pending emails."""
    pending_emails = {req_id: status for req_id, status in email_status.items() if "failed" in status or status == "pending"}
    if pending_emails:
        for req_id, status in pending_emails.items():
            print(f"Request ID: {req_id}, Status: {status}")
    else:
        print("No pending emails.")

def toggle_email_sending():
    """Pause or resume email sending."""
    global email_sending_paused
    email_sending_paused = not email_sending_paused
    print("Email sending is now", "paused." if email_sending_paused else "resumed.")

def view_active_connections():
    """Display active network connections."""
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        print(f"{conn.laddr} -> {conn.raddr} | Status: {conn.status}")

def email_queue_length():
    """Show the current email queue length."""
    print(f"Current email queue length: {len(email_status)}")

def clear_pending_emails():
    """Clear all pending or failed emails from the status log."""
    for req_id in list(email_status.keys()):
        if "failed" in email_status[req_id] or email_status[req_id] == "pending":
            del email_status[req_id]
    print("All pending emails cleared.")

def view_email_queue():
    """View the email queue with statuses."""
    if not email_status:
        print("No emails in the queue.")
    else:
        for req_id, status in email_status.items():
            print(f"Request ID: {req_id}, Status: {status}")

def export_email_logs():
    """Export the email logs to a file."""
    with open("email_log.txt", "r") as log_file:
        logs = log_file.read()
    with open(f"exported_email_logs_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as export_file:
        export_file.write(logs)
    print("Logs exported successfully.")

def server_health_check():
    """Display basic health metrics for the server."""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    print(f"CPU Usage: {cpu}%")
    print(f"Memory Usage: {memory.percent}%")

def reset_email_queue():
    """Clear all email status and reset the queue."""
    global email_status
    email_status.clear()
    print("Email queue has been reset.")

def set_email_credentials():
    """Set or update email credentials in the .env file."""
    print("Setting email credentials...")

    # Check if the email credentials already exist in the environment
    if not os.getenv("USER_EMAIL"):
        user_email = input("Enter your email address: ")
        set_key('.env', 'USER_EMAIL', user_email)

    if not os.getenv("USER_APP_PASSWORD"):
        user_password = input("Enter your app password (use app-specific password if using Gmail): ")
        set_key('.env', 'USER_APP_PASSWORD', user_password)

    if not os.getenv("EMAIL_FROM_NAME"):
        from_name = input("Enter your email's sender name: ")
        set_key('.env', 'EMAIL_FROM_NAME', from_name)

    print("Email credentials set successfully.")

def show_email_credentials():
    """Display current email credentials."""
    user_email = os.getenv("USER_EMAIL")
    user_password = os.getenv("USER_APP_PASSWORD")
    from_name = os.getenv("EMAIL_FROM_NAME")

    if user_email and user_password and from_name:
        print(f"User Email: {user_email}")
        print(f"Email From Name: {from_name}")
        print("App Password: ******** (not displayed for security reasons)")
    else:
        print("Credentials not set yet. Run 'set-email-credentials' first.")

def interactive_terminal():
    """Interactive terminal to control server settings and view logs."""
    while True:
        print("\nEnter a command:")
        print("1. View logs")
        print("2. Change IP/Port")
        print("3. Exit")
        print("Or type 'more' to see all available commands.")
        
        command = input("Please select an option (1-3 or 'more'): ").strip()

        if command == "1":
            logs = get_latest_logs()
            if logs:
                print(logs)
            else:
                print("No logs available.")
        
        elif command == "2":
            change_ip_port()  # Call the function for changing IP/Port
        
        elif command == "3":
            print("Exiting server.")
            shutdown_server()  # Shut down the server
            break
        
        elif command.lower() == "more":
            # Display all commands with new numbering and a back option
            while True:
                print("\nAdditional commands:")
                print("1. View all logs")
                print("2. Check pending emails")
                print("3. Toggle email sending")
                print("4. View active network connections")
                print("5. Show email queue length")
                print("6. Clear pending emails")
                print("7. View email queue")
                print("8. Export email logs to file")
                print("9. Server health check")
                print("10. Reset email queue")
                print("11. Set email credentials")
                print("12. Show email credentials")
                print("13. Go back")

                command = input("Please select an option (1-13): ").strip()

                if command == "1":
                    logs = view_all_logs()
                    print(logs)
                elif command == "2":
                    check_pending_emails()
                elif command == "3":
                    toggle_email_sending()
                elif command == "4":
                    view_active_connections()
                elif command == "5":
                    email_queue_length()
                elif command == "6":
                    clear_pending_emails()
                elif command == "7":
                    view_email_queue()
                elif command == "8":
                    export_email_logs()
                elif command == "9":
                    server_health_check()
                elif command == "10":
                    reset_email_queue()
                elif command == "11":
                    set_email_credentials()
                elif command == "12":
                    show_email_credentials()
                elif command == "13":
                    break  # Exit the "more" menu
                else:
                    print("Invalid option. Please try again.")
        else:
            print("Invalid option. Please try again.")
