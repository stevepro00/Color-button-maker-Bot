from pyrogram import Client, filters, StopPropagation
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from config import ADMIN, ADMIN_USERNAME, DB_URI, DB_NAME

class Stevebotz:
    def __init__(self):
        mongo_client = AsyncIOMotorClient(DB_URI)
        db = mongo_client[DB_NAME]
        self.banned_users = db["banned_users"]

    async def ban_user(self, user_id: int, reason: str = None) -> bool:
        try:
            await self.banned_users.update_one({"user_id": user_id}, {"$set": {"reason": reason}}, upsert=True)
            return True
        except Exception:
            return False

    async def unban_user(self, user_id: int) -> bool:
        try:
            result = await self.banned_users.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception:
            return False

    async def is_user_banned(self, user_id: int):
        return await self.banned_users.find_one({"user_id": user_id})

sb = Stevebotz()

@Client.on_message(filters.private & ~filters.user(ADMIN) & ~filters.bot & ~filters.service & ~filters.me, group=-2)
async def global_ban_checker(_, m: Message):
    if not m.from_user:
        return
    ban = await sb.is_user_banned(m.from_user.id)
    if not ban:
        return
    try:
        await m.delete()
    except:
        pass
    text = "🚫 **You are banned from using this bot.**"
    if ban.get("reason"):
        text += f"\n\n**Reason:** {ban['reason']}"
    await m.reply_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👨‍💻 OWNER 👨‍💻", url=ADMIN_USERNAME)]]))
    raise StopPropagation

@Client.on_message(filters.command("ban") & filters.private & filters.user(ADMIN))
async def ban_cmd(c: Client, m: Message):
    parts = m.text.split(maxsplit=2)
    if len(parts) < 2:
        return await m.reply("Usage: /ban user_id [reason]")
    try:
        user_id = int(parts[1])
    except:
        return await m.reply("Invalid user ID.")
    reason = parts[2] if len(parts) > 2 else None
    if await sb.ban_user(user_id, reason):
        await m.reply(f"✅ **User `{user_id}` banned.**")
        try:
            msg = "🚫 You have been banned from using the bot."
            if reason:
                msg += f"\nReason: {reason}"
            await c.send_message(user_id, msg)
        except:
            pass
    else:
        await m.reply("❌ Failed to ban user.")

@Client.on_message(filters.command("unban") & filters.private & filters.user(ADMIN))
async def unban_cmd(c: Client, m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        return await m.reply("Usage: /unban user_id")
    try:
        user_id = int(parts[1])
    except:
        return await m.reply("Invalid user ID.")
    if await sb.unban_user(user_id):
        await m.reply(f"✅ **User `{user_id}` unbanned.**")
        try:
            await c.send_message(user_id,"✅ **You have been unbanned.**\n\nYou can now use the bot again.")
        except:
            pass
    else:
        await m.reply("❌ User was not banned.")

@Client.on_message(filters.command("banned") & filters.private & filters.user(ADMIN))
async def banned_cmd(_, m: Message):
    users = await sb.banned_users.find().to_list(length=None)
    if not users:
        return await m.reply("No users are currently banned.")
    text = "🚫 **Banned Users:**\n\n"
    for u in users:
        text += f"• `{u['user_id']}` — {u.get('reason','No reason')}\n"
    await m.reply(text)
