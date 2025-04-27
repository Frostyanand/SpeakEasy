import jwt
import os
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get JWT secret from environment
JWT_SECRET = os.getenv("JWT_SECRET")

# Generate JWT token from payload
def generate_token(payload):
    # Add expiration time (24 hours from now)
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    # Sign the token with our secret
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# Verify and decode JWT token
def verify_token(token):
    try:
        # Decode and verify the token
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None 