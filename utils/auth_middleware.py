from functools import wraps
from flask import request, jsonify
from utils.jwt_handler import verify_token

# Authentication middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if Authorization header exists
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            
            # Check if header has the correct format (Bearer token)
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        # Return error if no token provided
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify the token
        payload = verify_token(token)
        
        # Return error if token is invalid
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user info from token to request
        request.user = payload
        
        # Continue to the protected route
        return f(*args, **kwargs)
    
    return decorated

# Role-based access control middleware
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            # Check if user has the required role
            if request.user.get('role') not in allowed_roles:
                return jsonify({'error': 'Access denied'}), 403
            
            # Continue to the protected route
            return f(*args, **kwargs)
        return decorated_function
    return decorator 