from config import mongo_client
from bson.objectid import ObjectId

# Database collection
speakers_collection = mongo_client.speakeasy.speakers
users_collection = mongo_client.speakeasy.users

def create_or_update_speaker_profile(user_id, expertise, price_per_session):
    """
    Create a new speaker profile or update existing one
    
    Args:
        user_id (str): ID of the user (speaker)
        expertise (str): Speaker's areas of expertise
        price_per_session (float): Price charged per session
        
    Returns:
        str: ID of the created/updated speaker profile
    """
    # Create speaker profile document
    speaker_profile = {
        "user_id": user_id,
        "expertise": expertise,
        "price_per_session": price_per_session
    }
    
    # Check if speaker profile already exists
    existing_profile = speakers_collection.find_one({"user_id": user_id})
    
    if existing_profile:
        # Update existing profile
        result = speakers_collection.update_one(
            {"user_id": user_id},
            {"$set": speaker_profile}
        )
        return str(existing_profile["_id"])
    else:
        # Create new profile
        result = speakers_collection.insert_one(speaker_profile)
        return str(result.inserted_id)

def get_speaker_profile(user_id):
    """
    Get speaker profile by user ID
    
    Args:
        user_id (str): ID of the user (speaker)
        
    Returns:
        dict: Speaker profile or None if not found
    """
    profile = speakers_collection.find_one({"user_id": user_id})
    return profile

def get_all_speakers():
    """
    Get all speaker profiles with user information
    
    Returns:
        list: List of speaker profiles with basic user information
    """
    speakers = []
    
    # Find all speaker profiles
    profiles = speakers_collection.find()
    
    for profile in profiles:
        # Get user information for this speaker
        user = users_collection.find_one({"_id": ObjectId(profile["user_id"])})
        
        if user:
            # Create combined speaker information
            speaker_info = {
                "profile_id": str(profile["_id"]),
                "user_id": profile["user_id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "expertise": profile["expertise"],
                "price_per_session": profile["price_per_session"]
            }
            
            speakers.append(speaker_info)
    
    return speakers 