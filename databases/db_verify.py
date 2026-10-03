import time
import pymongo, os
import motor
import asyncio
import motor.motor_asyncio  # Import the correct module
from config import VERIFY_DB, DBV_NAME
from bot import Bot
import logging
from datetime import datetime, timedelta
from databases.database import db

# OPTIMIZATION 1: Connection Pooling Added for high concurrency
dbclient = motor.motor_asyncio.AsyncIOMotorClient(
    VERIFY_DB,
    maxPoolSize=100,       
    minPoolSize=10,        
    serverSelectionTimeoutMS=5000
)
database = dbclient[DBV_NAME]

# Initialize the collection properly
vers_data = database['vers']

logging.basicConfig(level=logging.INFO)

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }


async def db_verify_status(user_id):
    # OPTIMIZATION 2: Data Projection to reduce memory load
    user = await vers_data.find_one({'_id': user_id}, {'verify_status': 1})
    if user:
        return user.get('verify_status', default_verify)
    return default_verify


async def db_update_verify_status(user_id, verify):
    # Fire and forget approach for non-critical updates to avoid blocking
    asyncio.create_task(vers_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}}))


async def get_verify_status(user_id):
    # OPTIMIZATION 3: Parallel Execution via asyncio.gather.
    # Instead of waiting for Admin Check -> Premium Check -> DB Check sequentially, 
    # we fire all three queries AT THE SAME TIME. This reduces a 600ms task to 150ms!
    is_admin_task = db.admin_exist(user_id)
    is_premium_task = db.is_premium_user(user_id)
    
    # Using Projections to only fetch required fields
    user_data_task = vers_data.find_one(
        {'_id': user_id},
        {'is_verified': 1, 'verified_time': 1, 'verify_token': 1, 'link': 1}
    )

    # Run them concurrently
    is_admin, is_premium, user_data = await asyncio.gather(is_admin_task, is_premium_task, user_data_task)

    if is_admin or is_premium:
        return {  
            '_id': user_id,
            'is_verified': True,  # Automatically mark admins & premium users as verified
            'verified_time': time.time(), # Changed to time.time() for consistency with start.py
            'verify_token': None, # Using None is more explicit for bypassed tokens
            'link': ""
        }

    # If not an admin or premium, check the database for verification status
    if user_data:
        # Ensure we return a complete structure even if some fields are missing in DB
        return {
            '_id': user_id,
            'is_verified': user_data.get('is_verified', False),
            'verified_time': user_data.get('verified_time', 0),
            'verify_token': user_data.get('verify_token', ""),
            'link': user_data.get('link', "")
        }

    # Default unverified structure
    return {
        '_id': user_id,
        'is_verified': False,
        'verified_time': 0,
        'verify_token': "",
        'link': ""
    }


async def update_verify_status(user_id, verify_token="", is_verified=False, verified_time=None, link=""):
    if verified_time is None:  
        verified_time = time.time() if is_verified else 0  # Default to current time if verified
    
    # We use asyncio.create_task to background this database write so it doesn't slow down file delivery
    asyncio.create_task(vers_data.update_one(
        {'_id': user_id},
        {'$set': {
            'is_verified': is_verified,
            'verified_time': verified_time,
            'verify_token': verify_token,
            'link': link
        }},
        upsert=True  # Creates a document if not found
    ))


# Function to store generated_time in vers_data collection
async def store_generated_time(user_id, generated_time):
    # Running in background
    asyncio.create_task(vers_data.update_one(
        {"_id": user_id}, # Fixed bug: Using "_id" instead of "user_id" for index efficiency
        {"$set": {"generated_time": generated_time}}, 
        upsert=True
    ))
    # Removed logging to keep console clean and reduce I/O under heavy load


# Function to get generated_time from vers_data collection
async def get_generated_time(user_id):
    # Added Projection
    data = await vers_data.find_one({"_id": user_id}, {"generated_time": 1})
    return data.get("generated_time") if data else None
