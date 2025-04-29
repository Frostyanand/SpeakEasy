# SpeakEasy - Speaker Session Booking System

SpeakEasy is a comprehensive platform that connects speakers with users for booking and managing speaking sessions. The system facilitates session scheduling, booking management, and feedback collection, providing a seamless experience for both speakers and users.

## 🚀 Features

- **User Authentication & Authorization**
  - Secure signup and login with JWT tokens
  - Role-based access control (User/Speaker)
  - Email verification with OTP

- **Speaker Management**
  - Speaker profile creation and management
  - Session creation and scheduling
  - Availability management
  - Speaker directory

- **Session Management**
  - Session booking system
  - Calendar integration
  - Session reminders
  - Booking confirmation emails
  - Session feedback system

- **Email Notifications**
  - Booking confirmations
  - Session reminders
  - Feedback notifications
  - OTP verification

## 🏗️ System Architecture

### Backend Components

1. **Authentication System**
   - JWT-based authentication
   - Role-based authorization
   - Secure password handling
   - Email verification

2. **Speaker Management**
   - Profile creation and updates
   - Session scheduling
   - Availability management
   - Speaker search and filtering

3. **Booking System**
   - Session booking
   - Calendar integration
   - Booking management
   - Session reminders

4. **Feedback System**
   - Rating submission
   - Feedback collection
   - Notification system

### Data Flow

1. **User Registration Flow**
   ```
   User Signup → Email Verification → Account Activation → Login
   ```

2. **Session Booking Flow**
   ```
   Speaker Creates Session → User Books Session → Confirmation Emails → Session Reminders → Session Completion → Feedback Collection
   ```

3. **Feedback Flow**
   ```
   Session Completion → User Submits Feedback → Speaker Receives Feedback → System Updates Rating
   ```

## 📁 Project Structure

```
SpeakEasy/
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── API_DOCUMENTATION.md  # Detailed API documentation
├── routes/               # API route handlers
│   ├── auth_routes.py    # Authentication endpoints
│   ├── speaker_routes.py # Speaker management endpoints
│   └── booking_routes.py # Booking and session endpoints
├── services/             # Business logic
│   ├── auth_service.py   # Authentication logic
│   ├── speaker_service.py# Speaker management logic
│   ├── booking_service.py# Booking management logic
│   └── email_service.py  # Email notification system
├── utils/                # Utility functions
│   ├── auth_middleware.py# Authentication middleware
│   └── jwt_handler.py    # JWT token management
└── templates/            # Email templates
    └── emails/           # HTML email templates
```

## 🔧 Technical Stack

- **Backend**: Python, Flask
- **Database**: MongoDB
- **Authentication**: JWT
- **Email Service**: SMTP
- **API Documentation**: Postman

## 🛠️ API Endpoints Overview

### Authentication
- Signup
- Login
- OTP Verification
- Password Reset

### Speaker Management
- Create/Update Profile
- Get Speaker Details
- List Available Speakers
- Manage Sessions

### Session Management
- Create Session
- Book Session
- View Bookings
- Cancel Booking
- Submit Feedback

> For detailed API documentation, please refer to [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB
- SMTP Server (for emails)

### Installation

1. Clone the repository
```bash
git clone [repository-url]
cd SpeakEasy
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
```bash
# Create a .env file with the following variables
MONGO_URI=your_mongodb_uri
JWT_SECRET=your_jwt_secret
SMTP_SERVER=your_smtp_server
SMTP_PORT=your_smtp_port
SMTP_EMAIL=your_smtp_email
SMTP_PASSWORD=your_smtp_password
```

4. Run the application
```bash
python app.py
```

## 🔄 System Interactions

### User Journey
1. **Registration & Authentication**
   - User signs up
   - Verifies email
   - Logs in
   - Receives JWT token

2. **Session Booking**
   - User browses available speakers
   - Selects a session
   - Books the session
   - Receives confirmation email
   - Gets session reminders
   - Attends session
   - Submits feedback

### Speaker Journey
1. **Profile Setup**
   - Speaker signs up
   - Creates profile
   - Sets availability
   - Creates sessions

2. **Session Management**
   - Receives booking notifications
   - Manages sessions
   - Receives feedback
   - Updates profile

## 📧 Email Notifications

The system sends various email notifications:
- Account verification
- Session booking confirmations
- Session reminders
- Feedback notifications

All emails are HTML-formatted with responsive design and proper UTF-8 encoding.

## 🔒 Security Features

- JWT-based authentication
- Role-based access control
- Secure password handling
- Email verification
- Input validation
- Error handling

## 🚀 Future Enhancements

1. **Frontend Development**
   - User-friendly web interface
   - Mobile-responsive design
   - Real-time notifications

2. **Additional Features**
   - Payment integration
   - Video conferencing
   - Session recording
   - Advanced analytics

3. **Deployment**
   - Docker containerization
   - CI/CD pipeline
   - Cloud deployment
   - Load balancing

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support, please contact [support@speakeasy.com](mailto:support@speakeasy.com)

 
