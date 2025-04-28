from flask import Blueprint, request, jsonify
from utils.auth_middleware import token_required, role_required
from services.speaker_service import create_or_update_speaker_profile, get_speaker_profile, get_all_speakers

# Create a new Blueprint for speaker routes
speaker_bp = Blueprint('speaker', __name__)

@speaker_bp.route('/speaker/profile', methods=['POST'])
@token_required
@role_required(["speaker"])
def create_profile():
    """
    Create or update a speaker profile
    
    This endpoint allows speakers to create or update their profile with
    expertise and price per session information.
    
    Required fields:
    - expertise: String containing speaker's expertise areas
    - price_per_session: Number representing the cost per session
    """
    # Get request data
    data = request.get_json()
    
    # Validate required fields
    if 'expertise' not in data:
        return jsonify({'error': 'Missing required field: expertise'}), 400
    
    if 'price_per_session' not in data:
        return jsonify({'error': 'Missing required field: price_per_session'}), 400
    
    # Validate price_per_session is a number
    try:
        price = float(data['price_per_session'])
        if price <= 0:
            return jsonify({'error': 'Price per session must be a positive number'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Price per session must be a valid number'}), 400
    
    # Get user ID from token
    user_id = request.user.get('id')
    
    # Create or update speaker profile
    profile_id = create_or_update_speaker_profile(
        user_id,
        data['expertise'],
        price
    )
    
    # Return success response
    return jsonify({
        'message': 'Speaker profile updated successfully',
        'profile_id': profile_id
    }), 201

@speaker_bp.route('/speaker/profile', methods=['GET'])
@token_required
@role_required(["speaker"])
def get_profile():
    """
    Get the current speaker's profile
    
    This endpoint allows speakers to view their current profile information.
    """
    # Get user ID from token
    user_id = request.user.get('id')
    
    # Get speaker profile
    profile = get_speaker_profile(user_id)
    
    # Check if profile exists
    if not profile:
        return jsonify({'error': 'Speaker profile not found'}), 404
    
    # Return profile
    return jsonify({
        'profile': {
            'id': str(profile['_id']),
            'user_id': profile['user_id'],
            'expertise': profile['expertise'],
            'price_per_session': profile['price_per_session']
        }
    }), 200

@speaker_bp.route('/speakers', methods=['GET'])
@token_required
def get_speakers():
    """
    Get all available speakers
    
    This endpoint allows users to browse all available speakers and their profiles.
    """
    # Get all speaker profiles with user information
    speakers = get_all_speakers()
    
    # Return list of speakers
    return jsonify({
        'speakers': speakers,
        'count': len(speakers)
    }), 200 