import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

REGISTER_CREDITS = 1
REFER_CREDITS = 3
OUTLINE_KEY_COST = 5
V2RAY_KEY_COST = 8
EHI_KEY_COST = 8
BUY_CREDITS_FIXED = 8        # Buy credits ပုံသေ ပမာဏ
BUY_CREDITS_THRESHOLD = 8    # ဒီနံပါတ်အောက်ကျမှ Buy Credits နှိပ်လို့ရမည်

SERVER_NAME = "Lord Kazuma VPN"
SERVER_LOCATION = "Singapore"
CHANNEL_URL = "https://t.me/bug303"
CHANNEL_USERNAME = "@bug303"     # Channel join check အတွက်
