from datetime import datetime
from bson import ObjectId
from config import mongo_client
from services.email_service import send_booking_confirmation

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

def get_user_bookings(user_id):
    """
    Get all sessions booked by a user
    
    Args:
        user_id (str): ID of the user
        
    Returns:
        list: List of booked sessions with speaker details
    """
    bookings = []
    
    # Find all bookings for this user
    user_bookings = bookings_collection.find({"user_id": user_id})
    
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
    
    # Find all sessions by this speaker
    speaker_sessions = sessions_collection.find({"speaker_id": speaker_id})
    
    for session in speaker_sessions:
        # Get all bookings for this session
        session_bookings = bookings_collection.find({"session_id": str(session["_id"])})
        booked_users = []
        
        for booking in session_bookings:
            user = users_collection.find_one({"_id": ObjectId(booking["user_id"])})
            if user:
                booked_users.append({
                    "user_id": booking["user_id"],
                    "name": f"{user['first_name']} {user['last_name']}",
                    "email": user["email"]
                })
        
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