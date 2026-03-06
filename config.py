import os

API_ID = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN = int(os.environ.get("ADMIN", "8587894416"))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "https://t.me/AmaniContactBot")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "SteveApproverBot")

UPDATE = os.environ.get("UPDATE", "https://t.me/SteveBotz")
SUPPORT = os.environ.get("SUPPORT", "https://t.me/SteveBotzSupport")
PICS = (os.environ.get("PICS", "https://i.ibb.co/21JT4yQg/photo.jpg https://i.ibb.co/k2tw1zk0/photo.jpg")).split()
FSUB_PIC = os.environ.get("FSUB_PIC", "https://i.ibb.co/hJzKT4fv/photo.jpg")
SUCCESS_PIC = os.environ.get("SUCCESS_PIC", "https://i.ibb.co/C3DWKpxV/photo.jpg")

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002421781174"))
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "Cluster0")
IS_FSUB = os.environ.get("IS_FSUB", "True").lower() == "true" 
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNEL", "-1002553442366").split()))
FSUB_EXPIRE = int(os.environ.get("FSUB_EXPIRE", 2)) 
