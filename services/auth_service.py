import bcrypt
import random
from config import mongo_client
from utils.jwt_handler import generate_token
from services.email_service import send_otp_email

# Database collection
users_collection = mongo_client.speakeasy.users

# Hash password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Verify password using bcrypt
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

# Check if email already exists
def email_exists(email):
    return users_collection.find_one({"email": email}) is not None

# Generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Save new user to database
def save_user(user_data):
    # Hash the password before saving
    user_data["password"] = hash_password(user_data["password"])
    
    # Generate OTP and set verification status
    otp = generate_otp()
    user_data["otp"] = otp
    user_data["is_verified"] = False
    
    # Insert into MongoDB
    result = users_collection.insert_one(user_data)
    
    # Send OTP email
    send_otp_email(user_data["email"], otp, user_data["first_name"])
    
    # Return the inserted user's ID
    return str(result.inserted_id)

# Verify OTP and update user verification status
def verify_otp(email, otp):
    # Find user by email
    user = users_collection.find_one({"email": email})
    
    # Check if user exists
    if not user:
        return False
    
    # Check if OTP matches
    if user.get("otp") != otp:
        return False
    
    # Update verification status and clear OTP
    users_collection.update_one(
        {"email": email},
        {"$set": {"is_verified": True, "otp": ""}}
    )
    
    return True

# Authenticate user and generate token
def authenticate_user(email, password):
    # Find user by email
    user = users_collection.find_one({"email": email})
    
    # Check if user exists
    if not user:
        return None
    
    # Check if user is verified
    if not user.get("is_verified", False):
        raise ValueError("Account not verified. Please verify your OTP first.")
    
    # Verify password
    if not verify_password(password, user["password"]):
        return None
    
    # Generate token payload
    payload = {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    }
    
    # Generate and return token
    token = generate_token(payload)
    return token 