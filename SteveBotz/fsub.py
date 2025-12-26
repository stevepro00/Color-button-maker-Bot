import logging
import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pyrogram.enums import ParseMode
from config import AUTH_CHANNELS, AUTH_REQ_CHANNELS, ADMIN, FSUB_EXPIRE, DB_URI, DB_NAME, IS_FSUB, FSUB_PIC

class SteveBotz:
    def __init__(self):
        client = AsyncIOMotorClient(DB_URI)
        db = client[DB_NAME]
        self.join_requests = db["join_requests"]
        if FSUB_EXPIRE > 0:
            self.join_requests.create_index("created_at", expireAfterSeconds=FSUB_EXPIRE * 60)

    async def add_join_req(self, user_id: int, channel_id: int):
        await self.join_requests.update_one(
            {"user_id": user_id},
            {"$addToSet": {"channels": channel_id}, "$setOnInsert": {"created_at": datetime.datetime.utcnow()}},
            upsert=True
        )

    async def has_joined_channel(self, user_id: int, channel_id: int) -> bool:
        doc = await self.join_requests.find_one({"user_id": user_id})
        return bool(doc and channel_id in doc.get("channels", []))

    async def del_join_req(self):
        await self.join_requests.drop()

sb = SteveBotz()

def is_auth_req_channel(_, __, update):
    return update.chat.id in AUTH_REQ_CHANNELS

@Client.on_chat_join_request(filters.create(is_auth_req_channel))
async def join_reqs(client: Client, message: ChatJoinRequest):
    await sb.add_join_req(message.from_user.id, message.chat.id)

@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMIN))
async def del_requests(client: Client, message: Message):
    await sb.del_join_req()
    await message.reply("**⚙ Successfully join request cache deleted.**")

async def is_subscribed(bot: Client, user_id: int, expire_at):
    missing = []
    for channel_id in AUTH_CHANNELS:
        try:
            await bot.get_chat_member(channel_id, user_id)
        except UserNotParticipant:
            try:
                chat = await bot.get_chat(channel_id)
                invite = await bot.create_chat_invite_link(channel_id, expire_date=expire_at)
                missing.append((chat.title, invite.invite_link))
            except ChatAdminRequired:
                logging.error(f"Bot not admin in auth channel {channel_id}")
            except Exception:
                pass
        except Exception:
            pass
    return missing

async def is_req_subscribed(bot: Client, user_id: int, expire_at):
    missing = []
    for channel_id in AUTH_REQ_CHANNELS:
        if await sb.has_joined_channel(user_id, channel_id):
            continue
        try:
            chat = await bot.get_chat(channel_id)
            invite = await bot.create_chat_invite_link(channel_id, creates_join_request=True, expire_date=expire_at)
            missing.append((chat.title, invite.invite_link))
        except ChatAdminRequired:
            logging.error(f"Bot not admin in request channel {channel_id}")
        except Exception:
            pass
    return missing

async def get_fsub(bot: Client, message: Message) -> bool:
    user_id = message.from_user.id
    if user_id == ADMIN:
        return True
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=FSUB_EXPIRE) if FSUB_EXPIRE > 0 else None
    missing = []
    if AUTH_CHANNELS:
        missing.extend(await is_subscribed(bot, user_id, expire_at))
    if AUTH_REQ_CHANNELS:
        missing.extend(await is_req_subscribed(bot, user_id, expire_at))
    if not missing:
        return True
    bot_user = await bot.get_me()
    buttons = []
    for i in range(0, len(missing), 2):
        row = []
        for j in range(2):
            if i + j < len(missing):
                title, link = missing[i + j]
                row.append(InlineKeyboardButton(f"{i + j + 1}. {title}", url=link))
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔄 Try Again", url=f"https://telegram.me/{bot_user.username}?start=start")])
    
    await message.reply_photo(
        photo=FSUB_PIC,
        caption=f"**ʜᴇʏ {message.from_user.mention} 🙋🏻‍♂️ ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ,\n\nTᴏ ᴄᴏɴᴛɪɴᴜᴇ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ, ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ 💬\n\nSᴇʀᴠᴇʀ ʟᴏᴀᴅ ɪs ʜɪɢʜ, sᴏ ᴀᴄᴄᴇss ɪs ʟɪᴍɪᴛᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴍᴇᴍʙᴇʀs ᴏɴʟʏ** 🚀",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return False

