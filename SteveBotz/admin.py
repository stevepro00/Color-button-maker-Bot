from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, InputUserDeactivated
from config import ADMIN
from .database import sb
from collections import defaultdict
import re, os, sys, asyncio

def parse_button_markup(text: str):
    if not text: return None
    lines = text.split("\n")
    buttons = []
    button_pattern = re.compile(r"\[(.+?)\]\((.+?)\)")
    
    style_map = {
        "danger": enums.ButtonStyle.DANGER, "red": enums.ButtonStyle.DANGER,
        "success": enums.ButtonStyle.SUCCESS, "green": enums.ButtonStyle.SUCCESS,
        "primary": enums.ButtonStyle.PRIMARY, "blue": enums.ButtonStyle.PRIMARY,
        "default": enums.ButtonStyle.DEFAULT
    }

    for line in lines:
        if not line.strip(): continue
        parts = line.split("|") # Separating buttons by |
        row = []
        for part in parts:
            match = button_pattern.search(part.strip())
            if match:
                btn_text = match.group(1).strip()
                btn_data_raw = match.group(2).strip()
                style = enums.ButtonStyle.DEFAULT
                
                # Handling :color format
                if ":" in btn_data_raw:
                    btn_data, style_str = btn_data_raw.rsplit(":", 1)
                    btn_data = btn_data.strip()
                    style = style_map.get(style_str.strip().lower(), enums.ButtonStyle.DEFAULT)
                else:
                    btn_data = btn_data_raw.strip()
                    
                if btn_data.startswith(("http://", "https://", "t.me/")):
                    row.append(InlineKeyboardButton(btn_text, url=btn_data, style=style))
                else:
                    row.append(InlineKeyboardButton(btn_text, callback_data=btn_data, style=style))
        if row:
            buttons.append(row)
            
    return InlineKeyboardMarkup(buttons) if buttons else None

# Broadcast aur stats commands same as before...
@Client.on_message(filters.command("stats") & filters.private & filters.user(ADMIN))
async def total_users(client: Client, message: Message):
    try:
        users = await sb.get_all_users()
        await message.reply_text(f"👥 **Total Users:** {len(users)}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎭 𝖢𝗅𝗈𝗌𝖾", callback_data="close")]]))
    except Exception as e:
        r=await message.reply(f"❌ *Error:* `{str(e)}`")
        await asyncio.sleep(30)
        await r.delete()

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(ADMIN))
async def broadcasting_func(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to broadcast.</b>")
    msg = await message.reply_text("📢 Starting broadcast...")
    to_copy_msg = message.reply_to_message
    users_list = await sb.get_all_users()
    total_before = len(users_list)
    completed_users = set()
    failed = 0
    
    # Isme buttons text se extract kiye jaate hain broadcast ke liye
    text_content = to_copy_msg.caption or to_copy_msg.text or ""
    reply_markup = parse_button_markup(text_content)

    for i, user in enumerate(users_list, start=1):
        user_id = user.get("user_id")
        if not user_id: continue
        try:
            user_id = int(user_id)
            await to_copy_msg.copy(user_id, reply_markup=reply_markup)
            completed_users.add(user_id)
        except (UserIsBlocked, PeerIdInvalid, InputUserDeactivated):
            await sb.delete_user(user_id)
            failed += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await to_copy_msg.copy(user_id, reply_markup=reply_markup)
            completed_users.add(user_id)
        except Exception:
            await sb.delete_user(user_id)
            failed += 1
            
        if i % 20 == 0 or i == total_before:
            try:
                await msg.edit(f"😶‍🌫 Broadcasting...\n\n👥 Total: {total_before}\n✅ Success: `{len(completed_users)}`\n❌ Failed: `{failed}`\n⚙️ Progress: {i}/{total_before}")
            except Exception: pass
        await asyncio.sleep(0.05)

    await msg.edit(f"🎯 **Broadcast Completed**\n\n👥 Total Users: `{total_before}`\n✅ Successful: `{len(completed_users)}`\n❌ Failed: `{failed}`")

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("restart"))
async def restart_bot(_, message: Message):
    steve = await message.reply_text("**🔄 Restarting bot...**")
    await asyncio.sleep(3)
    await steve.edit("**✅ Bot restarted successfully**")
    os.execl(sys.executable, sys.executable, *sys.argv)
