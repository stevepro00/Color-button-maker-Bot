import random
from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAnimation, InputMediaAudio
from Script import text
from config import PICS, UPDATE, SUPPORT
from .database import sb
from .admin import parse_button_markup

def get_channel_kb(channels: list, selected: list, post_id: str):
    kb = []
    for ch in channels:
        mark = "✅" if ch["id"] in selected else "❌"
        kb.append([InlineKeyboardButton(f"{mark} {ch['title']}", callback_data=f"toggle_{ch['id']}")])
    kb.append([InlineKeyboardButton("🚀 Send to Selected Channels", callback_data="send_to_selected")])
    kb.append([InlineKeyboardButton("🗑 Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(kb)

# Media Editor Helper Function
async def edit_channel_message(client, chat_id, msg_id, draft_msg, markup):
    if draft_msg.text:
        await client.edit_message_text(chat_id, msg_id, text=draft_msg.text, reply_markup=markup)
    elif draft_msg.photo:
        await client.edit_message_media(chat_id, msg_id, media=InputMediaPhoto(draft_msg.photo.file_id, caption=draft_msg.caption or ""), reply_markup=markup)
    elif draft_msg.video:
        await client.edit_message_media(chat_id, msg_id, media=InputMediaVideo(draft_msg.video.file_id, caption=draft_msg.caption or ""), reply_markup=markup)
    elif draft_msg.document:
        await client.edit_message_media(chat_id, msg_id, media=InputMediaDocument(draft_msg.document.file_id, caption=draft_msg.caption or ""), reply_markup=markup)

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    if query.data == "start":
        await query.message.edit_media(
            InputMediaPhoto(media=random.choice(PICS), caption=text.START.format(query.from_user.mention)),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Create Post ➕", callback_data="create_post")],
                [InlineKeyboardButton("✏️ Edit Post ✏️", callback_data="edit_post")],
                [InlineKeyboardButton('ℹ️ Help', callback_data='help'), InlineKeyboardButton('💌 About', callback_data='about')]
            ])
        )

    elif query.data == "create_post":
        await sb.set_session(query.from_user.id, {"state": "WAITING_FOR_CONTENT"})
        await query.message.reply("📤 **Send your post's content. It can be anything. (text, 🖼photo, 🎙audio, etc ...)**\n\nType `/cancel` to abort.")

    elif query.data == "edit_post":
        await sb.set_session(query.from_user.id, {"state": "WAITING_FOR_EDIT_LINK"})
        await query.message.reply("✏️ **Send the Telegram link of the channel post you want to edit.**\nExample: `https://t.me/c/1234567/89`\n\nType `/cancel` to abort.")

    elif query.data.startswith("toggle_"):
        ch_id = int(query.data.split("_")[1])
        session = await sb.get_session(query.from_user.id)
        selected = session.get("selected_channels", [])
        if ch_id in selected: selected.remove(ch_id)
        else: selected.append(ch_id)
        session["selected_channels"] = selected
        await sb.set_session(query.from_user.id, session)
        
        channels = await sb.get_connected_channels(query.from_user.id)
        await query.message.edit_reply_markup(get_channel_kb(channels, selected, session.get("post_id")))

    elif query.data == "send_to_selected":
        session = await sb.get_session(query.from_user.id)
        selected = session.get("selected_channels", [])
        if not selected:
            return await query.answer("❌ Select at least one channel!", show_alert=True)
            
        markup = parse_button_markup(session.get("draft_buttons", ""))
        success = 0
        for ch_id in selected:
            try:
                await client.copy_message(chat_id=ch_id, from_chat_id=query.from_user.id, message_id=session["draft_msg_id"], reply_markup=markup)
                success += 1
            except Exception as e: print(f"Error sending to {ch_id}: {e}")
                
        await query.message.edit_text(f"**✅ Successfully posted to {success} channels!**\n\n**Inline Post ID:** `{session.get('post_id')}`\nUse `@botusername {session.get('post_id')}` anywhere!")
        await sb.set_session(query.from_user.id, None)

    elif query.data == "confirm_edit":
        session = await sb.get_session(query.from_user.id)
        markup = parse_button_markup(session.get("draft_buttons", ""))
        draft_msg = await client.get_messages(query.from_user.id, session["draft_msg_id"])
        
        try:
            await edit_channel_message(client, session["edit_ch_id"], session["edit_msg_id"], draft_msg, markup)
            await query.message.edit_text(f"**✅ Message successfully Edited in Channel!**\n\n**New Inline Post ID:** `{session.get('post_id')}`")
        except Exception as e:
            await query.message.edit_text(f"**❌ Failed to edit message:** `{e}`")
        await sb.set_session(query.from_user.id, None)

    elif query.data == "cancel":
        await sb.set_session(query.from_user.id, None)
        await query.message.edit_text("**🗑 Action Cancelled & Draft Deleted.**")
        
    elif query.data in ["help", "about", "close"]:
        # Aapka purana code yaha rahega
        if query.data == "close": await query.message.delete()
        elif query.data == "about": await query.message.edit_caption(text.ABOUT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ ʙᴀᴄᴋ", callback_data="start")]]))
        elif query.data == "help": await query.message.edit_caption(text.HELP, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ ʙᴀᴄᴋ", callback_data="start")]]))
