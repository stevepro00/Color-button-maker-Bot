import logging
import datetime
from pyrogram import Client, filters, StopPropagation, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from config import AUTH_CHANNELS, ADMIN, IS_FSUB, FSUB_EXPIRE, FSUB_PIC, SUCCESS_PIC
from Script import text
from .database import sb

async def check_all_channels_joined(bot: Client, user_id: int):
    for channel_id in AUTH_CHANNELS:
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                return False
        except UserNotParticipant:
            return False
        except Exception:
            pass
    return True

async def auto_delete_fsub_and_start(client: Client, user_id: int):
    if not await check_all_channels_joined(client, user_id):
        return
    
    session = await sb.get_session(user_id)
    if session and isinstance(session, dict) and session.get("fsub_msg_id"):
        try:
            await client.delete_messages(user_id, session["fsub_msg_id"])
        except Exception as e:
            logging.error(f"Failed to delete fsub message: {e}")
            
        session["fsub_msg_id"] = None
        await sb.set_session(user_id, session)

        user = await client.get_users(user_id)
        bot_user = await client.get_me()
        try:
            await client.send_photo(
                chat_id=user_id,
                photo=SUCCESS_PIC,
                caption=text.FSUB_SUCCESS.format(user.mention), 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ 𝖲𝗍𝖺𝗋𝗍", url=f"https://telegram.me/{bot_user.username}?start=start")]])
            )
        except Exception:
            pass

@Client.on_chat_member_updated(filters.chat(AUTH_CHANNELS))
async def check_member_updates(client: Client, message: ChatMemberUpdated):
    if not message.from_user:
        return

    user_id = message.from_user.id
    
    if message.new_chat_member and message.new_chat_member.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        await auto_delete_fsub_and_start(client, user_id)

async def is_subscribed(bot: Client, user_id: int):
    missing = []
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=FSUB_EXPIRE) if FSUB_EXPIRE > 0 else None
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

async def get_fsub(bot: Client, message: Message) -> bool:
    user_id = message.from_user.id
    if user_id == ADMIN:
        return True
        
    missing = await is_subscribed(bot, user_id)
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
    buttons.append([InlineKeyboardButton("🔄 𝖳𝗋𝗒 𝖠𝗀𝖺𝗂𝗇", url=f"https://telegram.me/{bot_user.username}?start=start")])
    
    msg = await message.reply_photo(
        photo=FSUB_PIC,
        caption=text.FSUB_TEXT.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
    session = await sb.get_session(user_id) or {}
    session["fsub_msg_id"] = msg.id
    await sb.set_session(user_id, session)
    
    return False

@Client.on_message(filters.private & ~filters.user(ADMIN) & ~filters.bot & ~filters.service & ~filters.me, group=-10)
async def global_fsub_checker(client: Client, message: Message):
    if not IS_FSUB:
        return
    if not await get_fsub(client, message):
        raise StopPropagation
