# +++ ᴜɪ ʙʏ ᴀʜᴍᴇᴅ [telegram username: @ᴜʀʀ_sᴀɴᴊɪɪɪ] +++
# --- Fully Optimized & Fixed for FORCE_MSG ---

import asyncio
import base64
import logging
import os
import random
import sys
import time
import string as rohit
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from plugins.autoDelete import auto_del_notification, delete_message
from bot import Bot
from config import *
from helper_func import *
from databases.database import db
from databases.db_verify import *

# Explicitly import message templates from FORMATS to avoid NameError
from plugins.FORMATS import FORCE_MSG, START_MSG, TOKEN_PIC

# Create a global dictionary to store chat data cache
chat_data_cache = {}

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    MIN_VERIFY_TIME = 45

    if not await db.present_user(id):
        try:
            await db.add_user(id)
        except Exception as e:
            logging.error(f"Error adding user: {e}")

    VERIFY_EXPIRE, SHORTLINK_URL, SHORTLINK_API, TUT_VID, ADMINS, is_premium = await asyncio.gather(
        db.get_verified_time(),
        db.get_shortener_url(),
        db.get_shortener_api(),
        db.get_tut_video(),
        db.get_all_admins(),
        db.is_premium_user(id)
    )

    if id in ADMINS or is_premium:
        verify_status = {
            'is_verified': True,
            'verify_token': None,
            'verified_time': time.time(),
            'link': ""
        }
    else:
        verify_status = await get_verify_status(id)

    if SHORTLINK_URL:
        if verify_status.get('is_verified') and VERIFY_EXPIRE < (time.time() - verify_status.get('verified_time', 0)):
            await update_verify_status(id, is_verified=False)
            verify_status['is_verified'] = False

        if len(message.command) > 1 and message.command[1].startswith("verify_"):
            token = message.command[1].split("_", 1)[1]
            stored_token = verify_status.get('verify_token')
            generated_time = await get_generated_time(id)

            if not stored_token or stored_token != token:
                return await message.reply("<blockquote>ʏᴏᴜʀ ᴛᴏᴋᴇɴ ɪs ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ. ᴛʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ /start</blockquote>")

            if not generated_time or (time.time() - generated_time) < MIN_VERIFY_TIME:
                return await message.reply_video(
                    video="https://envs.sh/ekQ.mp4",
                    caption="<blockquote><b>🚨 Bʏᴘᴀss Aᴛᴛᴇᴍᴘᴛ Dᴇᴛᴇᴄᴛᴇᴅ! 🚨</b></blockquote>\n\n» ᴡᴀʀɴɪɴɢ...!!! ʏᴏᴜ ᴍᴜsᴛ ʀᴇsᴏʟᴠᴇ ᴛʜᴇ ʟɪɴᴋ ᴛᴏ ᴀᴄᴄᴇss ᴛʜᴇ ғɪʟᴇ. ɴᴏ sʜᴏʀᴛᴄᴜᴛs, ɴᴏ ᴛʀɪᴄᴋs! ᴀɴʏ ᴀᴛᴛᴇᴍᴘᴛ ᴛᴏ ʙʏᴘᴀss ᴛʜᴇ sʏsᴛᴇᴍ ᴡɪʟʟ ᴛʀɪɢɢᴇʀ ᴀɴ ɪɴsᴛᴀɴᴛ ʙᴀɴ! 🚫🔥",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("• ᴄʟɪᴄᴋ ᴛᴏ ᴠᴇʀɪғʏ ᴀɢᴀɪɴ •", url=f"https://t.me/{client.username}?start=start")],
                        [InlineKeyboardButton("• ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ", url=TUT_VID), InlineKeyboardButton("ᴅᴇᴠʟᴏᴘᴇʀ •", url="https://t.me/Urr_Sanjiii")]
                    ])
                )

            await update_verify_status(id, is_verified=True, verified_time=time.time())
            return await message.reply(
                f"<blockquote>» ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs !!, 🥳🥳\n\n»ʏᴏᴜʀ ᴛᴏᴋᴇɴ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ ᴀɴᴅ ɴᴏᴡ ᴠᴀʟɪᴅ ғᴏʀ {get_exp_time(VERIFY_EXPIRE)}\n\n» ɴᴏᴡ ʏᴏᴜ <a href='https://t.me/Mugiwaras_Network'>ɢᴇᴛ ᴀᴄᴇss ᴛᴏ ᴀʟʟ 6 ʙᴏᴛs</a> ᴏғ @Anime_Fury ғᴏʀ {get_exp_time(VERIFY_EXPIRE)}.</blockquote>",
                quote=True, disable_web_page_preview=True
            )

        if not verify_status.get('is_verified'):
            token = ''.join(random.choices(rohit.ascii_letters + rohit.digits, k=10))
            await update_verify_status(id, verify_token=token, link="")
            await store_generated_time(id, time.time())

            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
            
            return await message.reply_photo(
                photo=TOKEN_PIC,
                caption=f"<blockquote><b>›› Hey!!, {message.from_user.mention} ~</b></blockquote>\n\n<i>Your Ads token is expired, refresh your token and try again.</i> \n\n<b>Token Timeout:</b> {get_exp_time(VERIFY_EXPIRE)} \n\n<blockquote expandable><b>What is token?</b> \n<i>This is an ads token. If you pass 1 ad, you can use the bot for {get_exp_time(VERIFY_EXPIRE)} after passing the ad.</i>\n\nOnce done you will <a href='https://t.me/Battousai_Network/31'>get access to all our 6 bots</a> for {get_exp_time(VERIFY_EXPIRE)} which are ⬇️\n\n» @Sukuna_Sama_Bot\n» @Devil_Fruit_Bot\n» @Lord_Aizen_Raven_Bot\n» @Hitokiri_Battousai_Bot\n» @pirate_hunter_zoro_raven_bot\n» @Black_Goku_Raven_Bot\n\n<b>APPLE/IPHONE USERS COPY TOKEN LINK AND OPEN IN CHROME BROWSER</b></blockquote>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("» ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ᴠᴇʀɪғʏ «", url=link)],
                    [InlineKeyboardButton("» ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ/ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ «", url=TUT_VID)],
                    [InlineKeyboardButton("🎁 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ 🔖", callback_data="plan")]
                ])
            )

    if len(message.command) > 1:
        try:
            base64_string = message.command[1]
            decoded_str = await decode(base64_string)
            if not decoded_str:
                return
        except: return

        argument = decoded_str.split("-")
        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
            except: return
        elif len(argument) == 2:
            try: ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except: return

        await message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT)

        try:
            messages = await get_messages(client, ids)
        except Exception:
            return await message.reply("<b><i>sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ..!</i></b>")

        AUTO_DEL, DEL_TIMER, HIDE_CAPTION, CHNL_BTN, PROTECT_MODE = await asyncio.gather(
            db.get_auto_delete(), db.get_del_timer(), db.get_hide_caption(), db.get_channel_button(), db.get_protect_content()
        )
        
        button_name, button_link = await db.get_channel_button_link() if CHNL_BTN else (None, None)
        last_message = None

        for idx, msg in enumerate(messages):
            caption = ""
            if CUSTOM_CAPTION and msg.document:
                caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
            elif not HIDE_CAPTION:
                caption = "" if not msg.caption else msg.caption.html

            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=button_name, url=button_link)]]) if (CHNL_BTN and (msg.document or msg.photo or msg.video or msg.audio)) else msg.reply_markup   

            try:
                copied_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_MODE)
                await asyncio.sleep(0.05)
            except FloodWait as e:
                await asyncio.sleep(getattr(e, 'value', 2) + 0.5) 
                copied_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_MODE)
            except Exception:
                continue
            
            if AUTO_DEL:
                asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                if idx == len(messages) - 1: last_message = copied_msg

        if AUTO_DEL and last_message:
            asyncio.create_task(auto_del_notification(client.username, last_message, DEL_TIMER, message.command[1]))

    else:   
        try:
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name or "",
                    username=f"@{message.from_user.username}" if message.from_user.username else "",
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ᴄʟɪᴄᴋ ғᴏʀ ᴍᴏʀᴇ •", callback_data='about')],
                    [InlineKeyboardButton("• sᴇᴛᴛɪɴɢs", callback_data='setting'), InlineKeyboardButton(' ᴅᴇᴠᴇʟᴏᴘᴇʀ •', url='https://t.me/urr_sanjiii')],
                    [InlineKeyboardButton("• ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ •", url='https://t.me/Mugiwaras_Network')]
                ]),
                message_effect_id=5104841245755180586
            )
        except Exception: pass


@Bot.on_message(filters.command('start') & filters.private & ~banUser)
async def not_joined(client: Client, message: Message):
    user_id = message.from_user.id
    REQFSUB = await db.get_request_forcesub()
    buttons = []
    not_joined_any = False

    try:
        for chat_id in await db.get_all_channels():
            if not await is_userJoin(client, user_id, chat_id):
                not_joined_any = True
                if chat_id not in chat_data_cache:
                    chat_data_cache[chat_id] = await client.get_chat(chat_id)
                data = chat_data_cache[chat_id]

                if REQFSUB and not data.username: 
                    link = await db.get_stored_reqLink(chat_id)
                    if not link:
                        link = (await client.create_chat_invite_link(chat_id=chat_id, creates_join_request=True)).invite_link
                        await db.store_reqLink(chat_id, link)
                else:
                    link = data.invite_link

                buttons.append([InlineKeyboardButton(text='» ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ «', url=link)])

        if not not_joined_any:
            return 

        if REQFSUB:
            byt_links = await db.get_all_fsub_button_links()
            if byt_links:
                for link in byt_links:
                    buttons.append([InlineKeyboardButton(text='» ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ «', url=link)])

        if len(message.command) > 1:
            buttons.append([InlineKeyboardButton(text='‼️ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ ‼️', url=f"https://t.me/{client.username}?start={message.command[1]}")])

        await message.reply_photo(
            photo=random.choice(PICS),
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or "",
                username=f"@{message.from_user.username}" if message.from_user.username else "",
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            message_effect_id=5104841245755180586
        )
    except Exception as e:
        logging.error(f"FSub Error: {e}")


@Bot.on_message(filters.command('restart') & filters.private & filters.user(OWNER_ID))
async def restart_bot(client: Client, message: Message):
    msg = await message.reply("<b><i>» ʀᴇsᴛᴀʀᴛɪɴɢ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ!</i></b>")
    await asyncio.sleep(2)
    await msg.delete()
    os.execl(sys.executable, sys.executable, "main.py")
