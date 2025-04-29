from flask import Blueprint, request, jsonify
from utils.auth_middleware import token_required, role_required
from services.booking_service import (
    create_session,
    book_session,
    get_user_bookings,
    get_speaker_bookings,
    cancel_booking,
    submit_feedback,
    clear_past_sessions
)
from datetime import datetime

# Create a new Blueprint for booking routes
booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/speaker/create-session', methods=['POST'])
@token_required
@role_required(["speaker"])
def create_speaker_session():
    """
    Create a new session slot
    
    This endpoint allows speakers to create available session slots with a maximum
    number of seats.
    """
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['date', 'time', 'max_seats']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate max_seats is a positive number
    try:
        max_seats = int(data['max_seats'])
        if max_seats <= 0:
            return jsonify({'error': 'max_seats must be a positive number'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'max_seats must be a valid number'}), 400
    
    # Validate date format (YYYY-MM-DD)
    try:
        session_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if session_date < datetime.now().date():
            return jsonify({'error': 'Session date cannot be in the past'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate time format (HH:MM)
    try:
        datetime.strptime(data['time'], '%H:%M')
    except ValueError:
        return jsonify({'error': 'Invalid time format. Use HH:MM (24-hour format)'}), 400
    
    try:
        # Get speaker ID from token
        speaker_id = request.user.get('id')
        
        # Create session
        session_id = create_session(
            speaker_id,
            data['date'],
            data['time'],
            max_seats
        )
        
        # Return success response
        return jsonify({
            'message': 'Session created successfully!',
            'session_id': session_id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to create session'}), 500

@booking_bp.route('/book-session', methods=['POST'])
@token_required
@role_required(["user"])
def book_speaker_session():
    """
    Book a seat in a session
    
    This endpoint allows users to book an available seat in a session.
    """
    # Get request data
    data = request.get_json()
    
    # Validate session_id is provided
    if 'session_id' not in data:
        return jsonify({'error': 'Missing required field: session_id'}), 400
    
    try:
        # Get user ID from token
        user_id = request.user.get('id')
        
        # Book session
        book_session(user_id, data['session_id'])
        
        # Return success response
        return jsonify({
            'message': 'Session booked successfully!'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        return jsonify({'error': 'Failed to book session'}), 500

@booking_bp.route('/my-bookings', methods=['GET'])
@token_required
def get_bookings():
    """
    Get user's bookings
    
    This endpoint returns:
    - For users: List of sessions they have booked
    - For speakers: List of their sessions with booking details
    """
    try:
        # Get user info from token
        user_id = request.user.get('id')
        user_role = request.user.get('role')
        
        # Get bookings based on role
        if user_role == "speaker":
            bookings = get_speaker_bookings(user_id)
        else:
            bookings = get_user_bookings(user_id)
        
        # Return bookings
        return jsonify({
            'bookings': bookings,
            'count': len(bookings)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch bookings'}), 500

@booking_bp.route('/cancel-booking', methods=['POST'])
@token_required
@role_required(["user"])
def cancel_user_booking():
    """
    Cancel a booking
    
    This endpoint allows users to cancel their existing bookings.
    """
    # Get request data
    data = request.get_json()
    
    # Validate booking_id is provided
    if 'booking_id' not in data:
        return jsonify({'error': 'Missing required field: booking_id'}), 400
    
    try:
        # Get user ID from token
        user_id = request.user.get('id')
        
        # Cancel booking
        result = cancel_booking(user_id, data['booking_id'])
        
        # Return success response
        return jsonify({
            'message': result
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to cancel booking'}), 500

@booking_bp.route('/submit-feedback', methods=['POST'])
@token_required
@role_required(["user"])
def submit_session_feedback():
    """
    Submit feedback for a completed session
    
    This endpoint allows users to submit a rating and optional feedback text
    for sessions they have attended.
    """
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['booking_id', 'rating']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate rating is an integer
    try:
        rating = int(data['rating'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Rating must be an integer from 1 to 5'}), 400
    
    try:
        # Get user ID from token
        user_id = request.user.get('id')
        
        # Get optional feedback text
        feedback_text = data.get('feedback_text')
        
        # Submit feedback
        result = submit_feedback(user_id, data['booking_id'], rating, feedback_text)
        
        # Return success response
        return jsonify({
            'message': result
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to submit feedback'}), 500

@booking_bp.route('/clear-past-sessions', methods=['POST'])
@token_required
def clear_past_sessions_route():
    """
    Clear Past Sessions
    
    This endpoint allows users or speakers to soft-delete their past sessions or bookings.
    - For users: Marks all bookings for past sessions as cleared
    - For speakers: Marks all past sessions as cleared
    
    The records are not permanently deleted, just marked as cleared and won't show
    in the my-bookings endpoint.
    """
    try:
        # Get user info from token
        user_id = request.user.get('id')
        user_role = request.user.get('role')
        
        # Clear past sessions based on role
        result = clear_past_sessions(user_id, user_role)
        
        # Return success response
        return jsonify({
            'message': 'Past sessions cleared successfully.',
            'cleared_count': result.get('cleared_count', 0)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to clear past sessions'}), 500 