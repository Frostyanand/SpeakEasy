# **SpeakEasy**

## Overview

**SpeakEasy** is a backend application built with **Flask** and **MongoDB**, designed to streamline the process of **booking speaker sessions** for users.  
The system provides a secure and efficient way to browse available speakers, book sessions, and receive booking confirmations via email.  
The project focuses on simplicity, robustness, and clean API-driven design.

This project was developed as a part of the **GDG SRM Technical Domain Recruitment Task 2025**.

---

## Features

- 🔒 **User and Speaker Registration & Authentication** (with JWT)
- 🗂️ **Role-Based Access Control** (User/Speaker)
- 🎙️ **Speaker Profile Management** (Expertise, Pricing per Session)
- 📅 **Session Booking System** (1-hour slots between 9 AM to 4 PM)
- 🚫 **Time Slot Blocking** (prevents double bookings)
- 📧 **Email Confirmation** on Successful Booking (to both User and Speaker)
- 📜 **API Documentation** using Postman Collection
- 🌐 **Deployment** on Render (Publicly Accessible)

---
 
## Tech Stack

| Purpose | Technology |
|:--|:--|
| Backend Framework | Flask |
| Database | MongoDB (pymongo) |
| Authentication | JWT (using `pyjwt`) |
| Password Management | bcrypt (using `bcrypt`) |
| Email Notifications | smtplib (basic Python email sending) |
| API Testing/Documentation | Postman |
| Deployment | Render |

---

## Project Structure

```
/[platform_name]/
│
├── app.py               # Main Flask application
├── models/              # Database models (Users, Speakers, Bookings)
│   ├── user_model.py
│   ├── speaker_model.py
│   └── booking_model.py
│
├── routes/              # All API routes organized
│   ├── auth_routes.py
│   ├── speaker_routes.py
│   └── booking_routes.py
│
├── services/            # Business logic (email, auth helpers)
│   ├── auth_service.py
│   ├── email_service.py
│   └── booking_service.py
│
├── utils/               # Utility files
│   ├── jwt_handler.py
│   └── validators.py
│
├── requirements.txt     # Python dependencies
├── README.md             # Project documentation
├── postman_collection.json # Postman Collection (API Documentation)
└── config.py             # Environment variables configuration
```

---

## Database Schema Overview

### 1. User Collection

| Field | Type | Description |
|:--|:--|:--|
| `id` | ObjectId | MongoDB unique ID |
| `first_name` | String | First name |
| `last_name` | String | Last name |
| `email` | String | Email (unique) |
| `password` | String | Hashed password |
| `role` | String | "user" or "speaker" |
| `otp_verified` | Boolean | OTP verification status |

---

### 2. Speaker Profile Collection

| Field | Type | Description |
|:--|:--|:--|
| `speaker_id` | ObjectId | Linked to User ID |
| `expertise` | String | Area of expertise |
| `price_per_session` | Number | Fee for one session |

---

### 3. Booking Collection

| Field | Type | Description |
|:--|:--|:--|
| `booking_id` | ObjectId | Booking ID |
| `user_id` | ObjectId | ID of the user booking |
| `speaker_id` | ObjectId | ID of the speaker booked |
| `date` | Date | Date of session |
| `time_slot` | String | Time (example: "11:00 AM - 12:00 PM") |

---

## Core APIs

| Endpoint | Method | Access | Purpose |
|:--|:--|:--|:--|
| `/signup` | POST | Public | Register user or speaker |
| `/login` | POST | Public | Login and receive JWT token |
| `/speakers` | GET | Authenticated | List all available speakers |
| `/speaker/profile` | POST | Speaker only | Create or update speaker profile |
| `/book-session` | POST | User only | Book a session with a speaker |
| `/my-bookings` | GET | User or Speaker | View personal bookings |

---

## Main Functional Flow

```
User Signup/Login → Receives JWT Token → Views List of Speakers → 
Selects Speaker and Time Slot → Books Session → 
System Blocks Slot + Sends Email → Booking Success!
```

---

## Email Confirmation Example

- Subject: **Booking Confirmed: [Speaker Name]**
- Body: Includes:
  - User Name
  - Speaker Name
  - Session Date and Time
  - Speaker's Price per Session
  - Meeting Link (Optional/Placeholder)

Emails will be sent using Gmail's SMTP server through a secured application password.

---

## Planned Enhancements (If Time Permits)

- 🔄 **Session Rescheduling / Cancellation**
- 🌟 **Google Calendar Event Creation**
- 💳 **Payment Gateway Mock Integration (e.g., Stripe/Fake Gateway)**
- 📊 **Admin Dashboard (View All Bookings)**
- 📝 **Speaker Rating System (Post-Session Feedback)**

---

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   MONGO_URI=your_mongo_uri_here
   JWT_SECRET=your_jwt_secret_here
   
   # Email settings (for booking confirmations)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=465
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_email_app_password
   ```
   
   **Note for Gmail users**: 
   - If using Gmail, you'll need to use an App Password instead of your regular password
   - Go to your Google Account > Security > 2-Step Verification > App passwords
   - Generate a new app password for "Mail" and use it for SMTP_PASSWORD
   
5. Run the application:
   ```bash
   python app.py
   ```

6. Import Postman collection and start testing APIs.

---

## Deployment

- The app will be deployed on [Render](https://render.com/), making it publicly accessible for testing.

---

## Acknowledgments

Special thanks to **Google Developer Groups on Campus SRM** for organizing this opportunity to build and showcase technical skills.

---

# SpeakEasy - Speaker Session Booking System

A Flask-based API for managing speaker sessions and bookings.

## Project Structure

```
/app.py - Main Flask application
/models/ - Database models
/routes/ - API routes
/services/ - Business logic services
/utils/ - Utility functions and helpers
config.py - Configuration settings
requirements.txt - Project dependencies
```

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with the following variables:
   ```
   MONGO_URI=your_mongo_uri_here
   JWT_SECRET=your_jwt_secret_here
   
   # Email settings (for booking confirmations)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=465
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_email_app_password
   ```
   
   **Note for Gmail users**: 
   - If using Gmail, you'll need to use an App Password instead of your regular password
   - Go to your Google Account > Security > 2-Step Verification > App passwords
   - Generate a new app password for "Mail" and use it for SMTP_PASSWORD
   
5. Run the application:
   ```
   python app.py
   ```

## API Endpoints

### Authentication
- `POST /api/signup` - Register a new user or speaker
- `POST /api/login` - Login and receive JWT token
- `GET /api/profile` - Get user profile (protected)

### Speaker Management
- `POST /api/speaker/profile` - Create or update speaker profile
- `GET /api/speaker/profile` - Get speaker's own profile
- `GET /api/speakers` - List all available speakers

### Session Booking
- `POST /api/speaker/create-session` - Create a new session (speaker only)
- `POST /api/book-session` - Book a seat in a session (user only)
- `GET /api/my-bookings` - Get user's bookings or speaker's sessions

### System
- `GET /` - Health check endpoint

 
