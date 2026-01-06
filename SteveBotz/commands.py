import random
from pyrogram import Client, filters, enums
from pyrogram.errors import *
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import PICS, BOT_USERNAME, LOG_CHANNEL, SUPPORT, API_ID, API_HASH, NEW_REQ_MODE
import asyncio
from Script import text
from .database import sb

@Client.on_message(filters.command("start"))
async def start_cmd(client, message):           
    await message.reply_photo(
        photo=random.choice(PICS),
        caption=text.START.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⇆', url=f"https://telegram.me/{BOT_USERNAME}?startgroup=true&admin=invite_users")],
            [InlineKeyboardButton('ℹ️ ʜᴇʟᴘ', callback_data='help'),
             InlineKeyboardButton('💌 ᴀʙᴏᴜᴛ', callback_data='about')],
            [InlineKeyboardButton('⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⇆', url=f"https://telegram.me/{BOT_USERNAME}?startchannel=true&admin=invite_users")]
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
    sb = await message.reply(text.HELP.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🪷 𝘚𝘶𝘱𝘱𝘰𝘳𝘵 𝘎𝘳𝘰𝘶𝘱", url=SUPPORT)]]))
    await asyncio.sleep(300)
    await sb.delete()
    try:
        await message.delete()
    except:
        pass

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):        
    show = await message.reply("**Please Wait.....**")
    user_data = await sb.get_session(message.from_user.id)
    if user_data is None:
        return await show.edit("**To accept join requests, please /login first.**")
    try:
        acc = Client("joinrequest", session_string=user_data, api_id=API_ID, api_hash=API_HASH)
        await acc.connect()
    except:
        return await show.edit("**Your login session has expired. Use /logout first, then /login again.**")
    await show.edit("**Forward a message from your Channel or Group (with forward tag).\n\nMake sure your logged-in account is an admin there with full rights.**")
    fwd_msg = await client.listen(message.chat.id)
    if fwd_msg.forward_from_chat and fwd_msg.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = fwd_msg.forward_from_chat.id
        try:
            info = await acc.get_chat(chat_id)
        except:
            return await show.edit("**Error: Ensure your account is admin in this Channel/Group with required rights.**")
    else:
        return await message.reply("**Message not forwarded from a valid Channel/Group.**")
    await fwd_msg.delete()
    msg = await show.edit("**Accepting all join requests... Please wait.**")
    try:
        while True:
            await acc.approve_all_chat_join_requests(chat_id)
            await asyncio.sleep(1)
            join_requests = [req async for req in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**✅ Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** `{str(e)}`")

@Client.on_chat_join_request()
async def approve_new(client, m):
    if not NEW_REQ_MODE:
        return
    try:
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        try:
            await client.send_message(
                m.from_user.id,
                f"**Hello {m.from_user.mention} 🙋🏻‍♂️ Wassup,\n\n𝖸𝗈𝗎𝗋 𝖱𝖾𝗊𝗎𝗌𝗍 𝖳𝗈 𝖩𝗈𝗂𝗇 {m.chat.title} 𝖧𝖺𝗌 𝖡𝖾𝖾𝗇 𝖠𝖼𝖼𝖾𝗉𝗍𝖾𝖽.**"
            )
        except:
            pass
    except Exception as e:
        print(str(e))
        pass

