import random
from pyrogram import Client, filters, enums
from pyrogram.errors import *
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import PICS, BOT_USERNAME, LOG_CHANNEL, SUPPORT
import asyncio
from Script import text
from .database import sb
from .admin import parse_button_markup

@Client.on_message(filters.command("start"))
async def start_cmd(client, message):           
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=text.START.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('ℹ️ ʜᴇʟᴘ', callback_data='help'),
             InlineKeyboardButton('💌 ᴀʙᴏᴜᴛ', callback_data='about')]
        ])
    )
    
    if await sb.get_user(message.from_user.id) is None:
        await sb.add_user(message.from_user.id, message.from_user.first_name)
        bot = await client.get_me()
        await client.send_message(
            LOG_CHANNEL,
            text.LOG.format(
                message.from_user.id,
                message.from_user.first_name or "N/A",
                f"@{message.from_user.username}" if message.from_user.username else "N/A",
                bot.username
            )
        )

@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):    
    msg = await message.reply(text.HELP, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🪷 𝘚𝘶𝘱𝘱𝘰𝘳𝘵 𝘎𝘳𝘰𝘶𝘱", url=SUPPORT)]]))
    await asyncio.sleep(300)
    await msg.delete()
    try:
        await message.delete()
    except:
        pass

@Client.on_message(filters.command("connect") & filters.private)
async def connect_channel(client, message):
    if len(message.command) < 2:
        return await message.reply("**⚠️ Syntax:** `/connect -100xxxxxxx`\nMake sure I am an admin in that channel first!")
    
    try:
        channel_id = int(message.command[1])
        chat = await client.get_chat(channel_id)
        member = await chat.get_member(client.me.id)
        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return await message.reply("❌ I must be an admin in the channel to post!")
            
        await sb.connect_channel(message.from_user.id, channel_id)
        await message.reply(f"**✅ Successfully connected to {chat.title}!**\nNow, send me a post to create.")
    except Exception as e:
        await message.reply(f"**❌ Error:** Make sure the ID is correct and I am an admin.\n`{str(e)}`")

@Client.on_message(filters.command("edit") & filters.private)
async def edit_post(client, message):
    if len(message.command) < 2:
        return await message.reply("**⚠️ Syntax:** `/edit <message_id>`\nReply to this with the new text and buttons.")
    
    channel_id = await sb.get_connected_channel(message.from_user.id)
    if not channel_id:
        return await message.reply("❌ Please `/connect` a channel first.")
        
    msg_id = int(message.command[1])
    await message.reply(
        f"**✏️ Editing Message ID {msg_id} in your connected channel.**\n\n"
        f"Now, send me the new content and buttons for this post.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Cancel Edit", callback_data="cancel", style=enums.ButtonStyle.DANGER)
        ]])
    )
    await sb.set_session(message.from_user.id, {"action": "edit", "msg_id": msg_id})

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "connect", "edit", "stats", "broadcast", "restart", "delreq"]))
async def create_post_preview(client, message):
    reply_markup, text_content = parse_button_markup(message.text)
    
    session = await sb.get_session(message.from_user.id)
    if session and isinstance(session, dict) and session.get("action") == "edit":
        channel_id = await sb.get_connected_channel(message.from_user.id)
        try:
            await client.edit_message_text(
                chat_id=channel_id,
                message_id=session["msg_id"],
                text=text_content,
                reply_markup=reply_markup
            )
            await message.reply("**✅ Post successfully edited in the channel!**")
        except Exception as e:
            await message.reply(f"**❌ Failed to edit:** `{str(e)}`")
        finally:
            await sb.set_session(message.from_user.id, None)
        return

    if not text_content:
        return await message.reply(
            "**❌ No valid buttons found in your message or text is empty.**\n\n"
            "Use the format:\n"
            "`Your message text here`\n"
            "`[Button Name](link_or_data | style)`"
        )

    preview_msg = await message.reply_text(
        text=text_content,
        reply_markup=reply_markup
    )
    
    await sb.set_session(message.from_user.id, {"draft": message.text})
    
    controls = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Send to Channel", callback_data="send_channel", style=enums.ButtonStyle.SUCCESS)],
        [InlineKeyboardButton("💾 Save for Inline Mode", callback_data="save_inline", style=enums.ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("❌ Discard", callback_data="cancel", style=enums.ButtonStyle.DANGER)]
    ])
    
    await message.reply(
        "**👀 Preview generated above!**\nWhat would you like to do with this post?",
        reply_markup=controls,
        reply_to_message_id=preview_msg.id
    )
