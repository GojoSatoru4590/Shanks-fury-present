# +++ Ui Made By Sanjiii [telegram username: @Urr_Sanjiii] +++
# --- Optimized helper_func.py ---

import binascii
import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import *
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait
from shortzy import Shortzy
import requests
import time
from datetime import datetime
from databases.database import db
import pytz

#=============================================================================================================================================================================
# -------------------- HELPER FUNCTIONS FOR USER VERIFICATION IN DIFFERENT CASES -------------------- 
#=============================================================================================================================================================================

# used for checking banned user
async def check_banUser(filter, client, update):
    try:
        user_id = update.from_user.id
        return await db.ban_user_exist(user_id)
    except:
        return False


#used for cheking if a user is admin ~Owner also treated as admin level
async def check_admin(filter, client, update):
    try:
        user_id = update.from_user.id       
        return any([user_id == OWNER_ID, await db.admin_exist(user_id)])
    except Exception as e:
        print(f"! Exception in check_admin: {e}")
        return False

# OPTIMIZED is_subscribed function
async def is_subscribed(filter, client, update):
    Channel_ids = await db.get_all_channels()
    
    if not Channel_ids:
        return True

    user_id = update.from_user.id

    if user_id == OWNER_ID or await db.admin_exist(user_id):
        return True

    # Use asyncio gather to check all channels simultaneously. 
    # This prevents the bot from waiting for one channel query before starting the next.
    tasks = [is_userJoin(client, user_id, channel_id) for channel_id in Channel_ids if channel_id]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check if ANY of the results evaluated to False (meaning user isn't in that channel)
    # This is much faster as it checks the final list of boolean values
    for result in results:
        if not result or isinstance(result, Exception):
            return False
            
    return True

# Check user subscription by specifying channel id and user id
async def is_userJoin(client, user_id, channel_id):
    try:
        member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}
        
    except UserNotParticipant:
        # If user is not participant, quickly check request mode without waiting for extra network calls if possible
        if await db.get_request_forcesub(): 
            return await db.reqSent_user_exist(channel_id, user_id)
            
        return False
        
    except Exception as e:
        # Log minimal info, return False to force sub if anything fails
        # print(f"!Error on is_userJoin(): {e}")
        return False
        
#=============================================================================================================================================================================

async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link

async def encode(string):
    try:
        string_bytes = string.encode("ascii")
        base64_bytes = base64.urlsafe_b64encode(string_bytes)
        base64_string = (base64_bytes.decode("ascii")).strip("=")
        return base64_string
    except Exception as e:
        print(f'Error occured on encode, reason: {e}')

async def decode(base64_string):
    try:
        base64_string = base64_string.strip("=")
        base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes) 
        string = string_bytes.decode("ascii")
        return string
    except Exception as e:
        print(f'Error occured on decode, reason: {e}')
        return None
        
async def get_messages(client, message_ids):
    try:
        messages = []
        total_messages = 0
        while total_messages != len(message_ids):
            temb_ids = message_ids[total_messages:total_messages+200]
            try:
                msgs = await client.get_messages(
                    chat_id=client.db_channel.id,
                    message_ids=temb_ids
                )
            except FloodWait as e:
                await asyncio.sleep(e.value) # Using e.value for newer Pyrogram versions
                msgs = await client.get_messages(
                    chat_id=client.db_channel.id,
                    message_ids=temb_ids
                )
            except:
                pass
            total_messages += len(temb_ids)
            if 'msgs' in locals() and msgs:
                messages.extend(msgs)
        return messages
    except Exception as e:
        print(f'Error occured on get_messages, reason: {e}')

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0

def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)} {period_name} '
    return result.strip()


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

subscribed = filters.create(is_subscribed)
is_admin = filters.create(check_admin)
banUser = filters.create(check_banUser)
