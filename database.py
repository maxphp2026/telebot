from supabase import create_client
from config import *

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== USER FUNCTIONS =====
def get_user(user_id):
    try:
        res = supabase.table("users").select("*").eq("user_id", user_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"get_user error: {e}")
        return None

def create_user(user_id, username, full_name, referred_by=None):
    try:
        if get_user(user_id):
            return
        data = {
            "user_id": user_id,
            "username": username or "",
            "full_name": full_name or "",
            "credits": REGISTER_CREDITS,
            "registered": True,
            "is_banned": False
        }
        if referred_by:
            data["referred_by"] = referred_by
        supabase.table("users").insert(data).execute()
    except Exception as e:
        print(f"create_user error: {e}")

def add_credits(user_id, amount):
    try:
        user = get_user(user_id)
        if user:
            supabase.table("users").update({"credits": user["credits"] + amount}).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"add_credits error: {e}")

def deduct_credits(user_id, amount):
    try:
        user = get_user(user_id)
        if user:
            supabase.table("users").update({"credits": max(0, user["credits"] - amount)}).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"deduct_credits error: {e}")

def get_user_keys(user_id):
    try:
        res = supabase.table("keys").select("*").eq("user_id", user_id).order("id", desc=True).limit(50).execute()
        return res.data or []
    except:
        return []

def get_user_key_stats(user_id):
    """User ၏ key type အလိုက် အရေအတွက် ပြန်ပေး"""
    try:
        keys = get_user_keys(user_id)
        stats = {"Outline": 0, "V2RAY": 0, "EHI": 0}
        for k in keys:
            kt = k.get("key_type", "")
            if kt in stats:
                stats[kt] += 1
        return stats, len(keys)
    except:
        return {"Outline": 0, "V2RAY": 0, "EHI": 0}, 0

def save_key(user_id, key_type, key_value):
    try:
        supabase.table("keys").insert({
            "user_id": user_id,
            "key_type": key_type,
            "key_value": key_value
        }).execute()
    except Exception as e:
        print(f"save_key error: {e}")

# ===== BAN FUNCTIONS =====
def ban_user(user_id):
    try:
        supabase.table("users").update({"is_banned": True}).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"ban_user error: {e}")
        return False

def unban_user(user_id):
    try:
        supabase.table("users").update({"is_banned": False}).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"unban_user error: {e}")
        return False

def is_banned(user_id):
    try:
        user = get_user(user_id)
        return user.get("is_banned", False) if user else False
    except:
        return False

# ===== KEY POOL =====
def get_outline_key():
    try:
        res = supabase.table("outline_pool").select("*").eq("is_used", False).limit(1).execute()
        if res.data:
            doc = res.data[0]
            supabase.table("outline_pool").update({"is_used": True}).eq("id", doc["id"]).execute()
            return doc["key_value"]
        return None
    except Exception as e:
        print(f"get_outline_key error: {e}")
        return None

def get_v2ray_key():
    try:
        res = supabase.table("v2ray_pool").select("*").eq("is_used", False).limit(1).execute()
        if res.data:
            doc = res.data[0]
            supabase.table("v2ray_pool").update({"is_used": True}).eq("id", doc["id"]).execute()
            return doc["key_value"]
        return None
    except Exception as e:
        print(f"get_v2ray_key error: {e}")
        return None

def get_ehi_key():
    try:
        res = supabase.table("ehi_pool").select("*").eq("is_used", False).limit(1).execute()
        if res.data:
            doc = res.data[0]
            supabase.table("ehi_pool").update({"is_used": True}).eq("id", doc["id"]).execute()
            return doc["key_value"]
        return None
    except Exception as e:
        print(f"get_ehi_key error: {e}")
        return None

def add_outline_key(key_value):
    try:
        supabase.table("outline_pool").insert({"key_value": key_value.strip(), "is_used": False}).execute()
        return True
    except Exception as e:
        print(f"add_outline_key error: {e}")
        return False

def add_v2ray_key(key_value):
    try:
        supabase.table("v2ray_pool").insert({"key_value": key_value.strip(), "is_used": False}).execute()
        return True
    except Exception as e:
        print(f"add_v2ray_key error: {e}")
        return False

def add_ehi_key(key_value):
    try:
        supabase.table("ehi_pool").insert({"key_value": key_value.strip(), "is_used": False}).execute()
        return True
    except Exception as e:
        print(f"add_ehi_key error: {e}")
        return False

def count_keys():
    try:
        outline = supabase.table("outline_pool").select("id", count="exact").eq("is_used", False).execute()
        v2ray = supabase.table("v2ray_pool").select("id", count="exact").eq("is_used", False).execute()
        ehi = supabase.table("ehi_pool").select("id", count="exact").eq("is_used", False).execute()
        return outline.count or 0, v2ray.count or 0, ehi.count or 0
    except Exception as e:
        print(f"count_keys error: {e}")
        return 0, 0, 0

def count_users():
    try:
        res = supabase.table("users").select("user_id", count="exact").execute()
        return res.count or 0
    except:
        return 0

def get_all_users():
    try:
        res = supabase.table("users").select("user_id").limit(500).execute()
        return res.data or []
    except:
        return []

def count_total_keys_issued():
    """Total keys user တွေ ထုတ်ထားသမျှ"""
    try:
        outline = supabase.table("keys").select("id", count="exact").eq("key_type", "Outline").execute()
        v2ray = supabase.table("keys").select("id", count="exact").eq("key_type", "V2RAY").execute()
        ehi = supabase.table("keys").select("id", count="exact").eq("key_type", "EHI").execute()
        return outline.count or 0, v2ray.count or 0, ehi.count or 0
    except:
        return 0, 0, 0

# ===== CREDIT REQUESTS =====
def create_credit_request(user_id, amount):
    try:
        supabase.table("credit_requests").insert({
            "user_id": user_id,
            "amount": amount,
            "status": "pending"
        }).execute()
    except Exception as e:
        print(f"create_credit_request error: {e}")

def has_pending_request(user_id):
    try:
        res = supabase.table("credit_requests").select("id").eq("user_id", user_id).eq("status", "pending").execute()
        return len(res.data) > 0
    except:
        return False

def get_pending_requests():
    try:
        res = supabase.table("credit_requests").select("*").eq("status", "pending").execute()
        return res.data or []
    except:
        return []

def approve_credit_request(req_id):
    try:
        res = supabase.table("credit_requests").select("*").eq("id", req_id).execute()
        if res.data:
            req = res.data[0]
            add_credits(req["user_id"], req["amount"])
            supabase.table("credit_requests").update({"status": "approved"}).eq("id", req_id).execute()
            return req["user_id"], req["amount"]
        return None, None
    except Exception as e:
        print(f"approve error: {e}")
        return None, None

def reject_credit_request(req_id):
    try:
        supabase.table("credit_requests").update({"status": "rejected"}).eq("id", req_id).execute()
    except Exception as e:
        print(f"reject error: {e}")
