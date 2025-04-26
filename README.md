
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

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env` file:
   ```
   MONGO_URI=your_mongodb_connection_string
   JWT_SECRET=your_jwt_secret_key
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   ```

4. Run the server:
   ```bash
   python app.py
   ```

5. Import Postman collection and start testing APIs.

---

## Deployment

- The app will be deployed on [Render](https://render.com/), making it publicly accessible for testing.

---

## Acknowledgments

Special thanks to **Google Developer Groups on Campus SRM** for organizing this opportunity to build and showcase technical skills.

---

 
