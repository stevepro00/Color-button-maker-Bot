import os
from typing import List

API_ID = os.environ.get("API_ID", "24916176")
API_HASH = os.environ.get("API_HASH", "15e8847a5d612831b6a42c5f8d846a8a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8281045976:AAFJ6_03YyU_oY0o5BxY8MjE9Jwy_NwoOCQ")
ADMIN = int(os.environ.get("ADMIN", "6317211079"))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "https://t.me/AmaniContactBot")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "SteveApproverBot")

UPDATE = os.environ.get("UPDATE", "https://t.me/SteveBotz")
SUPPORT = os.environ.get("SUPPORT", "https://t.me/SteveBotzSupport")

PICS = (os.environ.get("PICS", "https://i.ibb.co/MDssddJp/pic.jpg https://i.ibb.co/n8fQ2xcx/pic.jpg https://i.ibb.co/LDxwffYv/pic.jpg https://i.ibb.co/m5BN0XPD/pic.jpg")).split()
FSUB_PIC = os.environ.get("FSUB_PIC", "https://i.ibb.co/rGgLzw3b/photo.jpg")

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002421781174"))
NEW_REQ_MODE = os.environ.get("NEW_REQ_MODE", "True").lower() == "true"
DB_URI = os.environ.get("DB_URI", "mongodb+srv://lesalov501:ILnYPvfZ6dEYIIXV@cluster0.xxm59rc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "Cluster0")
IS_FSUB = os.environ.get("IS_FSUB", "True").lower() == "true"  # Set "True" For Enable Force Subscribe
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNEL", "-1002553442366").split())) # Add Multiple channel ids
AUTH_REQ_CHANNELS = list(map(int, os.environ.get("AUTH_REQ_CHANNEL", "-1003651824778").split())) # Add Multiple channel ids
FSUB_EXPIRE = int(os.environ.get("FSUB_EXPIRE", 2))  # minutes, 0 = no expiry
