# +++ ᴜɪ ʙʏ ᴀʜᴍᴇᴅ [telegram username: @ᴜʀʀ_sᴀɴᴊɪɪɪ] +++

import asyncio
import base64
import logging
import os
import random
import sys
import re
import string 
import string as rohit
import time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from plugins.autoDelete import auto_del_notification, delete_message
from bot import Bot
from config import *
from helper_func import *
from databases.database import *
from plugins.FORMATS import *
from databases.database import db
from databases.db_verify import *
from config import *
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from datetime import datetime, timedelta
from pytz import timezone


# +++ ᴜɪ ʙʏ ᴀʜᴍᴇᴅ [telegram username: @ᴜʀʀ_sᴀɴᴊɪɪɪ] +++

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id

    # Default initialization
    AUTO_DEL = False
    DEL_TIMER = 0
    HIDE_CAPTION = False
    CHNL_BTN = None
    PROTECT_MODE = False
    last_message = None
    messages = []

    VERIFY_EXPIRE = await db.get_verified_time()  # Fetch verification expiration time
    SHORTLINK_URL = await db.get_shortener_url()
    SHORTLINK_API = await db.get_shortener_api()
    TUT_VID = await db.get_tut_video()
    ADMINS = await db.get_all_admins()
    MIN_VERIFY_TIME = 45  # Minimum time (in seconds) before verification

    logging.info(f"Received /start command from user ID: {id}")

    # Check and add user to the database if not present
    if not await db.present_user(id):
        try:
            await db.add_user(id)
        except Exception as e:
            logging.error(f"Error adding user: {e}")
            return

    text = message.text

    # Check if user is an admin and treat them as verified
    if id in ADMINS:
        verify_status = {
            'is_verified': True,
            'verify_token': None,  # Admins don't need a token
            'verified_time': time.time(),
            'link': ""
        }
    else:
        verify_status = await get_verify_status(id)
    
    # Check if user is premium - premium users don't need token verification
    is_premium = await db.is_premium_user(id)
    if is_premium:
        verify_status = {
            'is_verified': True,
            'verify_token': None,  # Premium users don't need a token
            'verified_time': time.time(),
            'link': ""
        }
    #verify_status = await get_verify_status(id)
           

# Main token verification logic
    if SHORTLINK_URL:
    # Check if token has expired
        if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
            await update_verify_status(id, is_verified=False)
            logging.info(f"User {id} token expired, verification reset.")

        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            logging.info(f"User {id} entered token: {token}")

            stored_token = verify_status.get('verify_token', None)
            generated_time = await get_generated_time(id)  # Fetch generated_time from vers_data

            logging.info(f"» sᴛᴏʀᴇᴅ ᴛᴏᴋᴇɴ : {stored_token}, » ɢᴇɴᴇʀᴀᴛᴇᴅ ᴛɪᴍᴇ : {generated_time}")

            if not stored_token or stored_token != token:
                logging.warning(f"ᴜsᴇʀ {id} ᴇɴᴛᴇʀᴇᴅ ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ : {token}")
                return await message.reply("<blockquote>ʏᴏᴜʀ ᴛᴏᴋᴇɴ ɪs ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ. ᴛʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ /start</blockquote>")

        # Ensure the token is at least 40 seconds old before verification
            if not generated_time or (time.time() - generated_time) < MIN_VERIFY_TIME:
                remaining_time = int(MIN_VERIFY_TIME - (time.time() - generated_time))
                logging.warning(f"ᴜsᴇʀ {id} ᴛʀɪᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ ᴛᴏᴏ ᴇᴀʀʟʏ. ʀᴇᴍᴀɪɴɪɴɢ ᴛɪᴍᴇ : {remaining_time} sec")
                return await message.reply_video(
			video = "https://envs.sh/ekQ.mp4",
			caption = "<blockquote><b>🚨 Bʏᴘᴀss Aᴛᴛᴇᴍᴘᴛ Dᴇᴛᴇᴄᴛᴇᴅ! 🚨</blockquote>\n\n» ᴡᴀʀɴɪɴɢ...!!!</b> ʏᴏᴜ ᴍᴜsᴛ ʀᴇsᴏʟᴠᴇ ᴛʜᴇ ʟɪɴᴋ ᴛᴏ ᴀᴄᴄᴇss ᴛʜᴇ ғɪʟᴇ. ɴᴏ sʜᴏʀᴛᴄᴜᴛs, ɴᴏ ᴛʀɪᴄᴋs! ᴀɴʏ ᴀᴛᴛᴇᴍᴘᴛ ᴛᴏ ʙʏᴘᴀss ᴛʜᴇ sʏsᴛᴇᴍ ᴡɪʟʟ ᴛʀɪɢɢᴇʀ ᴀɴ ɪɴsᴛᴀɴᴛ ʙᴀɴ! 🚫🔥",
		        reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ᴄʟɪᴄᴋ ᴛᴏ ᴠᴇʀɪғʏ ᴀɢᴀɪɴ  •", url=f"https://t.me/{client.username}?start=start")],
                    [InlineKeyboardButton("• ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ", url=TUT_VID),
		    InlineKeyboardButton("ᴅᴇᴠʟᴏᴘᴇʀ •", url = "https://t.me/Urr_Sanjiii") ]
                ])
		)

        # If token is valid and has waited long enough, verify user
            await update_verify_status(id, is_verified=True, verified_time=time.time())
            logging.info(f"User {id} successfully verified with token: {token}")

            return await message.reply(
                f"<blockquote>» ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs !!, 🥳🥳\n\n»ʏᴏᴜʀ ᴛᴏᴋᴇɴ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ ᴀɴᴅ ɴᴏᴡ ᴠᴀʟɪᴅ ғᴏʀ {get_exp_time(VERIFY_EXPIRE)}\n\n» ɴᴏᴡ ʏᴏᴜ <a href='https://t.me/Mugiwaras_Network'>ɢᴇᴛ ᴀᴄᴇss ᴛᴏ ᴀʟʟ 6 ʙᴏᴛs</a> ᴏғ @Anime_Fury ғᴏʀ {get_exp_time(VERIFY_EXPIRE)}.</blockquote>",
                protect_content=False,
                quote=True,
		disable_web_page_preview=True
            )

        if not verify_status['is_verified']:
            token = ''.join(random.choices(rohit.ascii_letters + rohit.digits, k=10))
            generated_time = time.time()
        
            await update_verify_status(id, verify_token=token, link="")
            await store_generated_time(id, generated_time)  # Store generated time separately

            logging.info(f"ɴᴇᴡ ᴛᴏᴋᴇɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ғᴏʀ ᴜsᴇʀ {id}: {token}")

            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
            logging.info(f"Verification link for user {id}: {link}")

            return await message.reply_photo(
                photo=TOKEN_PIC,
                caption=f"<blockquote><b>›› Hey!!, {message.from_user.mention} ~</b></blockquote>\n\n<i>Your Ads token is expired, refresh your token and try again.</i> \n\n<b>Token Timeout:</b> {get_exp_time(VERIFY_EXPIRE)} \n\n<blockquote expandable><b>What is token?</b> \n<i>This is an ads token. If you pass 1 ad, you can use the bot for {get_exp_time(VERIFY_EXPIRE)} after passing the ad.</i>\n\nOnce done you will <a href='https://t.me/Battousai_Network/31'>get access to all our 6 bots</a> for {get_exp_time(VERIFY_EXPIRE)} which are ⬇️\n\n» @Sukuna_Sama_Bot\n» @Devil_Fruit_Bot\n» @Lord_Aizen_Raven_Bot\n» @Hitokiri_Battousai_Bot\n» @pirate_hunter_zoro_raven_bot\n» @Black_Goku_Raven_Bot\n\n<b>APPLE/IPHONE USERS COPY TOKEN LINK AND OPEN IN CHROME BROWSER</b></blockquote>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("»  ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴠᴇʀɪғʏ  «", url=link)],
                    [InlineKeyboardButton("» ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ/ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ «", url=TUT_VID)],
                    [InlineKeyboardButton("🎁 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ 🔖", callback_data="plan")]
                ])
            )
                            
    text = message.text        
    if len(text)>7:
        await message.delete()

        try: base64_string = text.split(" ", 1)[1]
        except: return
                
        string = await decode(base64_string)
        if not string:  # Check if decode failed
            return
        argument = string.split("-")
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
                    
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
                            
        elif len(argument) == 2:
            try: ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except: return
                    
        last_message = None
        await message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT)  
        
        try: messages = await get_messages(client, ids)
        except: return await message.reply("<b><i>sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ..!</i></b>")
            
        AUTO_DEL, DEL_TIMER, HIDE_CAPTION, CHNL_BTN, PROTECT_MODE = await asyncio.gather(db.get_auto_delete(), db.get_del_timer(), db.get_hide_caption(), db.get_channel_button(), db.get_protect_content())   
        if CHNL_BTN: button_name, button_link = await db.get_channel_button_link()
            
        for idx, msg in enumerate(messages):
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)

            elif HIDE_CAPTION and (msg.document or msg.audio):
                caption = ""

            else:
                caption = "" if not msg.caption else msg.caption.html

            if CHNL_BTN:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=button_name, url=button_link)]]) if msg.document or msg.photo or msg.video or msg.audio else None
            else:
                reply_markup = msg.reply_markup   
                    
            try:
                copied_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_MODE)
                await asyncio.sleep(0.1)

                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1: last_message = copied_msg

            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_MODE)
                await asyncio.sleep(0.1)
                
                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1: last_message = copied_msg
                        
        if AUTO_DEL and last_message:
                asyncio.create_task(auto_del_notification(client.username, last_message, DEL_TIMER, message.command[1]))
                        
    else:   
        reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ᴄʟɪᴄᴋ ғᴏʀ ᴍᴏʀᴇ •", callback_data='about')],
                    [InlineKeyboardButton("• sᴇᴛᴛɪɴɢs", callback_data='setting'),
                     InlineKeyboardButton(' ᴅᴇᴠᴇʟᴏᴘᴇʀ •', url='https://t.me/urr_sanjiii')],
                    [InlineKeyboardButton("• ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ •", url='https://t.me/Mugiwaras_Network')],
                ])
        await message.reply_photo(
            photo = random.choice(PICS),
            caption = START_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
            reply_markup = reply_markup,
		has_spoiler = True,
	        message_effect_id=5104841245755180586 #🔥
        )
        try: await message.delete()
        except: pass

   
##===================================================================================================================##

#TRIGGRED START MESSAGE FOR HANDLE FORCE SUB MESSAGE AND FORCE SUB CHANNEL IF A USER NOT JOINED A CHANNEL

##===================================================================================================================##   


# Create a global dictionary to store chat data
chat_data_cache = {}

@Bot.on_message(filters.command('start') & filters.private & ~banUser)
async def not_joined(client: Client, message: Message):
    temp = await message.reply(f"<b>??</b>")

    user_id = message.from_user.id

    REQFSUB = await db.get_request_forcesub()
    buttons = []
    count = 0

    try:
        for total, chat_id in enumerate(await db.get_all_channels(), start=1):
            await message.reply_chat_action(ChatAction.PLAYING)

            # Show the join button of non-subscribed Channels.....
            if not await is_userJoin(client, user_id, chat_id):
                try:
                    # Check if chat data is in cache
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]  # Get data from cache
                    else:
                        data = await client.get_chat(chat_id)  # Fetch from API
                        chat_data_cache[chat_id] = data  # Store in cache

                    cname = data.title

                    # Handle private channels and links
                    if REQFSUB and not data.username: 
                        link = await db.get_stored_reqLink(chat_id)
                        await db.add_reqChannel(chat_id)

                        if not link:
                            link = (await client.create_chat_invite_link(chat_id=chat_id, creates_join_request=True)).invite_link
                            await db.store_reqLink(chat_id, link)
                    else:
                        link = data.invite_link

                    # Add button for the chat
                    buttons.append([InlineKeyboardButton(text='»  ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ  «', url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")

                except Exception as e:
                    print(f"Can't Export Channel Name and Link..., Please Check If the Bot is admin in the FORCE SUB CHANNELS:\nProvided Force sub Channel:- {chat_id}")
                    return await temp.edit(f"<b>! ᴇʀʀᴏʀ, ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @urr_sanjiii</b>\n<blockquote expandable><b>ʀᴇᴀsᴏɴ:</b> {e}</blockquote>")

        # If user has joined all channels, delete temp and return (success - they're verified)
        if count == 0:
            await temp.delete()
            return 

        # Add /byt links first (before "now click here")
        if REQFSUB:
            try:
                byt_links = await db.get_all_fsub_button_links()
                if byt_links:
                    for link in byt_links:
                        buttons.append([InlineKeyboardButton(text='»  ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ  «', url=link)])
            except Exception as e:
                logging.info(f"No /byt links to add: {e}")

        # Add "now click here" button last
        try:
            buttons.append([InlineKeyboardButton(text='‼️ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ ‼️', url=f"https://t.me/{client.username}?start={message.command[1]}")])
        except IndexError:
            pass

        await message.reply_photo(
            photo=random.choice(PICS),
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
    message_effect_id=5104841245755180586  #🔥 Add the effect ID here
        )
    except Exception as e:
        print(f"Error: {e}")  # Print the error message for debugging
        # Optionally, send an error message to the user or handle further actions here
        await temp.edit(f"<b><i>! ᴇʀʀᴏʀ, ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @urr_sanjiii</i></b>\n<blockquote expandable><b>ʀᴇᴀsᴏɴ:</b> {e}</blockquote>")


# +++ Customised By Rohit [telegram username: @rohit_1888] +++

#=====================================================================================##
#......... RESTART COMMAND FOR RESTARTING BOT .......#
#=====================================================================================##

@Bot.on_message(filters.command('restart') & filters.private & filters.user(OWNER_ID))
async def restart_bot(client: Client, message: Message):
    print("Restarting bot...")
    msg = await message.reply(text=f"<b><i>» {client.name} ɢᴏɪɴɢ ᴛᴏ ʀᴇsᴛᴀʀᴛ...\n\n» ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ 5 sᴇᴄᴏɴᴅs...!!!</i></b>")
    try:
        await asyncio.sleep(5)  # Wait for 5 seconds before restarting
        await msg.delete()
        args = [sys.executable, "main.py"]  # Adjust this if your start file is named differently
        os.execl(sys.executable, *args)
    except Exception as e:
        print(f"Error occured while Restarting the bot: {e}")
        return await msg.edit_text(f"<b>! ᴇʀʀᴏʀ, ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @urr_sanjiii</b>\n<blockquote expandable><b>ʀᴇᴀsᴏɴ:</b> {e}</blockquote>")
    # Optionally, you can add cleanup tasks here
    #subprocess.Popen([sys.executable, "main.py"])  # Adjust this if your start file is named differently
    #sys.exit()
