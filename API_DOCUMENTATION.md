# SpeakEasy API Documentation

This comprehensive guide documents all available API endpoints in the SpeakEasy platform. It provides details on request formats, authentication requirements, and expected responses to help developers integrate with our system.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:5000/api
```

## Authentication

Most endpoints require authentication using a JWT token. Include the token in your request headers:

```
Authorization: Bearer <your_jwt_token>
```

The token is obtained from the `/login` endpoint and remains valid for 24 hours.

## Response Format

All responses follow a standard JSON format:

- Success responses include a `message` field and optional data fields
- Error responses include an `error` field with a descriptive message

## API Endpoints

### 1. Authentication

#### 1.1. User Signup

Creates a new user or speaker account. After signup, an OTP will be sent to the provided email for verification.

- **URL**: `/signup`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com",
    "password": "securePassword123",
    "role": "user"  // "user" or "speaker"
  }
  ```
- **Success Response** (201 Created):
  ```json
  {
    "message": "User created successfully. Please check your email for OTP verification.",
    "user_id": "60a1c3f9a6e6c3001c0a5b8a"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing required fields
  - 400 Bad Request: Invalid role
  - 409 Conflict: Email already exists

#### 1.2. OTP Verification

Verifies the OTP sent to the user's email after signup.

- **URL**: `/verify-otp`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "email": "jane.doe@example.com",
    "otp": "123456"
  }
  ```
- **Success Response** (200 OK):
  ```json
  {
    "message": "OTP verified successfully!"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing fields
  - 400 Bad Request: Invalid email or OTP

#### 1.3. Login

Authenticates a user and provides a JWT token for accessing protected endpoints.

- **URL**: `/login`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "email": "jane.doe@example.com",
    "password": "securePassword123"
  }
  ```
- **Success Response** (200 OK):
  ```json
  {
    "message": "Login successful",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing fields
  - 401 Unauthorized: Invalid credentials
  - 401 Unauthorized: Account not verified

### 2. Speaker Management

#### 2.1. Create/Update Speaker Profile

Creates or updates a speaker's profile with expertise and pricing information.

- **URL**: `/speaker/profile`
- **Method**: `POST`
- **Authentication**: Required (Speaker only)
- **Request Body**:
  ```json
  {
    "expertise": "JavaScript Development",
    "bio": "10+ years of experience in frontend development",
    "price_per_session": 75.00
  }
  ```
- **Success Response** (200 OK):
  ```json
  {
    "message": "Speaker profile updated successfully",
    "profile_id": "60a1c3f9a6e6c3001c0a5b8b"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing required fields
  - 401 Unauthorized: Not authenticated
  - 403 Forbidden: Not a speaker

#### 2.2. Get Speaker Profile

Retrieves the authenticated speaker's profile information.

- **URL**: `/speaker/profile`
- **Method**: `GET`
- **Authentication**: Required (Speaker only)
- **Success Response** (200 OK):
  ```json
  {
    "profile": {
      "expertise": "JavaScript Development",
      "bio": "10+ years of experience in frontend development",
      "price_per_session": 75.00,
      "speaker_id": "60a1c3f9a6e6c3001c0a5b8a"
    }
  }
  ```
- **Error Responses**:
  - 401 Unauthorized: Not authenticated
  - 403 Forbidden: Not a speaker
  - 404 Not Found: Profile not found

#### 2.3. Get All Speakers

Retrieves a list of all available speakers and their profiles.

- **URL**: `/speakers`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response** (200 OK):
  ```json
  {
    "speakers": [
      {
        "speaker_id": "60a1c3f9a6e6c3001c0a5b8a",
        "name": "John Smith",
        "expertise": "JavaScript Development",
        "bio": "10+ years of experience in frontend development",
        "price_per_session": 75.00
      },
      {
        "speaker_id": "60a1c4f9a6e6c3001c0a5b8c",
        "name": "Jane Rogers",
        "expertise": "Python & Data Science",
        "bio": "Data scientist with focus on ML applications",
        "price_per_session": 90.00
      }
    ],
    "count": 2
  }
  ```
- **Error Responses**:
  - 401 Unauthorized: Not authenticated

### 3. Session Management

#### 3.1. Create Session (Speaker)

Creates a new session slot for users to book.

- **URL**: `/speaker/create-session`
- **Method**: `POST`
- **Authentication**: Required (Speaker only)
- **Request Body**:
  ```json
  {
    "date": "2023-12-15",
    "time": "10:00",
    "max_seats": 5
  }
  ```
- **Success Response** (201 Created):
  ```json
  {
    "message": "Session created successfully!",
    "session_id": "60a1c5f9a6e6c3001c0a5b8d"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing required fields
  - 400 Bad Request: Invalid date format
  - 400 Bad Request: Invalid time format
  - 400 Bad Request: Session date cannot be in the past
  - 400 Bad Request: Sessions must be between 9:00 AM to 4:00 PM, 1-hour slots only
  - 401 Unauthorized: Not authenticated
  - 403 Forbidden: Not a speaker
  - 409 Conflict: Session already exists at this date and time

#### 3.2. Book Session (User)

Books a seat in an available session.

- **URL**: `/book-session`
- **Method**: `POST`
- **Authentication**: Required (User only)
- **Request Body**:
  ```json
  {
    "session_id": "60a1c5f9a6e6c3001c0a5b8d"
  }
  ```
- **Success Response** (201 Created):
  ```json
  {
    "message": "Session booked successfully!"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing session_id
  - 401 Unauthorized: Not authenticated
  - 403 Forbidden: Not a user
  - 409 Conflict: Session not found
  - 409 Conflict: Session is fully booked
  - 409 Conflict: Already booked this session

#### 3.3. View My Bookings

Retrieves all bookings for the authenticated user or all sessions for the authenticated speaker.

- **URL**: `/my-bookings`
- **Method**: `GET`
- **Authentication**: Required
- **Success Response for Users** (200 OK):
  ```json
  {
    "bookings": [
      {
        "booking_id": "60a1c6f9a6e6c3001c0a5b8e",
        "session_id": "60a1c5f9a6e6c3001c0a5b8d",
        "date": "2023-12-15",
        "time": "10:00",
        "speaker_name": "John Smith",
        "expertise": "JavaScript Development",
        "price_per_session": 75.00,
        "rating": 4,  // Optional, if feedback is provided
        "feedback_text": "Session was very helpful!"  // Optional, if feedback is provided
      }
    ],
    "count": 1
  }
  ```
- **Success Response for Speakers** (200 OK):
  ```json
  {
    "bookings": [
      {
        "session_id": "60a1c5f9a6e6c3001c0a5b8d",
        "date": "2023-12-15",
        "time": "10:00",
        "max_seats": 5,
        "seats_booked": 1,
        "booked_users": [
          {
            "user_id": "60a1c3f9a6e6c3001c0a5b8a",
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "rating": 4,  // Optional, if feedback is provided
            "feedback_text": "Session was very helpful!"  // Optional, if feedback is provided
          }
        ]
      }
    ],
    "count": 1
  }
  ```
- **Error Responses**:
  - 401 Unauthorized: Not authenticated
  - 500 Internal Server Error: Failed to fetch bookings

#### 3.4. Cancel Booking

Cancels an existing session booking.

- **URL**: `/cancel-booking`
- **Method**: `POST`
- **Authentication**: Required (User only)
- **Request Body**:
  ```json
  {
    "booking_id": "60a1c6f9a6e6c3001c0a5b8e"
  }
  ```
- **Success Response** (200 OK):
  ```json
  {
    "message": "Booking cancelled successfully"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing booking_id
  - 400 Bad Request: Booking not found
  - 400 Bad Request: Not your booking
  - 401 Unauthorized: Not authenticated
  - 403 Forbidden: Not a user
  - 500 Internal Server Error: Failed to cancel booking

#### 3.5. Clear Past Sessions

Soft-deletes past sessions or bookings based on the authenticated user's role.

- **URL**: `/clear-past-sessions`
- **Method**: `POST`
- **Authentication**: Required (User or Speaker)
- **Request Body**: No request body needed
- **Success Response** (200 OK):
  ```json
  {
    "message": "Past sessions cleared successfully.",
    "cleared_count": 3
  }
  ```
- **Behavior**:
  - For users: Marks past bookings as cleared (not visible in bookings list)
  - For speakers: Marks past sessions as cleared (not visible in sessions list)
- **Error Responses**:
  - 401 Unauthorized: Not authenticated
  - 500 Internal Server Error: Failed to clear past sessions

#### 3.6. Submit Feedback

Submits a rating and optional feedback for a completed session.

- **URL**: `/submit-feedback`
- **Method**: `POST`
- **Authentication**: Required (User only)
- **Request Body**:
  ```json
  {
    "booking_id": "60a1c6f9a6e6c3001c0a5b8e",
    "rating": 4,  // Integer from 1 to 5
    "feedback_text": "Session was very helpful!"  // Optional
  }
  ```
- **Success Response** (200 OK):
  ```json
  {
    "message": "Feedback submitted successfully"
  }
  ```
- **Error Responses**:
  - 400 Bad Request: Missing required fields
  - 400 Bad Request: Rating must be an integer from 1 to 5
  - 400 Bad Request: Booking not found
  - 400 Bad Request: Not your booking
  - 400 Bad Request: Feedback already submitted
  - 401 Unauthorized: Not authenticated
  - 403 Forbidden: Not a user
  - 500 Internal Server Error: Failed to submit feedback

## Using the API with Postman

### Setting Up Postman

1. Import the `SpeakEasy_API_Collection.json` file into Postman
2. Create an environment with the following variables:
   - `base_url`: `http://localhost:5000`
   - `token`: This will be filled automatically after login

### Authentication Flow

1. **Create an Account**:
   - Use the "Signup" request
   - Fill in the required fields
   - Send the request and note the success message

2. **Verify Your Account**:
   - Check your email for the OTP
   - Use the "Verify OTP" request
   - Fill in your email and the OTP
   - Send the request

3. **Login**:
   - Use the "Login" request
   - Fill in your email and password
   - Send the request
   - The JWT token will be automatically stored in the `token` variable for subsequent requests

### Speaker Workflow

1. **Create a Profile** (if you're a speaker):
   - Use the "Create/Update Speaker Profile" request
   - Fill in your expertise, bio, and price
   - Send the request

2. **Create Session Slots**:
   - Use the "Create Session (Speaker)" request
   - Set a date (YYYY-MM-DD), time (HH:MM), and maximum seats
   - Note: Time must be between 9:00 AM and 3:00 PM
   - Send the request

3. **View Booked Sessions**:
   - Use the "My Bookings" request
   - Send the request to see who has booked your sessions
   - Check for any feedback from users

### User Workflow

1. **Find Speakers**:
   - Use the "Get All Speakers" request
   - Send the request to see available speakers

2. **Book a Session**:
   - Note a session_id from a speaker's available sessions
   - Use the "Book Session (User)" request
   - Fill in the session_id
   - Send the request

3. **View Your Bookings**:
   - Use the "My Bookings" request
   - Send the request to see all your booked sessions

4. **Cancel a Booking** (if needed):
   - Note the booking_id from your bookings
   - Use the "Cancel Booking" request
   - Fill in the booking_id
   - Send the request

5. **Submit Feedback** (after attending a session):
   - Note the booking_id from your bookings
   - Use the "Submit Feedback" request
   - Fill in the booking_id, rating (1-5), and optional feedback text
   - Send the request

## Error Handling

All errors follow a standard format:

```json
{
  "error": "Descriptive error message"
}
```

Common HTTP status codes:
- 200 OK: Request successful
- 201 Created: Resource created successfully
- 400 Bad Request: Invalid input or validation error
- 401 Unauthorized: Missing or invalid authentication
- 403 Forbidden: Not authorized to access the resource
- 404 Not Found: Resource not found
- 409 Conflict: Resource conflict
- 500 Internal Server Error: Server-side error

## Rate Limiting

API requests are limited to 100 requests per minute per IP address. Exceeding this limit will result in a 429 (Too Many Requests) response.

## Additional Notes

- All timestamps are in UTC
- Session durations are fixed at 1 hour
- Speakers can create sessions between 9:00 AM and 3:00 PM only (last session ends at 4:00 PM)
- Users can provide feedback only once per booking
- Only users can cancel bookings (speakers cannot cancel) 