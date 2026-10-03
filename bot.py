# +++ Made By Sanjiii [telegram username: @Urr_Sanjiii] +++
# --- Optimized for High Performance & VPS Stability ---

from aiohttp import web
from plugins import web_server
import asyncio
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, CHANNEL_ID, PORT, OWNER_ID

class Bot(Client):
    def __init__(self):
        # OPTIMIZATION: Ensure TG_BOT_WORKERS is at least 150-200 for high traffic (1k+ users).
        # Agar config.py me ye kam set hai, toh bot messages queue me daal dega aur slow lagega.
        workers_count = int(TG_BOT_WORKERS) if hasattr(sys.modules['config'], 'TG_BOT_WORKERS') and int(TG_BOT_WORKERS) >= 150 else 200

        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=workers_count, # Increased default workers to handle more concurrent users
            bot_token=TG_BOT_TOKEN,
            max_concurrent_transmissions=20 # Helps when sending multiple files simultaneously
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        bot_info = await self.get_me()
        self.name = bot_info.first_name
        self.username = bot_info.username
        self.uptime = datetime.now()
        
        # Setup DB Channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)

            # Avoid making API calls to export invite link if it's already a public channel (username exists)
            if not db_channel.username and not db_channel.invite_link:
                try:
                    db_channel.invite_link = (await self.create_chat_invite_link(CHANNEL_ID)).invite_link
                except Exception:
                    pass # Fallback if bot doesn't have invite permissions

            self.db_channel = db_channel
            
            # Simple permission check
            test = await self.send_message(chat_id=db_channel.id, text="Testing Database Channel Permissions...")
            await test.delete()
            
        except Exception as e:
            self.LOGGER(__name__).warning(f"Error accessing DB Channel: {e}")
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel and has proper Permissions. Check CHANNEL_ID: {CHANNEL_ID}")
            self.LOGGER(__name__).info('Bot Stopped..')
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"ᴀᴅᴠᴀɴᴄᴇ ғɪʟᴇ-sʜᴀʀɪɴɢ ʙᴏᴛ ᴡɪᴛʜ ᴛᴏᴋᴇɴ ғᴇᴀᴛᴜʀᴇ V5 ᴍᴀᴅᴇ ʙʏ ➪ @Urr_Sanjiii")
        self.LOGGER(__name__).info(f"{self.name} Bot Running..! [Workers: {self.workers}]")
        self.LOGGER(__name__).info(f"ʜᴏsᴛᴇᴅ sᴜᴄᴇssғᴜʟʟʏ ʙᴀʙᴇʏʏʏ !! ✅")
        
        # Web Server Setup for pinging (Uptime/Health checks)
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        # Startup notification
        try: 
            await self.send_message(
                OWNER_ID, 
                text=f"<b><blockquote>ʙᴏᴛ sᴜᴄᴇssғᴜʟʟʏ ʀᴇsᴛᴀʀᴛᴇᴅ ʙᴏss ✅\n\n» ᴍʏ ᴜɪ ɪs ᴍᴀᴅᴇ ʙʏ @urr_sanjiii\n\nᴄʟɪᴄᴋ ᴏɴ : /start ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ ʙᴏᴛ...!!!</blockquote></b>",
                disable_web_page_preview=True
            )
        except Exception: 
            pass

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info(f"{self.name} Bot stopped.")
