import bcrypt
from config import mongo_client
from utils.jwt_handler import generate_token

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

# Save new user to database
def save_user(user_data):
    # Hash the password before saving
    user_data["password"] = hash_password(user_data["password"])
    
    # Insert into MongoDB
    result = users_collection.insert_one(user_data)
    
    # Return the inserted user's ID
    return str(result.inserted_id)

# Authenticate user and generate token
def authenticate_user(email, password):
    # Find user by email
    user = users_collection.find_one({"email": email})
    
    # Check if user exists
    if not user:
        return None
    
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