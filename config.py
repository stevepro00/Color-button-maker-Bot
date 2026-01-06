import os
from typing import List

API_ID = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN = int(os.environ.get("ADMIN", "6317211079"))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "https://t.me/AmaniContactBot")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "SteveApproverBot")

UPDATE = os.environ.get("UPDATE", "https://t.me/SteveBotz")
SUPPORT = os.environ.get("SUPPORT", "https://t.me/SteveBotzSupport")
PICS = (os.environ.get("PICS", "https://i.ibb.co/21JT4yQg/photo.jpg https://i.ibb.co/k2tw1zk0/photo.jpg https://i.ibb.co/w5XNzB5/photo.jpg https://i.ibb.co/VYxrsy6m/photo.jpg https://i.ibb.co/zhVCT7Sr/photo.jpg https://i.ibb.co/nNrMxHTK/photo.jpg https://i.ibb.co/dJgNpgPC/photo.jpg https://i.ibb.co/8LkZPyhD/photo.jpg https://i.ibb.co/prZ9pHSy/photo.jpg https://i.ibb.co/PG2QHRN4/photo.jpg https://i.ibb.co/gM6zNgs5/photo.jpg")).split()
FSUB_PIC = os.environ.get("FSUB_PIC", "https://i.ibb.co/hJzKT4fv/photo.jpg")
SUCCESS_PIC = os.environ.get("SUCCESS_PIC", "https://i.ibb.co/C3DWKpxV/photo.jpg")

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002421781174"))
NEW_REQ_MODE = os.environ.get("NEW_REQ_MODE", "True").lower() == "true"
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "Cluster0")
IS_FSUB = os.environ.get("IS_FSUB", "True").lower() == "true"  # Set "True" For Enable Force Subscribe
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNEL", "-1002553442366").split())) # Add Multiple channel ids
AUTH_REQ_CHANNELS = list(map(int, os.environ.get("AUTH_REQ_CHANNEL", "").split())) # Add Multiple channel ids
FSUB_EXPIRE = int(os.environ.get("FSUB_EXPIRE", 2))  # minutes, 0 = no expiry
