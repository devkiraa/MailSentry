# Email Server Project

This project is a Flask-based REST API that allows users to send emails asynchronously and check the status of email requests. It retrieves user details from a CSV file, authenticates with Gmail, and handles email dispatch in a separate thread. Each request is assigned a unique ID and logged for easy tracking.

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Logging](#logging)
- [Security Considerations](#security-considerations)
- [Future Improvements](#future-improvements)

## Project Structure

- `mail_server.py`: Main file containing the API implementation.
- `data.csv`: CSV file containing user data (email, app password, and key).
- `email_log.txt`: Log file that records email requests.
- `.env`: Environment file to store sensitive credentials.

## Requirements

To run this project, you'll need:

- Python 3.7+
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833) for each email account sending emails (due to Gmail's security requirements).
- Required Python packages (see below).

### Python Packages

Install the necessary packages by running:

```bash
pip install flask python-dotenv
```

If you plan to use Redis or Memcached for production rate-limiting, additional packages like `redis` or `memcache` might be needed.

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd email-server
   ```

2. **Set up the CSV file (`data.csv`)**:

   Create a CSV file named `data.csv` in the project directory with columns as shown below:

   ```csv
   key,email,app_password
   user1_key,example1@gmail.com,your_app_password
   user2_key,example2@gmail.com,another_app_password
   ```

   - **key**: Unique key for each user.
   - **email**: Gmail address of the sender.
   - **app_password**: Gmail app password for authentication.

3. **Create `.env` File**:

   Store any additional environment variables, such as `FLASK_ENV` if needed, in a `.env` file.

4. **Configure Gmail**:

   Ensure each email account used in the CSV file has an [App Password](https://support.google.com/accounts/answer/185833) for secure access.

## Environment Variables

- `.env`: Load any additional environment variables using the `.env` file.

## Usage

Start the Flask application:

```bash
python mail_server.py
```

The server should start on `http://127.0.0.1:5000`. It provides two endpoints: one to send an email and another to check the status of an email request.

## Endpoints

### 1. Send Email

**Endpoint**: `POST /send-email`

**Description**: Send an email to a specified recipient.

#### Request Body

- `subject` (string): Subject of the email.
- `recipient` (string): Recipient email address.
- `body` (string): Body content of the email.
- `is_html` (boolean): Optional. Set `true` if the body is in HTML format; defaults to `false`.
- `key` (string): Unique key associated with the user (defined in `data.csv`).

#### Example Request

```json
POST /send-email
{
  "subject": "Welcome to Our Service",
  "recipient": "user@example.com",
  "body": "<h1>Hello!</h1> Thanks for joining us.",
  "is_html": true,
  "key": "user1_key"
}
```

#### Example Response

```json
{
  "message": "Email request is being processed",
  "request_id": "unique-request-id"
}
```

### 2. Check Email Status

**Endpoint**: `GET /email-status/<request_id>`

**Description**: Check the status of an email request using the unique `request_id` returned from the `/send-email` endpoint.

#### Example Request

```json
GET /email-status/unique-request-id
```

#### Example Response

```json
{
  "request_id": "unique-request-id",
  "status": "sent" // or "failed (reason)"
}
```

## Logging

The application logs email actions in `email_log.txt`. Each entry includes:

- `Request ID`: Unique identifier for the email request.
- `Sender`: Email address of the sender.
- `Recipient`: Email address of the recipient.
- `Date`: Date and time of the request.
- `Status`: Status of the email (e.g., "sent" or "failed").

Log Example:

```
Request ID: unique-request-id, Sender: example@gmail.com, Recipient: user@example.com, Date: 2024-11-09 16:14:34, Status: sent
```

## Security Considerations

1. **Use Secure Gmail App Passwords**:
   Store Gmail app passwords securely in `data.csv` and `.env` files. Avoid hardcoding passwords in the code.

2. **Rate Limiting**:
   If deployed in production, consider setting up persistent storage for Flask-Limiter (e.g., Redis). This prevents in-memory rate limiting, which is unreliable in scaled environments.

3. **Disable Debug Mode in Production**:
   Run Flask in production mode (`debug=False`) to avoid exposing sensitive information.

## Future Improvements

1. **Add Persistent Rate Limiting Storage**:
   For production, consider adding Redis or Memcached to manage rate limiting storage.

2. **Advanced Logging**:
   Implement logging to an external service (e.g., ELK stack, Datadog) for better monitoring.

3. **Error Notification**:
   Consider sending notifications to admins if an email fails.

4. **Database for User Management**:
   Replace the CSV file with a database to allow dynamic user management.
