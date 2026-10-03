import motor.motor_asyncio
from config import DB_URL, DB_NAME
import logging
from datetime import datetime, timedelta

# PyMongo ko puri tarah hata diya gaya hai kyunki Async bots me Sync library lagane se bot lag karta hai.

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

class Rohit:
    def __init__(self, DB_URL, DB_NAME):
        # OPTIMIZATION: Added Connection Pooling for 1k+ users
        # Isse database requests turant process hongi bina server ko hang kiye
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(
            DB_URL,
            maxPoolSize=100,       # 100 concurrent queries aaram se handle karega
            minPoolSize=10,        # Minimum 10 connection hamesha ready rahenge
            serverSelectionTimeoutMS=5000
        )
        self.database = self.dbclient[DB_NAME]

        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.user_data = self.database['users']
        self.banned_user_data = self.database['banned_user']
        self.autho_user_data = self.database['autho_user']
        self.shortener_data = self.database['shortener']
        self.settings_data = self.database['settings']
        
        self.auto_delete_data = self.database['auto_delete']
        self.hide_caption_data = self.database['hide_caption']
        self.protect_content_data = self.database['protect_content']
        self.channel_button_data = self.database['channel_button']
        self.del_timer_data = self.database['del_timer']
        self.channel_button_link_data = self.database['channelButton_link']

        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
        self.store_reqLink_data = self.database['store_reqLink']

    # Shortener Token
    async def set_shortener_url(self, url):
        try:
            existing = await self.shortener_data.find_one({"active": True}, {"_id": 1})
            if existing:
                await self.shortener_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"shortener_url": url, "updated_at": datetime.utcnow()}}
                )
            else:
                await self.shortener_data.insert_one({
                    "shortener_url": url,
                    "api_key": None,
                    "active": True,
                    "created_at": datetime.utcnow()
                })
            return True
        except Exception as e:
            logging.error(f"Error setting shortener URL: {e}")
            return False

    async def set_shortener_api(self, api):
        try:
            existing = await self.shortener_data.find_one({"active": True}, {"_id": 1})
            if existing:
                await self.shortener_data.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"api_key": api, "updated_at": datetime.utcnow()}}
                )
            else:
                await self.shortener_data.insert_one({
                    "shortener_url": None,
                    "api_key": api,
                    "active": True,
                    "created_at": datetime.utcnow()
                })
            return True
        except Exception as e:
            logging.error(f"Error setting shortener API key: {e}")
            return False

    async def get_shortener_url(self):
        try:
            shortener = await self.shortener_data.find_one({"active": True}, {"shortener_url": 1})
            return shortener.get("shortener_url") if shortener else None
        except Exception as e:
            return None

    async def get_shortener_api(self):
        try:
            shortener = await self.shortener_data.find_one({"active": True}, {"api_key": 1})
            return shortener.get("api_key") if shortener else None
        except Exception as e:
            return None

    async def deactivate_shortener(self):
        try:
            await self.shortener_data.update_many({"active": True}, {"$set": {"active": False}})
            return True
        except Exception as e:
            return False

    async def set_verified_time(self, verified_time: int):
        try:
            result = await self.settings_data.update_one(
                {"_id": "verified_time"},
                {"$set": {"verified_time": verified_time}},
                upsert=True
            )
            return result.modified_count > 0
        except Exception as e:
            return False

    async def get_verified_time(self):
        try:
            settings = await self.settings_data.find_one({"_id": "verified_time"}, {"verified_time": 1})
            return settings.get("verified_time", None) if settings else None
        except Exception as e:
            return None

    async def set_tut_video(self, video_url: str):
        try:
            result = await self.settings_data.update_one(
                {"_id": "tutorial_video"},
                {"$set": {"tutorial_video_url": video_url}},
                upsert=True
            )
            return result.modified_count > 0
        except Exception as e:
            return False

    async def get_tut_video(self):
        try:
            settings = await self.settings_data.find_one({"_id": "tutorial_video"}, {"tutorial_video_url": 1})
            return settings.get("tutorial_video_url", None) if settings else None
        except Exception as e:
            return None

    # USER MANAGEMENT
    async def present_user(self, user_id: int):
        found = await self.user_data.find_one({'_id': user_id}, {"_id": 1})
        return bool(found)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})

    async def full_userbase(self):
        # OPTIMIZED: Sirf _id fetch karega, saara data nahi. Saves HUGE amount of RAM.
        user_docs = await self.user_data.find({}, {"_id": 1}).to_list(length=None)
        return [doc['_id'] for doc in user_docs]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})

    async def update_shortener(self, user_id: int, site: str, api_key: str):
        await self.shortener_data.update_one(
            {'_id': user_id},
            {'$set': {'site': site, 'api': api_key}},
            upsert=True
        )

    async def toggle_shortener(self, user_id: int, enable: bool):
        await self.shortener_data.update_one(
            {'_id': user_id},
            {'$set': {'enabled': enable}},
            upsert=True
        )

    async def fetch_shortener(self, user_id: int):
        user = await self.shortener_data.find_one({'_id': user_id}, {"site": 1, "api": 1, "enabled": 1})
        if user:
            return {
                'site': user.get('site'),
                'api': user.get('api'),
                'enabled': user.get('enabled', False)
            }
        return None

    # CHANNEL BUTTON SETTINGS
    async def set_channel_button_link(self, button_name: str, button_link: str):
        await self.channel_button_link_data.delete_many({})
        await self.channel_button_link_data.insert_one({'button_name': button_name, 'button_link': button_link})

    async def get_channel_button_link(self):
        data = await self.channel_button_link_data.find_one({}, {"button_name": 1, "button_link": 1})
        if data:
            return data.get('button_name'), data.get('button_link')
        return ' Channel', 'https://t.me/Javpostr'

    # DELETE TIMER SETTINGS
    async def set_del_timer(self, value: int):        
        existing = await self.del_timer_data.find_one({}, {"_id": 1})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({}, {"value": 1})
        if data:
            return data.get('value', 600)
        return 600

    # SET BOOLEAN VALUES
    async def set_auto_delete(self, value: bool):
        existing = await self.auto_delete_data.find_one({}, {"_id": 1})
        if existing: await self.auto_delete_data.update_one({}, {'$set': {'value': value}})
        else: await self.auto_delete_data.insert_one({'value': value})

    async def set_hide_caption(self, value: bool):
        existing = await self.hide_caption_data.find_one({}, {"_id": 1})
        if existing: await self.hide_caption_data.update_one({}, {'$set': {'value': value}})
        else: await self.hide_caption_data.insert_one({'value': value})

    async def set_protect_content(self, value: bool):
        existing = await self.protect_content_data.find_one({}, {"_id": 1})
        if existing: await self.protect_content_data.update_one({}, {'$set': {'value': value}})
        else: await self.protect_content_data.insert_one({'value': value})

    async def set_channel_button(self, value: bool):
        existing = await self.channel_button_data.find_one({}, {"_id": 1})
        if existing: await self.channel_button_data.update_one({}, {'$set': {'value': value}})
        else: await self.channel_button_data.insert_one({'value': value})

    async def set_request_forcesub(self, value: bool):
        existing = await self.rqst_fsub_data.find_one({}, {"_id": 1})
        if existing: await self.rqst_fsub_data.update_one({}, {'$set': {'value': value}})
        else: await self.rqst_fsub_data.insert_one({'value': value})

    # GET BOOLEAN VALUES (Optimized with Projections)
    async def get_auto_delete(self):
        data = await self.auto_delete_data.find_one({}, {"value": 1})
        return data.get('value', False) if data else False

    async def get_hide_caption(self):
        data = await self.hide_caption_data.find_one({}, {"value": 1})
        return data.get('value', False) if data else False

    async def get_protect_content(self):
        data = await self.protect_content_data.find_one({}, {"value": 1})
        return data.get('value', False) if data else False

    async def get_channel_button(self):
        data = await self.channel_button_data.find_one({}, {"value": 1})
        return data.get('value', False) if data else False

    async def get_request_forcesub(self):
        data = await self.rqst_fsub_data.find_one({}, {"value": 1})
        return data.get('value', False) if data else False

    # CHANNEL MANAGEMENT
    async def channel_exist(self, channel_id: int):
        found = await self.channel_data.find_one({'_id': channel_id}, {"_id": 1})
        return bool(found)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.channel_data.insert_one({'_id': channel_id})

    async def del_channel(self, channel_id: int):
        await self.channel_data.delete_one({'_id': channel_id})

    async def get_all_channels(self):
        channel_docs = await self.channel_data.find({}, {"_id": 1}).to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    # ADMIN USER MANAGEMENT
    async def admin_exist(self, admin_id: int):
        found = await self.admins_data.find_one({'_id': admin_id}, {"_id": 1})
        return bool(found)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})

    async def del_admin(self, admin_id: int):
        await self.admins_data.delete_one({'_id': admin_id})

    async def get_all_admins(self):
        users_docs = await self.admins_data.find({}, {"_id": 1}).to_list(length=None)
        return [doc['_id'] for doc in users_docs]

    # BAN USER MANAGEMENT
    async def ban_user_exist(self, user_id: int):
        found = await self.banned_user_data.find_one({'_id': user_id}, {"_id": 1})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})

    async def del_ban_user(self, user_id: int):
        await self.banned_user_data.delete_one({'_id': user_id})

    async def get_ban_users(self):
        users_docs = await self.banned_user_data.find({}, {"_id": 1}).to_list(length=None)
        return [doc['_id'] for doc in users_docs]

    # REQUEST FORCE-SUB MANAGEMENT
    async def add_reqChannel(self, channel_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$setOnInsert': {'user_ids': []}},
            upsert=True
        )

    async def set_request_forcesub_channel(self, channel_id: int, fsub_mode: bool):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$set': {'fsub_mode': fsub_mode}},
            upsert=True
        )

    async def reqSent_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$addToSet': {'user_ids': user_id}}, 
            upsert=True
        )

    async def del_reqSent_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$pull': {'user_ids': user_id}}
        )

    async def clear_reqSent_user(self, channel_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$set': {'user_ids': []}}
        )

    async def reqSent_user_exist(self, channel_id: int, user_id: int):
        found = await self.rqst_fsub_Channel_data.find_one(
            {'_id': channel_id, 'user_ids': user_id}, {"_id": 1}
        )
        return bool(found)

    async def del_reqChannel(self, channel_id: int):
        await self.rqst_fsub_Channel_data.delete_one({'_id': channel_id})

    async def reqChannel_exist(self, channel_id: int):
        found = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id}, {"_id": 1})
        return bool(found)

    async def get_reqSent_user(self, channel_id: int):
        data = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id}, {"user_ids": 1})
        return data.get('user_ids', []) if data else []

    async def get_reqChannel(self):
        channel_docs = await self.rqst_fsub_Channel_data.find({}, {"_id": 1}).to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    async def get_reqLink_channels(self):
        channel_docs = await self.store_reqLink_data.find({}, {"_id": 1}).to_list(length=None)
        return [doc['_id'] for doc in channel_docs]

    async def get_stored_reqLink(self, channel_id: int):
        data = await self.store_reqLink_data.find_one({'_id': channel_id}, {"link": 1})
        return data.get('link') if data else None

    async def store_reqLink(self, channel_id: int, link: str):
        await self.store_reqLink_data.update_one(
            {'_id': channel_id}, 
            {'$set': {'link': link}}, 
            upsert=True
        )

    async def del_stored_reqLink(self, channel_id: int):
        await self.store_reqLink_data.delete_one({'_id': channel_id})

    # FSUB BUTTON LINKS MANAGEMENT
    async def add_fsub_button_link(self, link: str):
        fsub_links = self.database['fsub_button_links']
        await fsub_links.insert_one({'link': link, 'created_at': datetime.utcnow()})
        return True

    async def get_all_fsub_button_links(self):
        fsub_links = self.database['fsub_button_links']
        links_data = await fsub_links.find({}, {"link": 1}).to_list(length=None)
        return [link.get('link') for link in links_data]

    async def delete_all_fsub_button_links(self):
        fsub_links = self.database['fsub_button_links']
        result = await fsub_links.delete_many({})
        return result.deleted_count > 0

    async def get_fsub_button_links_count(self):
        fsub_links = self.database['fsub_button_links']
        return await fsub_links.count_documents({})

    # PREMIUM USER MANAGEMENT
    async def set_premium_user(self, user_id: int, days: int):
        premium_data = self.database['premium_users']
        expiry_date = datetime.utcnow() + timedelta(days=days)
        await premium_data.update_one(
            {'_id': user_id},
            {'$set': {'expiry_date': expiry_date, 'added_on': datetime.utcnow()}},
            upsert=True
        )
        return True

    async def is_premium_user(self, user_id: int):
        premium_data = self.database['premium_users']
        user = await premium_data.find_one({'_id': user_id}, {"expiry_date": 1})
        if not user:
            return False
        
        expiry_date = user.get('expiry_date')
        if expiry_date and expiry_date > datetime.utcnow():
            return True
        else:
            if expiry_date and expiry_date <= datetime.utcnow():
                await premium_data.delete_one({'_id': user_id})
            return False

    async def remove_premium_user(self, user_id: int):
        premium_data = self.database['premium_users']
        result = await premium_data.delete_one({'_id': user_id})
        return result.deleted_count > 0

    async def get_premium_user_info(self, user_id: int):
        premium_data = self.database['premium_users']
        user = await premium_data.find_one({'_id': user_id}, {"expiry_date": 1, "added_on": 1})
        if user:
            return {
                'user_id': user_id,
                'expiry_date': user.get('expiry_date'),
                'added_on': user.get('added_on')
            }
        return None

    async def get_all_premium_users(self):
        premium_data = self.database['premium_users']
        users = await premium_data.find({}, {"_id": 1, "expiry_date": 1}).to_list(length=None)
        active_users = []
        for user in users:
            expiry_date = user.get('expiry_date')
            if expiry_date and expiry_date > datetime.utcnow():
                active_users.append(user['_id'])
            else:
                await premium_data.delete_one({'_id': user['_id']})
        return active_users

db = Rohit(DB_URL, DB_NAME)
