import random
import string
from typing import Any
from config import DB_URI, DB_NAME
from motor import motor_asyncio
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

client = motor_asyncio.AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]

class Stevebotz:
    def __init__(self):
        self.users = db["users"]
        self.posts = db["posts"]
        self.cache: dict[int, dict[str, Any]] = {}

    async def add_user(self, user_id: int, name: str) -> dict[str, Any] | None:
        try:
            user = {"user_id": int(user_id), "name": name}
            saved = await self.users.find_one_and_update(
                {"user_id": user["user_id"]}, {"$set": user}, upsert=True, return_document=ReturnDocument.AFTER
            )
            if saved: self.cache[user["user_id"]] = saved
            return saved
        except DuplicateKeyError:
            existing = await self.users.find_one({"user_id": int(user_id)})
            if existing: self.cache[int(user_id)] = existing
            return existing
        except Exception: return None

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        try:
            if user_id in self.cache: return self.cache[user_id]
            user = await self.users.find_one({"user_id": int(user_id)})
            if user: self.cache[user_id] = user
            return user
        except Exception: return None

    async def set_session(self, user_id: int, session: Any) -> bool:
        try:
            result = await self.users.update_one({"user_id": user_id}, {"$set": {"session": session}})
            if user_id in self.cache: self.cache[user_id]["session"] = session
            return result.modified_count > 0
        except Exception: return False

    async def get_session(self, user_id: int) -> Any | None:
        try:
            user = await self.get_user(user_id)
            return user.get("session") if user else None
        except Exception: return None

    async def get_all_users(self) -> list[dict[str, Any]]:
        users: list[dict[str, Any]] = []
        async for user in self.users.find(): users.append(user)
        return users

    async def delete_user(self, identifier: int | str | ObjectId) -> bool:
        try:
            query = {"user_id": identifier} if isinstance(identifier, int) else {"_id": ObjectId(identifier)} if isinstance(identifier, str) else {"_id": identifier}
            result = await self.users.delete_one(query)
            return result.deleted_count > 0
        except Exception: return False

    # --- NAYE MULTI-CHANNEL AUR POST FUNCTIONS ---
    async def connect_channel(self, user_id: int, channel_id: int, title: str) -> bool:
        try:
            # Save as a dictionary to prevent duplicates and keep names mapping
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {f"connected_channels.{channel_id}": title}},
                upsert=True
            )
            if user_id in self.cache:
                if "connected_channels" not in self.cache[user_id]:
                    self.cache[user_id]["connected_channels"] = {}
                self.cache[user_id]["connected_channels"][str(channel_id)] = title
            return True
        except Exception as e:
            print("Error connecting channel:", e)
            return False

    async def get_connected_channels(self, user_id: int) -> list[dict]:
        user = await self.get_user(user_id)
        channels_dict = user.get("connected_channels", {})
        return [{"id": int(k), "title": v} for k, v in channels_dict.items()]

    async def save_post(self, user_id: int, msg, buttons_str: str) -> str:
        post_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        post_data = {
            "post_id": post_id,
            "user_id": user_id,
            "buttons_str": buttons_str,
            "text": msg.text or msg.caption or "",
            "media_type": None,
            "file_id": None
        }
        if msg.photo:
            post_data["media_type"] = "photo"
            post_data["file_id"] = msg.photo.file_id
        elif msg.video:
            post_data["media_type"] = "video"
            post_data["file_id"] = msg.video.file_id
        elif msg.document:
            post_data["media_type"] = "document"
            post_data["file_id"] = msg.document.file_id
        elif msg.animation:
            post_data["media_type"] = "animation"
            post_data["file_id"] = msg.animation.file_id
        elif msg.audio:
            post_data["media_type"] = "audio"
            post_data["file_id"] = msg.audio.file_id
            
        await self.posts.insert_one(post_data)
        return post_id

    async def get_user_posts(self, user_id: int):
        cursor = self.posts.find({"user_id": user_id}).sort("_id", -1).limit(50)
        return await cursor.to_list(length=50)

sb = Stevebotz()
