from flask import Blueprint, request, jsonify
from services.auth_service import email_exists, save_user, authenticate_user, verify_otp
from utils.auth_middleware import token_required, role_required

# Create a new Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    # Get request data
    data = request.get_json()
    
    # Check if all required fields are present
    required_fields = ['first_name', 'last_name', 'email', 'password', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate role (must be either 'user' or 'speaker')
    if data['role'] not in ['user', 'speaker']:
        return jsonify({'error': 'Role must be either "user" or "speaker"'}), 400
    
    # Check if email already exists
    if email_exists(data['email']):
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create user object
    user = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'email': data['email'],
        'password': data['password'],
        'role': data['role']
    }
    
    # Save user to database
    user_id = save_user(user)
    
    # Return success response
    return jsonify({
        'message': 'User created successfully. Please check your email for OTP verification.',
        'user_id': user_id
    }), 201

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_user_otp():
    """
    Verify user's OTP and set account as verified
    
    This endpoint accepts an email and OTP code, verifies them,
    and sets the user's account as verified if the OTP is correct.
    """
    # Get request data
    data = request.get_json()
    
    # Check if email and otp are provided
    if 'email' not in data or 'otp' not in data:
        return jsonify({'error': 'Email and OTP are required'}), 400
    
    # Attempt to verify OTP
    if verify_otp(data['email'], data['otp']):
        return jsonify({
            'message': 'OTP verified successfully!'
        }), 200
    else:
        return jsonify({
            'error': 'Invalid email or OTP'
        }), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    # Get request data
    data = request.get_json()
    
    # Check if email and password are provided
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        # Attempt to authenticate user
        token = authenticate_user(data['email'], data['password'])
        
        # Check if authentication was successful
        if not token:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Return the token
        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401

# Test protected route
@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    # Access user info from the token
    user_id = request.user.get('id')
    email = request.user.get('email')
    role = request.user.get('role')
    
    return jsonify({
        'id': user_id,
        'email': email,
        'role': role
    }), 200

# Test role-specific route (speaker only)
@auth_bp.route('/speaker-only', methods=['GET'])
@role_required(['speaker'])
def speaker_only():
    return jsonify({
        'message': 'This endpoint is only accessible to speakers'
    }), 200 