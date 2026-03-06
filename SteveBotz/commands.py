import random
import re
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import PICS, BOT_USERNAME, LOG_CHANNEL, SUPPORT
import asyncio
from Script import text
from .database import sb
from .admin import parse_button_markup

# Link extractor helper
def parse_tg_link(link: str):
    match_c = re.match(r"https?://t\.me/c/(\d+)/(\d+)", link)
    if match_c: return int("-100" + match_c.group(1)), int(match_c.group(2))
    match_u = re.match(r"https?://t\.me/([^/]+)/(\d+)", link)
    if match_u: return match_u.group(1), int(match_u.group(2))
    return None, None

@Client.on_message(filters.command("start"))
async def start_cmd(client, message):           
    if await sb.get_user(message.from_user.id) is None:
        await sb.add_user(message.from_user.id, message.from_user.first_name)
        
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=text.START.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Create Post ➕", callback_data="create_post")],
            [InlineKeyboardButton("✏️ Edit Post ✏️", callback_data="edit_post")],
            [InlineKeyboardButton('ℹ️ Help', callback_data='help'), InlineKeyboardButton('💌 About', callback_data='about')]
        ])
    )

@Client.on_message(filters.command("connect") & filters.private)
async def connect_channel(client, message):
    if len(message.command) < 2:
        return await message.reply("**⚠️ Syntax:** `/connect -100xxxxxxx`")
    try:
        channel_id = int(message.command[1])
        chat = await client.get_chat(channel_id)
        member = await chat.get_member(client.me.id)
        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return await message.reply("❌ I must be an admin in the channel to post!")
            
        await sb.connect_channel(message.from_user.id, channel_id, chat.title)
        await message.reply(f"**✅ Successfully connected to {chat.title}!**\n\nClick on **➕ Create Post ➕** from /start to begin.")
    except Exception as e:
        await message.reply(f"**❌ Error:** `{e}`")

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_action(client, message):
    await sb.set_session(message.from_user.id, None)
    await message.reply("**🗑 Action Cancelled. Use /start to begin again.**")

@Client.on_message(filters.private & ~filters.command(["start", "help", "connect", "edit", "cancel", "stats", "broadcast", "restart"]))
async def fsm_handler(client, message):
    session = await sb.get_session(message.from_user.id)
    if not session or not isinstance(session, dict): return
    state = session.get("state")

    # ---- CREATE POST WORKFLOW ----
    if state == "WAITING_FOR_CONTENT":
        session["draft_msg_id"] = message.id
        session["state"] = "WAITING_FOR_BUTTONS"
        await sb.set_session(message.from_user.id, session)
        await message.reply("✅ **Content saved!**\n\nNow send your button format like this:\n\n`[Btn 1](url:danger) | [Btn 2](url:success)`\n\nType `/cancel` to abort.")

    elif state == "WAITING_FOR_BUTTONS":
        markup = parse_button_markup(message.text)
        if not markup and message.text.lower() != "skip":
            return await message.reply("❌ No valid buttons found. Check format or send 'skip' to send without buttons.")
            
        draft_msg = await client.get_messages(message.chat.id, session["draft_msg_id"])
        post_id = await sb.save_post(message.from_user.id, draft_msg, message.text if markup else "")
        
        session["draft_buttons"] = message.text if markup else ""
        session["post_id"] = post_id
        session["state"] = "READY_TO_SEND"
        session["selected_channels"] = [] 
        await sb.set_session(message.from_user.id, session)

        await message.reply("👀 **Here is your preview:**")
        preview = await client.copy_message(message.chat.id, message.chat.id, session["draft_msg_id"], reply_markup=markup)
        
        # Trigger UI Builder for multiple channels
        channels = await sb.get_connected_channels(message.from_user.id)
        from .callback import get_channel_kb
        await message.reply("📡 **Where do you want to send this post?**\nSelect channels below:", reply_markup=get_channel_kb(channels, [], post_id))

    # ---- EDIT POST WORKFLOW ----
    elif state == "WAITING_FOR_EDIT_LINK":
        ch_id, msg_id = parse_tg_link(message.text)
        if not ch_id or not msg_id:
            return await message.reply("❌ Invalid Link! Send a valid Telegram post link.\nExample: `https://t.me/c/1234567/89`")
        
        session["edit_ch_id"] = ch_id
        session["edit_msg_id"] = msg_id
        session["state"] = "WAITING_FOR_EDIT_CONTENT"
        await sb.set_session(message.from_user.id, session)
        await message.reply("🔗 **Link saved!**\n\nNow send the **NEW content** (text, photo, etc...) for this post.")

    elif state == "WAITING_FOR_EDIT_CONTENT":
        session["draft_msg_id"] = message.id
        session["state"] = "WAITING_FOR_EDIT_BUTTONS"
        await sb.set_session(message.from_user.id, session)
        await message.reply("✅ **New Content saved!**\n\nNow send the **NEW buttons** format.")

    elif state == "WAITING_FOR_EDIT_BUTTONS":
        markup = parse_button_markup(message.text)
        draft_msg = await client.get_messages(message.chat.id, session["draft_msg_id"])
        post_id = await sb.save_post(message.from_user.id, draft_msg, message.text if markup else "")
        
        session["draft_buttons"] = message.text if markup else ""
        session["post_id"] = post_id
        session["state"] = "READY_TO_EDIT"
        await sb.set_session(message.from_user.id, session)

        await message.reply("👀 **Edit Preview:**")
        await client.copy_message(message.chat.id, message.chat.id, session["draft_msg_id"], reply_markup=markup)
        
        await message.reply(
            f"**Inline Post ID generated:** `{post_id}`\n\nAre you sure you want to update the message in the channel?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Edit", callback_data="confirm_edit")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
        )
