import random
from pyrogram import Client, enums
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from Script import text
from config import PICS, UPDATE, SUPPORT
from .database import sb
from .admin import parse_button_markup

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    if query.data == "start":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.START.format(query.from_user.mention)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ℹ️ ʜᴇʟᴘ', callback_data='help'),
                 InlineKeyboardButton('💌 ᴀʙᴏᴜᴛ', callback_data='about')]
            ])
        )

    elif query.data == "help":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.HELP
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇs', url=UPDATE),
                 InlineKeyboardButton('💬 sᴜᴘᴘᴏʀᴛ', url=SUPPORT)],
                [InlineKeyboardButton('↩️ ʙᴀᴄᴋ', callback_data="start"),
                 InlineKeyboardButton('❌ ᴄʟᴏsᴇ', callback_data="close")]
            ])
        )

    elif query.data == "about":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.ABOUT
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("↩️ ʙᴀᴄᴋ", callback_data="start"),
                 InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")]
            ])
        )

    elif query.data == "close":
        await query.message.delete()

    # --- NAYE BUTTON MAKER CALLBACKS ---
    elif query.data == "send_channel":
        channel_id = await sb.get_connected_channel(query.from_user.id)
        if not channel_id:
            return await query.answer("❌ You haven't connected a channel yet! Use /connect -100xxx", show_alert=True)
            
        session = await sb.get_session(query.from_user.id)
        if not session or "draft" not in session:
            return await query.answer("❌ Draft expired.", show_alert=True)
            
        reply_markup, text_content = parse_button_markup(session["draft"])
        
        try:
            await client.send_message(channel_id, text_content, reply_markup=reply_markup)
            await query.message.edit_text("**✅ Successfully posted to your connected channel!**")
            await sb.set_session(query.from_user.id, None)
        except Exception as e:
            await query.message.edit_text(f"**❌ Error sending to channel:** `{e}`")

    elif query.data == "save_inline":
        session = await sb.get_session(query.from_user.id)
        if not session or "draft" not in session:
            return await query.answer("❌ Draft expired.", show_alert=True)
            
        post_id = await sb.save_post(query.from_user.id, session["draft"])
        await query.message.edit_text(
            f"**✅ Post Saved for Inline Mode!**\n\n"
            f"**Post ID:** `{post_id}`\n\n"
            f"You can now send this anywhere using:\n"
            f"`@{client.me.username} {post_id}`"
        )
        await sb.set_session(query.from_user.id, None)

    elif query.data == "cancel":
        await sb.set_session(query.from_user.id, None)
        await query.message.edit_text("**🗑 Action Cancelled & Draft Deleted.**")

    else:
        # Catch-all custom buttons ke liye
        await query.answer(f"Custom Button Clicked!\nData: {query.data}", show_alert=True)
