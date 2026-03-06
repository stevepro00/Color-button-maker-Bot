from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, InputUserDeactivated
from config import ADMIN
from .database import sb
from collections import defaultdict
import re, os, sys, asyncio

def parse_button_markup(text: str):
    lines = text.split("\n")
    buttons = []
    final_text_lines = []
    button_pattern = re.compile(r"\[(.+?)\]\((.+?)\)")
    
    style_map = {
        "danger": enums.ButtonStyle.DANGER,
        "red": enums.ButtonStyle.DANGER,
        "success": enums.ButtonStyle.SUCCESS,
        "green": enums.ButtonStyle.SUCCESS,
        "primary": enums.ButtonStyle.PRIMARY,
        "blue": enums.ButtonStyle.PRIMARY,
        "default": enums.ButtonStyle.DEFAULT
    }

    for line in lines:
        parts = line.split("||")
        row = []
        is_button_line = True
        
        for part in parts:
            match = button_pattern.fullmatch(part.strip())
            if match:
                btn_text = match.group(1).strip()
                btn_data_raw = match.group(2).strip()
                style = enums.ButtonStyle.DEFAULT
                
                if "|" in btn_data_raw:
                    btn_data, style_str = btn_data_raw.split("|", 1)
                    btn_data = btn_data.strip()
                    style = style_map.get(style_str.strip().lower(), enums.ButtonStyle.DEFAULT)
                else:
                    btn_data = btn_data_raw
                    
                if btn_data.startswith(("http://", "https://", "t.me/")):
                    row.append(InlineKeyboardButton(btn_text, url=btn_data, style=style))
                else:
                    row.append(InlineKeyboardButton(btn_text, callback_data=btn_data, style=style))
            else:
                is_button_line = False
                break
        
        if is_button_line and row:
            buttons.append(row)
        else:
            final_text_lines.append(line)
            
    return InlineKeyboardMarkup(buttons) if buttons else None, "\n".join(final_text_lines).strip()

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
    raw_text = to_copy_msg.caption or to_copy_msg.text or ""
    reply_markup, cleaned_text = parse_button_markup(raw_text)

    for i, user in enumerate(users_list, start=1):
        user_id = user.get("user_id")
        if not user_id:
            if await sb.delete_user(user.get("_id")):
                failed += 1
            continue
        try:
            user_id = int(user_id) 
            if to_copy_msg.text:
                await client.send_message(user_id, cleaned_text, reply_markup=reply_markup)
            elif to_copy_msg.photo:
                await client.send_photo(user_id, to_copy_msg.photo.file_id, caption=cleaned_text, reply_markup=reply_markup)
            elif to_copy_msg.video:
                await client.send_video(user_id, to_copy_msg.video.file_id, caption=cleaned_text, reply_markup=reply_markup)
            elif to_copy_msg.document:
                await client.send_document(user_id, to_copy_msg.document.file_id, caption=cleaned_text, reply_markup=reply_markup)
            else:
                await to_copy_msg.copy(user_id)
            completed_users.add(user_id)
        except (UserIsBlocked, PeerIdInvalid, InputUserDeactivated):
            if await sb.delete_user(user_id):
                failed += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await to_copy_msg.copy(user_id)
                completed_users.add(user_id)
            except Exception:
                if await sb.delete_user(user_id):
                    failed += 1
        except Exception:
            if await sb.delete_user(user_id):
                failed += 1
        if i % 20 == 0 or i == total_before:
            try:
                await msg.edit(
                    f"😶‍🌫 Broadcasting...\n\n"
                    f"👥 Total Users: {total_before}\n"
                    f"✅ Successful: <code>{len(completed_users)}</code>\n"
                    f"❌ Failed/Removed: <code>{failed}</code>\n"
                    f"⚙️ Progress: {i}/{total_before}"
                )
            except Exception:
                pass
        await asyncio.sleep(0.05)

    all_users = await sb.get_all_users()
    users_by_id = defaultdict(list)
    for user in all_users:
        uid = user.get("user_id")
        if not uid:
            if await sb.delete_user(user.get("_id")):
                failed += 1
            continue
        users_by_id[uid].append(user)

    for uid, docs in users_by_id.items():
        if uid in completed_users:
            for duplicate in docs[1:]:
                if await sb.delete_user(duplicate.get("user_id")):
                    failed += 1
        else:
            for doc in docs:
                if await sb.delete_user(doc.get("user_id")):
                    failed += 1

    active_users = len(completed_users)

    await msg.edit(
        f"🎯 <b>Broadcast Completed</b>\n\n"
        f"👥 Total Users (Before): <code>{total_before}</code>\n"
        f"✅ Successful: <code>{len(completed_users)}</code>\n"
        f"❌ Failed/Removed: <code>{failed}</code>\n"
        f"📊 Active Users (Now): <code>{active_users}</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎭 Close", callback_data="close")]]),
    )

@Client.on_message(filters.private & filters.user(ADMIN) & filters.command("restart"))
async def restart_bot(_, message: Message):
    steve = await message.reply_text("**🔄 Restarting bot...**")
    await asyncio.sleep(3)
    await steve.edit("**✅ Bot restarted successfully**")
    os.execl(sys.executable, sys.executable, *sys.argv)
