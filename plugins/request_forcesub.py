# +++ Made By Sanjiii [telegram username: @Urr_Sanjiii] +++
# --- Optimized for High Performance & Low VPS Load ---

import asyncio
from bot import Bot
from databases.database import db
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated

# This handler captures membership updates (like when a user leaves, banned)
@Bot.on_chat_member_updated()
async def handle_Chatmembers(client: Bot, chat_member_updated: ChatMemberUpdated):    
    old_member = chat_member_updated.old_chat_member
    new_member = chat_member_updated.new_chat_member

    # 1. EARLY EXIT: Agar user pehle MEMBER nahi tha, toh aage badhne ki zaroorat hi nahi (Saves CPU)
    if not old_member or old_member.status != ChatMemberStatus.MEMBER:
        return
    
    # 2. EARLY EXIT: Agar status change hua hai par user abhi bhi MEMBER hai (eg. Admin ne koi permission change ki ho)
    if new_member and new_member.status == ChatMemberStatus.MEMBER:
        return

    chat_id = chat_member_updated.chat.id

    if await db.reqChannel_exist(chat_id):
        user_id = old_member.user.id
        
        # 3. OPTIMIZATION: Database file me "$pull" function set hai, isliye pehle "exist" check karna waste of query hai.
        # Direct delete task create karo aur event loop ko free kardo. (Non-blocking execution)
        asyncio.create_task(db.del_reqSent_user(chat_id, user_id))
            

# This handler will capture any join request to the channel/group where the bot is an admin
@Bot.on_chat_join_request()
async def handle_join_request(client: Bot, chat_join_request):
    chat_id = chat_join_request.chat.id  
    
    if await db.reqChannel_exist(chat_id):
        user_id = chat_join_request.from_user.id 

        # 3. OPTIMIZATION: Database me "$addToSet" use hua hai, toh duplicate entry MongoDB khud rok lega.
        # Check karne ki query hata di aur isko background task (asyncio.create_task) me daal diya taaki bot turant aage badh jaye.
        asyncio.create_task(db.reqSent_user(chat_id, user_id))
        
        # Note: Agar tum chahte ho ki bot join request automatically ACCEPT (Approve) kar le, 
        # toh yahan ye neeche wali line ka '#' hata dena:
        # asyncio.create_task(client.approve_chat_join_request(chat_id, user_id))
