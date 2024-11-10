import threading
import os
import sys
import signal
import psutil
import csv
from datetime import datetime
from dotenv import load_dotenv, set_key

# Load the .env file
load_dotenv()

# Path to the CSV file containing email logs
CSV_FILE_PATH = "email_log.csv"

email_status = {}
email_sending_paused = False

def print_separator():
    print("══════════════════════════════════════════════════════════════════")

def print_section(title):
    print_separator()
    print(f"                      🚀 {title} 🚀")
    print_separator()

def get_latest_logs():
    """Retrieve the latest 5 logs, showing only Recipient, Date, and Status."""
    try:
        with open(CSV_FILE_PATH, "r") as csv_file:
            reader = list(csv.reader(csv_file))
            logs = reader[-5:]  # Get the last 5 logs
            
            # Display only Recipient, Date, and Status columns
            latest_logs = [
                {"Recipient": log[2], "Date": log[4], "Status": log[5]}
                for log in logs[1:]  # Skip header row
            ]
            return latest_logs
    except FileNotFoundError:
        return "Log file not found."

def view_all_logs():
    """Retrieve all logs, showing only Recipient, Date, and Status."""
    try:
        with open(CSV_FILE_PATH, "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header row
            all_logs = [
                {"Recipient": row[2], "Date": row[4], "Status": row[5]}
                for row in reader
            ]
            return all_logs
    except FileNotFoundError:
        return "Log file not found."

def change_ip_port():
    pass  # Keep as-is for this example

def shutdown_server():
    print("Shutting down the server...")
    os.kill(os.getpid(), signal.SIGINT)

def restart_server():
    print("Restarting the server...")
    os.execl(sys.executable, sys.executable, *sys.argv)

def check_pending_emails():
    pending_emails = {req_id: status for req_id, status in email_status.items() if "failed" in status or status == "pending"}
    if pending_emails:
        for req_id, status in pending_emails.items():
            print(f"Request ID: {req_id}, Status: {status}")
    else:
        print("No pending emails.")

def toggle_email_sending():
    global email_sending_paused
    email_sending_paused = not email_sending_paused
    print("Email sending is now", "paused." if email_sending_paused else "resumed.")

def view_active_connections():
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        print(f"{conn.laddr} -> {conn.raddr} | Status: {conn.status}")

def email_queue_length():
    print(f"Current email queue length: {len(email_status)}")

def clear_pending_emails():
    for req_id in list(email_status.keys()):
        if "failed" in email_status[req_id] or email_status[req_id] == "pending":
            del email_status[req_id]
    print("All pending emails cleared.")

def view_email_queue():
    if not email_status:
        print("No emails in the queue.")
    else:
        for req_id, status in email_status.items():
            print(f"Request ID: {req_id}, Status: {status}")

def export_email_logs():
    try:
        with open(CSV_FILE_PATH, "r") as csv_file:
            logs = csv_file.read()
        with open(f"exported_email_logs_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv", "w") as export_file:
            export_file.write(logs)
        print("Logs exported successfully.")
    except FileNotFoundError:
        print("Log file not found.")

def server_health_check():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    print(f"CPU Usage: {cpu}%")
    print(f"Memory Usage: {memory.percent}%")

def reset_email_queue():
    global email_status
    email_status.clear()
    print("Email queue has been reset.")

def set_email_credentials():
    print("Setting email credentials...")
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
    """Interactive terminal with categorized commands."""
    while True:
        print_section("Main Menu")
        print("1. Home 🏠")
        print("2. Settings ⚙️")
        print("3. Exit ❌")

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":  # Home Menu
            while True:
                print_section("Home")
                print("1. View recent logs 📑")
                print("2. Check pending emails 🕓")
                print("3. View email queue 📧")
                print("4. View active network connections 🌐")
                print("5. Export email logs 📤")
                print("6. Go back 🔙")

                home_choice = input("Select an option (1-6): ").strip()

                if home_choice == "1":
                    logs = get_latest_logs()
                    print_section("Recent Email Logs")
                    for log in logs:
                        print(f"Recipient: {log['Recipient']}, Date: {log['Date']}, Status: {log['Status']}")
                elif home_choice == "2":
                    check_pending_emails()
                elif home_choice == "3":
                    view_email_queue()
                elif home_choice == "4":
                    view_active_connections()
                elif home_choice == "5":
                    export_email_logs()
                elif home_choice == "6":
                    break
                else:
                    print("Invalid choice, please try again.")

        elif choice == "2":  # Settings Menu
            while True:
                print_section("Settings")
                print("1. Change IP/Port")
                print("2. Toggle email sending")
                print("3. Show email queue length")
                print("4. Clear pending emails")
                print("5. Reset email queue")
                print("6. Server health check")
                print("7. Set email credentials")
                print("8. Show email credentials")
                print("9. View all logs")
                print("10. Restart server")
                print("11. Go back")

                settings_choice = input("Select an option (1-11): ").strip()

                if settings_choice == "1":
                    change_ip_port()
                elif settings_choice == "2":
                    toggle_email_sending()
                elif settings_choice == "3":
                    email_queue_length()
                elif settings_choice == "4":
                    clear_pending_emails()
                elif settings_choice == "5":
                    reset_email_queue()
                elif settings_choice == "6":
                    server_health_check()
                elif settings_choice == "7":
                    set_email_credentials()
                elif settings_choice == "8":
                    show_email_credentials()
                elif settings_choice == "9":
                    logs = view_all_logs()
                    print_section("All Email Logs")
                    for log in logs:
                        print(f"Recipient: {log['Recipient']}, Date: {log['Date']}, Status: {log['Status']}")
                elif settings_choice == "10":
                    restart_server()
                elif settings_choice == "11":
                    break
                else:
                    print("Invalid choice, please try again.")

        elif choice == "3":  # Exit
            print("Exiting server.")
            shutdown_server()
            break
        else:
            print("Invalid choice, please try again.")
