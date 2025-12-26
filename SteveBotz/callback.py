import random
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from Script import text
from config import ADMIN, BOT_USERNAME, PICS, UPDATE, SUPPORT, ADMIN_USERNAME

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    if query.data == "start":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.START.format(query.from_user.mention)
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⇆', url=f"https://telegram.me/{BOT_USERNAME}?startgroup=true&admin=invite_users")],
                [InlineKeyboardButton('ℹ️ ʜᴇʟᴘ', callback_data='help'),
                 InlineKeyboardButton('💌 ᴀʙᴏᴜᴛ', callback_data='about')],
                [InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⇆', url=f"https://telegram.me/{BOT_USERNAME}?startchannel=true&admin=invite_users")]
            ])
        )

    elif query.data == "help":
        await query.message.edit_media(
            InputMediaPhoto(
                media=random.choice(PICS),
                caption=text.HELP.format(query.from_user.mention)
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
