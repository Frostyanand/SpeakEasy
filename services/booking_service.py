from datetime import datetime
from bson import ObjectId
from config import mongo_client
from services.email_service import send_booking_confirmation, send_feedback_confirmation

# Database collections
sessions_collection = mongo_client.speakeasy.sessions
bookings_collection = mongo_client.speakeasy.bookings
users_collection = mongo_client.speakeasy.users
speakers_collection = mongo_client.speakeasy.speakers

def create_session(speaker_id, date, time, max_seats):
    """
    Create a new session for a speaker
    
    Args:
        speaker_id (str): ID of the speaker
        date (str): Session date in YYYY-MM-DD format
        time (str): Session time in HH:MM format
        max_seats (int): Maximum number of seats available
        
    Returns:
        str: ID of the created session
    
    Raises:
        ValueError: If speaker already has a session at the same date and time
        ValueError: If session time is not between 9:00 AM and 3:00 PM
    """
    # Check if speaker already has a session at this date and time
    existing_session = sessions_collection.find_one({
        "speaker_id": speaker_id,
        "date": date,
        "time": time
    })
    
    if existing_session:
        raise ValueError("You already have a session scheduled at this date and time")
    
    # Validate session time (between 9:00 AM and 3:00 PM)
    try:
        session_time = datetime.strptime(time, "%H:%M").time()
        min_time = datetime.strptime("09:00", "%H:%M").time()
        max_time = datetime.strptime("15:00", "%H:%M").time()  # 3:00 PM (last slot is 3-4 PM)
        
        if session_time < min_time or session_time > max_time:
            raise ValueError("Sessions must be between 9:00 AM to 4:00 PM, 1-hour slots only.")
    except ValueError as e:
        # If the error is from the datetime.strptime, re-raise with our custom message
        if "does not match format" in str(e):
            raise ValueError("Invalid time format. Use HH:MM (24-hour format)")
        # Otherwise re-raise the original error
        raise
    
    # Create new session document
    session = {
        "speaker_id": speaker_id,
        "date": date,
        "time": time,
        "max_seats": max_seats,
        "seats_booked": 0
    }
    
    # Insert session
    result = sessions_collection.insert_one(session)
    return str(result.inserted_id)

def book_session(user_id, session_id):
    """
    Book a seat in a session
    
    Args:
        user_id (str): ID of the user booking the session
        session_id (str): ID of the session to book
        
    Returns:
        bool: True if booking successful
        
    Raises:
        ValueError: If session is full or user already booked
    """
    # Convert session_id to ObjectId
    session_oid = ObjectId(session_id)
    
    # Check if session exists and has available seats
    session = sessions_collection.find_one({"_id": session_oid})
    if not session:
        raise ValueError("Session not found")
    
    if session["seats_booked"] >= session["max_seats"]:
        raise ValueError("This session is fully booked")
    
    # Check if user already booked this session
    existing_booking = bookings_collection.find_one({
        "user_id": user_id,
        "session_id": str(session_id)
    })
    
    if existing_booking:
        raise ValueError("You have already booked this session")
    
    # Create booking
    booking = {
        "user_id": user_id,
        "session_id": str(session_id),
        "created_at": datetime.utcnow()
    }
    
    # Start a transaction
    with mongo_client.start_session() as mongo_session:
        with mongo_session.start_transaction():
            # Insert booking
            bookings_collection.insert_one(booking)
            
            # Increment seats_booked
            sessions_collection.update_one(
                {"_id": session_oid},
                {"$inc": {"seats_booked": 1}}
            )
    
    # Get user and speaker information for email notification
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    speaker = users_collection.find_one({"_id": ObjectId(session["speaker_id"])})
    
    if user and speaker:
        # Get user's full name
        user_name = f"{user['first_name']} {user['last_name']}"
        
        # Send email confirmation
        try:
            send_booking_confirmation(
                user_email=user["email"],
                speaker_email=speaker["email"],
                session_details={
                    "date": session["date"],
                    "time": session["time"],
                    "speaker_name": f"{speaker['first_name']} {speaker['last_name']}"
                },
                user_name=user_name
            )
        except Exception as e:
            # Log error but don't affect booking status
            print(f"Failed to send booking confirmation emails: {e}")
    
    return True

def cancel_booking(user_id, booking_id):
    """
    Cancel a session booking
    
    Args:
        user_id (str): ID of the user cancelling the booking
        booking_id (str): ID of the booking to cancel
        
    Returns:
        str: Success message
        
    Raises:
        ValueError: If booking not found or not owned by the user
    """
    # Convert booking_id to ObjectId
    booking_oid = ObjectId(booking_id)
    
    # Find the booking
    booking = bookings_collection.find_one({"_id": booking_oid})
    if not booking:
        raise ValueError("Booking not found")
    
    # Check if the booking belongs to the user
    if booking["user_id"] != user_id:
        raise ValueError("Not your booking")
    
    # Get session details
    session_id = booking["session_id"]
    session_oid = ObjectId(session_id)
    session = sessions_collection.find_one({"_id": session_oid})
    
    if not session:
        raise ValueError("Session not found")
    
    # Start a transaction
    with mongo_client.start_session() as mongo_session:
        with mongo_session.start_transaction():
            # Decrement seats_booked
            sessions_collection.update_one(
                {"_id": session_oid},
                {"$inc": {"seats_booked": -1}}
            )
            
            # Delete the booking
            bookings_collection.delete_one({"_id": booking_oid})
    
    return "Booking cancelled successfully"

def submit_feedback(user_id, booking_id, rating, feedback_text=None):
    """
    Submit feedback for a completed session
    
    Args:
        user_id (str): ID of the user submitting feedback
        booking_id (str): ID of the booking
        rating (int): Rating from 1 to 5
        feedback_text (str, optional): Text feedback
        
    Returns:
        str: Success message
        
    Raises:
        ValueError: If booking not found, not owned by user, or invalid rating
    """
    # Validate rating
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise ValueError("Rating must be an integer from 1 to 5")
    
    # Convert booking_id to ObjectId
    booking_oid = ObjectId(booking_id)
    
    # Find the booking
    booking = bookings_collection.find_one({"_id": booking_oid})
    if not booking:
        raise ValueError("Booking not found")
    
    # Check if the booking belongs to the user
    if booking["user_id"] != user_id:
        raise ValueError("Not your booking")
    
    # Check if feedback already exists
    if "rating" in booking:
        raise ValueError("Feedback already submitted for this session")
    
    # Update booking with feedback
    update_data = {
        "rating": rating,
        "feedback_submitted_at": datetime.utcnow()
    }
    
    if feedback_text:
        update_data["feedback_text"] = feedback_text
    
    # Update the booking
    bookings_collection.update_one(
        {"_id": booking_oid},
        {"$set": update_data}
    )
    
    # Get session and user details for email confirmation
    try:
        session = sessions_collection.find_one({"_id": ObjectId(booking["session_id"])})
        if not session:
            print(f"Failed to find session with ID: {booking['session_id']}")
            return "Feedback submitted successfully"
            
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            print(f"Failed to find user with ID: {user_id}")
            return "Feedback submitted successfully"
            
        speaker = users_collection.find_one({"_id": ObjectId(session["speaker_id"])})
        if not speaker:
            print(f"Failed to find speaker with ID: {session['speaker_id']}")
            return "Feedback submitted successfully"
        
        # Get user's full name
        user_name = f"{user['first_name']} {user['last_name']}"
        
        # Check if files exist
        import os
        if not os.path.exists("templates/emails/feedback_confirmation.html"):
            print("Error: Missing template file: templates/emails/feedback_confirmation.html")
            return "Feedback submitted successfully"
            
        if not os.path.exists("templates/emails/feedback_confirmation_speaker.html"):
            print("Error: Missing template file: templates/emails/feedback_confirmation_speaker.html")
            return "Feedback submitted successfully"
        
        # Send feedback confirmation emails
        send_feedback_confirmation(
            user_email=user["email"],
            speaker_email=speaker["email"],
            session_details={
                "date": session["date"],
                "time": session["time"],
                "speaker_name": f"{speaker['first_name']} {speaker['last_name']}"
            },
            user_name=user_name,
            rating=rating,
            feedback_text=feedback_text
        )
        print(f"Successfully sent feedback emails to {user['email']} and {speaker['email']}")
    except Exception as e:
        # Log error but don't affect feedback submission status
        print(f"Failed to send feedback confirmation emails: {str(e)}")
    
    return "Feedback submitted successfully"

def clear_past_sessions(user_id, role):
    """
    Soft-delete past sessions or bookings based on user role
    
    Args:
        user_id (str): ID of the user or speaker
        role (str): User's role ('user' or 'speaker')
        
    Returns:
        dict: Count of cleared items
        
    Raises:
        ValueError: If role is invalid
    """
    if role not in ["user", "speaker"]:
        raise ValueError("Invalid role")
    
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Running clear_past_sessions for {role} (ID: {user_id}). Today's date: {today}")
    
    result = {"cleared_count": 0}
    
    if role == "user":
        # For users - mark past bookings as cleared
        user_bookings = list(bookings_collection.find({"user_id": user_id, "cleared": {"$ne": True}}))
        print(f"Found {len(user_bookings)} uncleared bookings for user")
        
        for booking in user_bookings:
            # Get session details
            session = sessions_collection.find_one({"_id": ObjectId(booking["session_id"])})
            if session:
                print(f"Checking session date: {session['date']} against today: {today}")
                if session["date"] < today:
                    # Mark booking as cleared
                    bookings_collection.update_one(
                        {"_id": booking["_id"]},
                        {"$set": {"cleared": True}}
                    )
                    result["cleared_count"] += 1
                    print(f"Cleared booking ID: {booking['_id']} for session on {session['date']}")
            else:
                print(f"Session not found for booking ID: {booking['_id']}")
    
    elif role == "speaker":
        # For speakers - mark past sessions as cleared
        print(f"Looking for sessions for speaker with date < {today} and not cleared")
        update_result = sessions_collection.update_many(
            {"speaker_id": user_id, "date": {"$lt": today}, "cleared": {"$ne": True}},
            {"$set": {"cleared": True}}
        )
        result["cleared_count"] = update_result.modified_count
        print(f"Cleared {update_result.modified_count} past sessions for speaker")
    
    print(f"Clearing complete. Total items cleared: {result['cleared_count']}")
    return result

def get_user_bookings(user_id):
    """
    Get all sessions booked by a user
    
    Args:
        user_id (str): ID of the user
        
    Returns:
        list: List of booked sessions with speaker details
    """
    bookings = []
    
    # Find all bookings for this user that aren't cleared
    user_bookings = bookings_collection.find({"user_id": user_id, "cleared": {"$ne": True}})
    
    for booking in user_bookings:
        # Get session details
        session = sessions_collection.find_one({"_id": ObjectId(booking["session_id"])})
        if session:
            # Get speaker details
            speaker = users_collection.find_one({"_id": ObjectId(session["speaker_id"])})
            speaker_profile = speakers_collection.find_one({"user_id": session["speaker_id"]})
            
            if speaker and speaker_profile:
                booking_info = {
                    "booking_id": str(booking["_id"]),
                    "session_id": booking["session_id"],
                    "date": session["date"],
                    "time": session["time"],
                    "speaker_name": f"{speaker['first_name']} {speaker['last_name']}",
                    "expertise": speaker_profile["expertise"],
                    "price_per_session": speaker_profile["price_per_session"]
                }
                
                # Add feedback if exists
                if "rating" in booking:
                    booking_info["rating"] = booking["rating"]
                    
                    if "feedback_text" in booking:
                        booking_info["feedback_text"] = booking["feedback_text"]
                
                bookings.append(booking_info)
    
    # Sort by date and time
    return sorted(bookings, key=lambda x: (x["date"], x["time"]))

def get_speaker_bookings(speaker_id):
    """
    Get all sessions created by a speaker with booking details
    
    Args:
        speaker_id (str): ID of the speaker
        
    Returns:
        list: List of sessions with booking details
    """
    sessions = []
    
    # Find all sessions by this speaker that aren't cleared
    speaker_sessions = sessions_collection.find({"speaker_id": speaker_id, "cleared": {"$ne": True}})
    
    for session in speaker_sessions:
        # Get all bookings for this session
        session_bookings = bookings_collection.find({"session_id": str(session["_id"])})
        booked_users = []
        
        for booking in session_bookings:
            user = users_collection.find_one({"_id": ObjectId(booking["user_id"])})
            if user:
                user_info = {
                    "user_id": booking["user_id"],
                    "name": f"{user['first_name']} {user['last_name']}",
                    "email": user["email"]
                }
                
                # Add feedback if exists
                if "rating" in booking:
                    user_info["rating"] = booking["rating"]
                    
                    if "feedback_text" in booking:
                        user_info["feedback_text"] = booking["feedback_text"]
                
                booked_users.append(user_info)
        
        session_info = {
            "session_id": str(session["_id"]),
            "date": session["date"],
            "time": session["time"],
            "max_seats": session["max_seats"],
            "seats_booked": session["seats_booked"],
            "booked_users": booked_users
        }
        sessions.append(session_info)
    
    # Sort by date and time
    return sorted(sessions, key=lambda x: (x["date"], x["time"])) 