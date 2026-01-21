
import time
import pymongo, os
import motor
import motor.motor_asyncio  # Import the correct module
from config import VERIFY_DB, DBV_NAME
from bot import Bot
import logging
from datetime import datetime, timedelta
from databases.database import *

dbclient = motor.motor_asyncio.AsyncIOMotorClient(VERIFY_DB)
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
    user = await vers_data.find_one({'_id': user_id})
    if user:
        return user.get('verify_status', default_verify)
    return default_verify

async def db_update_verify_status(user_id, verify):
    await vers_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})


async def get_verify_status(user_id):
    is_admin = await db.admin_exist(user_id)  # Check if user is an admin
    if is_admin:
        return {  
            '_id': user_id,
            'is_verified': True,  # Automatically mark admins as verified
            'verified_time': datetime.utcnow().timestamp(),
            'verify_token': "",
            'link': ""
        }

    # Check if user is premium - premium users don't need verification
    is_premium = await db.is_premium_user(user_id)
    if is_premium:
        return {
            '_id': user_id,
            'is_verified': True,  # Automatically mark premium users as verified
            'verified_time': datetime.utcnow().timestamp(),
            'verify_token': "",
            'link': ""
        }

    # If not an admin or premium, check the database for verification status
    user = await vers_data.find_one({'_id': user_id})
    if user:
        return user

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
        verified_time = datetime.utcnow().timestamp() if is_verified else 0  # Default to current time if verified
    
    await vers_data.update_one(
        {'_id': user_id},
        {'$set': {
            'is_verified': is_verified,
            'verified_time': verified_time,
            'verify_token': verify_token,
            'link': link
        }},
        upsert=True  # Creates a document if not found
    )


# Function to store generated_time in vers_data collection
async def store_generated_time(user_id, generated_time):
    await vers_data.update_one(
        {"user_id": user_id}, 
        {"$set": {"generated_time": generated_time}}, 
        upsert=True
    )
    logging.info(f"Stored generated_time for user {user_id}: {generated_time}")

# Function to get generated_time from vers_data collection
async def get_generated_time(user_id):
    data = await vers_data.find_one({"user_id": user_id})
    return data.get("generated_time") if data else None
