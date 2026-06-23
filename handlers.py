from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from config import *
from database import *

class AdminState(StatesGroup):
    add_outline = State()
    add_v2ray = State()
    add_ehi = State()
    delete_key = State()
    add_credits_uid = State()
    add_credits_amt = State()
    deduct_credits_uid = State()
    deduct_credits_amt = State()
    ban_uid = State()
    unban_uid = State()
    view_user_uid = State()
    broadcast = State()

# ===== KEYBOARDS =====
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 User Info", callback_data="user_info"),
            InlineKeyboardButton(text="🔑 Generate Key", callback_data="generate_key")
        ],
        [
            InlineKeyboardButton(text="📋 My Keys", callback_data="my_keys"),
            InlineKeyboardButton(text="🖥 Server Status", callback_data="server_status")
        ],
        [
            InlineKeyboardButton(text="🔗 Refer", callback_data="refer"),
            InlineKeyboardButton(text="💰 Buy Credits", callback_data="buy_credits")
        ],
        [InlineKeyboardButton(text="📢 Channel", url=CHANNEL_URL)]
    ])

def key_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔵 Outline ({OUTLINE_KEY_COST} Credits)", callback_data="gen_outline")],
        [InlineKeyboardButton(text=f"🟣 V2RAY ({V2RAY_KEY_COST} Credits)", callback_data="gen_v2ray")],
        [InlineKeyboardButton(text=f"📡 HTTP Injector ({EHI_KEY_COST} Credits)", callback_data="gen_ehi")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_main")]
    ])

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Outline Keys", callback_data="admin_add_outline"),
            InlineKeyboardButton(text="➕ V2RAY Keys", callback_data="admin_add_v2ray")
        ],
        [
            InlineKeyboardButton(text="➕ EHI Keys", callback_data="admin_add_ehi"),
            InlineKeyboardButton(text="🗑 Delete Key", callback_data="admin_delete_key")
        ],
        [
            InlineKeyboardButton(text="🔍 View User", callback_data="admin_view_user"),
            InlineKeyboardButton(text="💰 Add Credits", callback_data="admin_add_credits")
        ],
        [
            InlineKeyboardButton(text="➖ Deduct Credits", callback_data="admin_deduct_credits"),
            InlineKeyboardButton(text="🚫 Ban User", callback_data="admin_ban")
        ],
        [
            InlineKeyboardButton(text="✅ Unban User", callback_data="admin_unban"),
            InlineKeyboardButton(text="📋 Pending", callback_data="admin_pending")
        ],
        [
            InlineKeyboardButton(text="📊 Stats", callback_data="admin_stats"),
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")
        ]
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_main")]
    ])

def admin_back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Admin Panel", callback_data="admin_back")]
    ])

def join_channel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Channel Join ပါ", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Joined ပြီးပါပြီ", callback_data="check_joined")]
    ])

# ===== CHANNEL CHECK =====
async def is_member(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in ("left", "kicked")
    except TelegramBadRequest:
        return False
    except Exception as e:
        print(f"is_member error: {e}")
        return False

async def check_banned(callback_or_msg, user_id):
    if is_banned(user_id):
        if isinstance(callback_or_msg, CallbackQuery):
            await callback_or_msg.answer("🚫 သင်သည် ban ခံထားသောကြောင့် bot သုံးခွင့်မရှိပါ!", show_alert=True)
        else:
            await callback_or_msg.answer("🚫 သင်သည် ban ခံထားသောကြောင့် bot သုံးခွင့်မရှိပါ!")
        return True
    return False

# ===== START =====
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    if await check_banned(message, message.from_user.id):
        return

    joined = await is_member(message.bot, message.from_user.id)
    if not joined:
        await message.answer(
            f"📢 <b>Channel Join လိုအပ်ပါသည်</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Bot ကိုသုံးရန် channel ကို join ဦးပါ-\n"
            f"{CHANNEL_URL}\n\n"
            f"Join ပြီးရင် အောက်က ခလုပ် နှိပ်ပါ-",
            reply_markup=join_channel_kb(), parse_mode="HTML"
        )
        return

    args = message.text.split()
    user = get_user(message.from_user.id)
    if not user:
        ref_id = None
        if len(args) > 1 and args[1].startswith("ref_"):
            try:
                ref_id = int(args[1].replace("ref_", ""))
                if ref_id == message.from_user.id:
                    ref_id = None
            except:
                ref_id = None
        create_user(message.from_user.id, message.from_user.username,
                    message.from_user.full_name, ref_id)
        if ref_id:
            add_credits(ref_id, REFER_CREDITS)

    await message.answer(
        f"✨ <b>{SERVER_NAME}</b> မှ ကြိုဆိုပါသည်\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📍 Server: {SERVER_LOCATION}\n\n"
        f"ခလုပ်များကို အသုံးပြုနိုင်ပါသည်-",
        reply_markup=main_keyboard(), parse_mode="HTML"
    )

async def cb_check_joined(callback: CallbackQuery):
    joined = await is_member(callback.bot, callback.from_user.id)
    if not joined:
        await callback.answer("❌ Channel ကို Join မထားသေးပါ!", show_alert=True)
        return

    user = get_user(callback.from_user.id)
    if not user:
        create_user(callback.from_user.id, callback.from_user.username, callback.from_user.full_name)

    await callback.message.edit_text(
        f"✨ <b>{SERVER_NAME}</b> မှ ကြိုဆိုပါသည်\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📍 Server: {SERVER_LOCATION}\n\n"
        f"ခလုပ်များကို အသုံးပြုနိုင်ပါသည်-",
        reply_markup=main_keyboard(), parse_mode="HTML"
    )

async def cb_back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if await check_banned(callback, callback.from_user.id):
        return
    joined = await is_member(callback.bot, callback.from_user.id)
    if not joined:
        await callback.message.edit_text(
            f"📢 <b>Channel Join လိုအပ်ပါသည်</b>\n━━━━━━━━━━━━━━━━\n{CHANNEL_URL}",
            reply_markup=join_channel_kb(), parse_mode="HTML"
        )
        return
    await callback.message.edit_text(
        f"✨ <b>{SERVER_NAME}</b> မှ ကြိုဆိုပါသည်\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"ခလုပ်များကို အသုံးပြုနိုင်ပါသည်-",
        reply_markup=main_keyboard(), parse_mode="HTML"
    )

# ===== USER INFO =====
async def cb_user_info(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Bot ကို /start နှိပ်ပါ!", show_alert=True)
        return
    stats, total = get_user_key_stats(callback.from_user.id)
    await callback.message.edit_text(
        f"👤 <b>User Information</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🆔 Chat ID: <code>{callback.from_user.id}</code>\n"
        f"👤 Name: {user['full_name']}\n"
        f"📛 Username: @{user['username'] or 'none'}\n"
        f"💰 Credits: <b>{user['credits']}</b>\n\n"
        f"🔑 <b>Keys ထုတ်ထားသမျှ: {total}</b>\n"
        f"🔵 Outline: {stats['Outline']}\n"
        f"🟣 V2RAY: {stats['V2RAY']}\n"
        f"📡 HTTP Injector: {stats['EHI']}",
        reply_markup=back_kb(), parse_mode="HTML"
    )

# ===== REFER =====
async def cb_refer(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{callback.from_user.id}"
    await callback.message.edit_text(
        f"🔗 <b>Referral System</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"မိတ်ဆွေများ invite လုပ်ပြီး Credits ရယူပါ!\n\n"
        f"🎁 Per invite: <b>{REFER_CREDITS} Credits</b>\n\n"
        f"🔗 သင်၏ Link:\n<code>{ref_link}</code>",
        reply_markup=back_kb(), parse_mode="HTML"
    )

# ===== GENERATE KEY =====
async def cb_generate_key(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Bot ကို /start နှိပ်ပါ!", show_alert=True)
        return
    await callback.message.edit_text(
        f"🔑 <b>Generate VPN Key</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 Credits: <b>{user['credits']}</b>\n\n"
        f"Key အမျိုးအစား ရွေးပါ-",
        reply_markup=key_type_keyboard(), parse_mode="HTML"
    )

async def cb_gen_outline(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Bot ကို /start နှိပ်ပါ!", show_alert=True)
        return
    if user["credits"] < OUTLINE_KEY_COST:
        await callback.answer(f"Credits မလုံလောက်! {OUTLINE_KEY_COST} Credits လိုသည်", show_alert=True)
        return
    key = get_outline_key()
    if not key:
        await callback.answer("Outline Keys ကုန်သွားပြီ! Admin ထံဆက်သွယ်ပါ", show_alert=True)
        return
    deduct_credits(callback.from_user.id, OUTLINE_KEY_COST)
    save_key(callback.from_user.id, "Outline", key)
    await callback.message.edit_text(
        f"✅ <b>Outline Key ရရှိပြီ!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🔵 Type: Outline VPN\n"
        f"💰 Credits ကျန်: <b>{user['credits'] - OUTLINE_KEY_COST}</b>\n\n"
        f"🔑 Key:\n<code>{key}</code>",
        reply_markup=back_kb(), parse_mode="HTML"
    )

async def cb_gen_v2ray(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Bot ကို /start နှိပ်ပါ!", show_alert=True)
        return
    if user["credits"] < V2RAY_KEY_COST:
        await callback.answer(f"Credits မလုံလောက်! {V2RAY_KEY_COST} Credits လိုသည်", show_alert=True)
        return
    key = get_v2ray_key()
    if not key:
        await callback.answer("V2RAY Keys ကုန်သွားပြီ! Admin ထံဆက်သွယ်ပါ", show_alert=True)
        return
    deduct_credits(callback.from_user.id, V2RAY_KEY_COST)
    save_key(callback.from_user.id, "V2RAY", key)
    await callback.message.edit_text(
        f"✅ <b>V2RAY Key ရရှိပြီ!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🟣 Type: V2RAY VPN\n"
        f"💰 Credits ကျန်: <b>{user['credits'] - V2RAY_KEY_COST}</b>\n\n"
        f"🔑 Key:\n<code>{key}</code>",
        reply_markup=back_kb(), parse_mode="HTML"
    )

async def cb_gen_ehi(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Bot ကို /start နှိပ်ပါ!", show_alert=True)
        return
    if user["credits"] < EHI_KEY_COST:
        await callback.answer(f"Credits မလုံလောက်! {EHI_KEY_COST} Credits လိုသည်", show_alert=True)
        return
    key = get_ehi_key()
    if not key:
        await callback.answer("HTTP Injector Keys ကုန်သွားပြီ! Admin ထံဆက်သွယ်ပါ", show_alert=True)
        return
    deduct_credits(callback.from_user.id, EHI_KEY_COST)
    save_key(callback.from_user.id, "EHI", key)
    await callback.message.edit_text(
        f"✅ <b>HTTP Injector Key ရရှိပြီ!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📡 Type: HTTP Injector\n"
        f"💰 Credits ကျန်: <b>{user['credits'] - EHI_KEY_COST}</b>\n\n"
        f"🔑 Cloud Key:\n<code>{key}</code>",
        reply_markup=back_kb(), parse_mode="HTML"
    )

# ===== MY KEYS =====
async def cb_my_keys(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    keys = get_user_keys(callback.from_user.id)
    if not keys:
        text = "📋 <b>My Keys</b>\n\nKey မရှိသေးပါ!"
    else:
        lines = [f"📋 <b>My Keys ({len(keys)} ခု)</b>\n━━━━━━━━━━━━━━━━"]
        for i, k in enumerate(keys[:10], 1):
            if k["key_type"] == "Outline":
                icon = "🔵"
            elif k["key_type"] == "V2RAY":
                icon = "🟣"
            else:
                icon = "📡"
            lines.append(f"{i}. {icon} {k['key_type']}\n<code>{k['key_value']}</code>\n")
        text = "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=back_kb(), parse_mode="HTML")

# ===== SERVER STATUS =====
async def cb_server_status(callback: CallbackQuery):
    outline_count, v2ray_count, ehi_count = count_keys()
    await callback.message.edit_text(
        f"🖥 <b>Server Status</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🌐 {SERVER_NAME}\n"
        f"📍 Location: {SERVER_LOCATION}\n"
        f"🟢 Status: Online\n\n"
        f"🔑 <b>Available Keys</b>\n"
        f"🔵 Outline: <b>{outline_count}</b>\n"
        f"🟣 V2RAY: <b>{v2ray_count}</b>\n"
        f"📡 HTTP Injector: <b>{ehi_count}</b>",
        reply_markup=back_kb(), parse_mode="HTML"
    )

# ===== BUY CREDITS (Threshold + Request only) =====
async def cb_buy_credits(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Bot ကို /start နှိပ်ပါ!", show_alert=True)
        return

    if user["credits"] >= BUY_CREDITS_THRESHOLD:
        await callback.answer(
            f"Credits {BUY_CREDITS_THRESHOLD} အောက်ကျမှ Buy Credits အသုံးပြုနိုင်ပါသည်!\n"
            f"လက်ရှိ Credits: {user['credits']}",
            show_alert=True
        )
        return

    if has_pending_request(callback.from_user.id):
        await callback.answer("သင့်တောင်းဆိုချက် Admin approve လုပ်ရန် စောင့်ဆိုင်းဆဲဖြစ်သည်!", show_alert=True)
        return

    await callback.message.edit_text(
        f"💰 <b>Buy Credits</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💳 Amount: <b>{BUY_CREDITS_FIXED} Credits</b>\n"
        f"💰 Your Credits: <b>{user['credits']}</b>\n\n"
        f"Request တင်လိုပါက အောက်ကနှိပ်ပါ-",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"✅ Request {BUY_CREDITS_FIXED} Credits", callback_data="confirm_buy")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="back_main")]
        ])
    )

async def cb_confirm_buy(callback: CallbackQuery):
    if await check_banned(callback, callback.from_user.id):
        return
    if has_pending_request(callback.from_user.id):
        await callback.answer("သင့်တောင်းဆိုချက် Admin approve လုပ်ရန် စောင့်ဆိုင်းဆဲဖြစ်သည်!", show_alert=True)
        return

    create_credit_request(callback.from_user.id, BUY_CREDITS_FIXED)
    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"💰 <b>Credit Request</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"👤 {callback.from_user.full_name}\n"
                f"🆔 <code>{callback.from_user.id}</code>\n"
                f"💰 Amount: <b>{BUY_CREDITS_FIXED} Credits</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="✅ Approve", callback_data=f"apv_{callback.from_user.id}_{BUY_CREDITS_FIXED}"),
                    InlineKeyboardButton(text="❌ Reject", callback_data=f"rej_{callback.from_user.id}")
                ]])
            )
        except:
            pass
    await callback.message.edit_text(
        f"✅ Request တင်ပြီ!\n💰 {BUY_CREDITS_FIXED} Credits တောင်းဆိုထားသည်\nAdmin approve ပြီးသည်နှင့် ရောက်မည်",
        reply_markup=main_keyboard(), parse_mode="HTML"
    )

# ===== ADMIN =====
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("👑 <b>Admin Panel</b>\n━━━━━━━━━━━━━━━━",
                         reply_markup=admin_keyboard(), parse_mode="HTML")

async def cb_admin_back(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    await callback.message.edit_text("👑 <b>Admin Panel</b>",
                                     reply_markup=admin_keyboard(), parse_mode="HTML")

# --- Key adding ---
async def cb_admin_add_outline(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "➕ <b>Outline Keys ထည့်မည်</b>\n\nKey တစ်ကြောင်းချင်း ရိုက်ပါ\nပြီးလျှင် /done",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.add_outline)
    await state.update_data(keys=[])

async def cb_admin_add_v2ray(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "➕ <b>V2RAY Keys ထည့်မည်</b>\n\nKey တစ်ကြောင်းချင်း ရိုက်ပါ\nပြီးလျှင် /done",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.add_v2ray)
    await state.update_data(keys=[])

async def cb_admin_add_ehi(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "➕ <b>HTTP Injector Keys ထည့်မည်</b>\n\nCloud Key တစ်ကြောင်းချင်း ရိုက်ပါ\nပြီးလျှင် /done",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.add_ehi)
    await state.update_data(keys=[])

async def admin_collect_keys(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    current = await state.get_state()
    data = await state.get_data()
    keys_list = data.get("keys", [])
    if message.text.strip() == "/done":
        success = 0
        for k in keys_list:
            if current == AdminState.add_outline:
                if add_outline_key(k): success += 1
            elif current == AdminState.add_v2ray:
                if add_v2ray_key(k): success += 1
            else:
                if add_ehi_key(k): success += 1
        if current == AdminState.add_outline:
            key_type = "Outline"
        elif current == AdminState.add_v2ray:
            key_type = "V2RAY"
        else:
            key_type = "HTTP Injector"
        await message.answer(
            f"✅ <b>{key_type} Keys ထည့်ပြီ!</b>\n\n✅ Success: {success} ခု\n❌ Failed: {len(keys_list)-success} ခု",
            reply_markup=admin_keyboard(), parse_mode="HTML"
        )
        await state.clear()
    else:
        key = message.text.strip()
        if key:
            keys_list.append(key)
            await state.update_data(keys=keys_list)
            await message.answer(f"✅ {len(keys_list)} ခု - ဆက်ရိုက်ပါ သို့မဟုတ် /done")

# --- Add Credits ---
async def cb_admin_add_credits(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "💰 <b>User Credits ထည့်မည်</b>\n\nUser ၏ Chat ID ရိုက်ထည့်ပါ-",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.add_credits_uid)

async def admin_credits_uid(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("Chat ID မှန်မှန် ရိုက်ပါ!")
        return
    await state.update_data(target_uid=int(message.text.strip()))
    await message.answer("💰 Credits ပမာဏ ရိုက်ထည့်ပါ-")
    await state.set_state(AdminState.add_credits_amt)

async def admin_credits_amt(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not message.text.strip().isdigit():
        await message.answer("ကိန်းဂဏန်းသာ ရိုက်ပါ!")
        return
    data = await state.get_data()
    uid = data["target_uid"]
    amount = int(message.text.strip())
    await state.clear()
    user = get_user(uid)
    if not user:
        await message.answer(f"❌ User ID {uid} မတွေ့ပါ!", reply_markup=admin_keyboard())
        return
    add_credits(uid, amount)
    await message.answer(
        f"✅ <b>Credits ထည့်ပြီ!</b>\n\n👤 {user['full_name']}\n🆔 {uid}\n💰 +{amount} Credits",
        reply_markup=admin_keyboard(), parse_mode="HTML"
    )
    try:
        await message.bot.send_message(uid,
            f"✅ <b>Credits ရောက်ပြီ!</b>\n\n💰 <b>+{amount} Credits</b>", parse_mode="HTML")
    except:
        pass

# --- Deduct Credits ---
async def cb_admin_deduct_credits(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "➖ <b>User Credits ပြန်ယူမည်</b>\n\nUser ၏ Chat ID ရိုက်ထည့်ပါ-",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.deduct_credits_uid)

async def admin_deduct_uid(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("Chat ID မှန်မှန် ရိုက်ပါ!")
        return
    await state.update_data(target_uid=int(message.text.strip()))
    await message.answer("➖ ပြန်ယူမည့် Credits ပမာဏ ရိုက်ထည့်ပါ-")
    await state.set_state(AdminState.deduct_credits_amt)

async def admin_deduct_amt(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not message.text.strip().isdigit():
        await message.answer("ကိန်းဂဏန်းသာ ရိုက်ပါ!")
        return
    data = await state.get_data()
    uid = data["target_uid"]
    amount = int(message.text.strip())
    await state.clear()
    user = get_user(uid)
    if not user:
        await message.answer(f"❌ User ID {uid} မတွေ့ပါ!", reply_markup=admin_keyboard())
        return
    deduct_credits(uid, amount)
    new_user = get_user(uid)
    await message.answer(
        f"✅ <b>Credits ပြန်ယူပြီ!</b>\n\n👤 {user['full_name']}\n🆔 {uid}\n➖ -{amount} Credits\n💰 ကျန်: {new_user['credits']}",
        reply_markup=admin_keyboard(), parse_mode="HTML"
    )
    try:
        await message.bot.send_message(uid,
            f"⚠️ <b>Credits ပြန်ယူခံရသည်!</b>\n\n➖ <b>-{amount} Credits</b>", parse_mode="HTML")
    except:
        pass

# --- View User ---
async def cb_admin_view_user(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "🔍 <b>User Details ကြည့်မည်</b>\n\nUser ၏ Chat ID ရိုက်ထည့်ပါ-",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.view_user_uid)

async def admin_view_user_uid(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("Chat ID မှန်မှန် ရိုက်ပါ!")
        return
    uid = int(message.text.strip())
    await state.clear()
    user = get_user(uid)
    if not user:
        await message.answer(f"❌ User ID {uid} မတွေ့ပါ!", reply_markup=admin_keyboard())
        return
    stats, total = get_user_key_stats(uid)
    ban_status = "🚫 Banned" if user.get("is_banned") else "✅ Active"
    await message.answer(
        f"🔍 <b>User Details</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👤 Name: {user['full_name']}\n"
        f"📛 Username: @{user['username'] or 'none'}\n"
        f"🆔 Chat ID: <code>{uid}</code>\n"
        f"💰 Credits: <b>{user['credits']}</b>\n"
        f"📌 Status: {ban_status}\n\n"
        f"🔑 <b>Keys ထုတ်ထားသမျှ: {total}</b>\n"
        f"🔵 Outline: {stats['Outline']}\n"
        f"🟣 V2RAY: {stats['V2RAY']}\n"
        f"📡 HTTP Injector: {stats['EHI']}",
        reply_markup=admin_keyboard(), parse_mode="HTML"
    )

# --- Ban / Unban ---
async def cb_admin_ban(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("🚫 <b>Ban User</b>\n\nBan လုပ်မည့် User ၏ Chat ID ရိုက်ပါ-", parse_mode="HTML")
    await state.set_state(AdminState.ban_uid)

async def admin_ban_uid(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("Chat ID မှန်မှန် ရိုက်ပါ!")
        return
    uid = int(message.text.strip())
    await state.clear()
    user = get_user(uid)
    if not user:
        await message.answer(f"❌ User ID {uid} မတွေ့ပါ!", reply_markup=admin_keyboard())
        return
    ban_user(uid)
    await message.answer(
        f"🚫 <b>Ban လုပ်ပြီ!</b>\n\n👤 {user['full_name']}\n🆔 {uid}",
        reply_markup=admin_keyboard(), parse_mode="HTML"
    )
    try:
        await message.bot.send_message(uid, "🚫 သင်သည် bot မှ ban ခံထားသည်!")
    except:
        pass

async def cb_admin_unban(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("✅ <b>Unban User</b>\n\nUnban လုပ်မည့် User ၏ Chat ID ရိုက်ပါ-", parse_mode="HTML")
    await state.set_state(AdminState.unban_uid)

async def admin_unban_uid(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("Chat ID မှန်မှန် ရိုက်ပါ!")
        return
    uid = int(message.text.strip())
    await state.clear()
    user = get_user(uid)
    if not user:
        await message.answer(f"❌ User ID {uid} မတွေ့ပါ!", reply_markup=admin_keyboard())
        return
    unban_user(uid)
    await message.answer(
        f"✅ <b>Unban လုပ်ပြီ!</b>\n\n👤 {user['full_name']}\n🆔 {uid}",
        reply_markup=admin_keyboard(), parse_mode="HTML"
    )
    try:
        await message.bot.send_message(uid, "✅ သင်သည် bot မှ unban ဖြစ်ပြီ! /start နှိပ်ပါ")
    except:
        pass

# --- Delete User-Issued Key ---
async def cb_admin_delete_key(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text(
        "🗑 <b>Key ဖျက်မည်</b>\n\nဖျက်လိုသော Key ကို အပြည့်အစုံ paste လုပ်ပါ-\n"
        "(User ထံ ထွက်သွားပြီးသော key အတိအကျ ဖြစ်ရမည်)",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.delete_key)

async def admin_delete_key_text(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    key_text = message.text.strip()
    success, record = delete_user_key_by_text(key_text)
    if success:
        icon = "🔵" if record["key_type"] == "Outline" else ("🟣" if record["key_type"] == "V2RAY" else "📡")
        await message.answer(
            f"✅ <b>Key ဖျက်ပြီ!</b>\n\n"
            f"{icon} Type: {record['key_type']}\n"
            f"👤 User ID: <code>{record['user_id']}</code>",
            reply_markup=admin_keyboard(), parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ ဒီ Key ကို database မှာ မတွေ့ပါ! Key text အတိအကျ ပြန်စစ်ပါ။",
            reply_markup=admin_keyboard()
        )

# --- /addkey command (quick add) ---
async def cmd_addkey(message: Message):
    """Usage: /addkey outline <key>  or  /addkey v2ray <key>  or  /addkey ehi <key>"""
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "📝 <b>Usage:</b>\n"
            "<code>/addkey outline ss://xxxxx</code>\n"
            "<code>/addkey v2ray vless://xxxxx</code>\n"
            "<code>/addkey ehi xxxxx</code>",
            parse_mode="HTML"
        )
        return
    key_type = parts[1].lower()
    key_value = parts[2].strip()

    if key_type == "outline":
        ok = add_outline_key(key_value)
        label = "Outline"
    elif key_type == "v2ray":
        ok = add_v2ray_key(key_value)
        label = "V2RAY"
    elif key_type == "ehi":
        ok = add_ehi_key(key_value)
        label = "HTTP Injector"
    else:
        await message.answer("❌ Key type မှားနေသည်! outline / v2ray / ehi သုံးပါ")
        return

    if ok:
        await message.answer(f"✅ {label} Key 1 ခု ထည့်ပြီ!\n<code>{key_value}</code>", parse_mode="HTML")
    else:
        await message.answer("❌ Key ထည့်ရာတွင် error ဖြစ်သည်!")

# --- Stats ---
async def cb_admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    total = count_users()
    outline, v2ray, ehi = count_keys()
    issued_outline, issued_v2ray, issued_ehi = count_total_keys_issued()
    await callback.message.edit_text(
        f"📊 <b>Bot Statistics</b>\n━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: <b>{total}</b>\n\n"
        f"🔑 <b>Available in Pool</b>\n"
        f"🔵 Outline: <b>{outline}</b>\n"
        f"🟣 V2RAY: <b>{v2ray}</b>\n"
        f"📡 EHI: <b>{ehi}</b>\n\n"
        f"📈 <b>Total Issued to Users</b>\n"
        f"🔵 Outline: <b>{issued_outline}</b>\n"
        f"🟣 V2RAY: <b>{issued_v2ray}</b>\n"
        f"📡 EHI: <b>{issued_ehi}</b>",
        reply_markup=admin_back_kb(), parse_mode="HTML"
    )

# --- Pending ---
async def cb_admin_pending(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    requests = get_pending_requests()
    if not requests:
        await callback.answer("Pending requests မရှိပါ", show_alert=True)
        return
    for req in requests:
        await callback.message.answer(
            f"💰 <b>Credit Request</b>\n"
            f"👤 User ID: <code>{req['user_id']}</code>\n"
            f"💰 Amount: <b>{req['amount']} Credits</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="✅ Approve", callback_data=f"apv_req_{req['id']}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"rej_req_{req['id']}")
            ]])
        )

async def cb_approve_req(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    req_id = int(callback.data.replace("apv_req_", ""))
    user_id, amount = approve_credit_request(req_id)
    if user_id:
        await callback.answer(f"✅ {amount} Credits ထည့်ပြီ!")
        await callback.message.edit_reply_markup(reply_markup=None)
        try:
            await callback.bot.send_message(user_id,
                f"✅ <b>Credits ရောက်ပြီ!</b>\n\n💰 <b>{amount} Credits</b>", parse_mode="HTML")
        except:
            pass

async def cb_reject_req(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    req_id = int(callback.data.replace("rej_req_", ""))
    reject_credit_request(req_id)
    await callback.answer("❌ Rejected!")
    await callback.message.edit_reply_markup(reply_markup=None)

async def cb_approve_direct(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    parts = callback.data.split("_")
    uid = int(parts[1])
    amt = int(parts[2])
    add_credits(uid, amt)
    await callback.answer(f"✅ {amt} Credits ထည့်ပြီ!")
    await callback.message.edit_reply_markup(reply_markup=None)
    try:
        await callback.bot.send_message(uid,
            f"✅ <b>Credits ရောက်ပြီ!</b>\n\n💰 <b>{amt} Credits</b>", parse_mode="HTML")
    except:
        pass

# --- Broadcast ---
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.edit_text("📢 Broadcast message ရိုက်ထည့်ပါ:")
    await state.set_state(AdminState.broadcast)

async def admin_broadcast_msg(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    users = get_all_users()
    sent, failed = 0, 0
    for user in users:
        try:
            await message.bot.send_message(
                user["user_id"],
                f"📢 <b>Announcement</b>\n━━━━━━━━━━━━━━━━\n{message.text}",
                parse_mode="HTML"
            )
            sent += 1
        except:
            failed += 1
    await message.answer(f"✅ Broadcast ပြီ!\n✅ Sent: {sent}\n❌ Failed: {failed}",
                         reply_markup=admin_keyboard())

# ===== REGISTER HANDLERS =====
def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_admin, Command("admin"))
    dp.message.register(cmd_addkey, Command("addkey"))

    dp.callback_query.register(cb_check_joined, F.data == "check_joined")
    dp.callback_query.register(cb_back_main, F.data == "back_main")
    dp.callback_query.register(cb_user_info, F.data == "user_info")
    dp.callback_query.register(cb_refer, F.data == "refer")
    dp.callback_query.register(cb_generate_key, F.data == "generate_key")
    dp.callback_query.register(cb_gen_outline, F.data == "gen_outline")
    dp.callback_query.register(cb_gen_v2ray, F.data == "gen_v2ray")
    dp.callback_query.register(cb_gen_ehi, F.data == "gen_ehi")
    dp.callback_query.register(cb_my_keys, F.data == "my_keys")
    dp.callback_query.register(cb_server_status, F.data == "server_status")
    dp.callback_query.register(cb_buy_credits, F.data == "buy_credits")
    dp.callback_query.register(cb_confirm_buy, F.data == "confirm_buy")

    dp.message.register(admin_collect_keys, AdminState.add_outline)
    dp.message.register(admin_collect_keys, AdminState.add_v2ray)
    dp.message.register(admin_collect_keys, AdminState.add_ehi)
    dp.message.register(admin_credits_uid, AdminState.add_credits_uid)
    dp.message.register(admin_credits_amt, AdminState.add_credits_amt)
    dp.message.register(admin_deduct_uid, AdminState.deduct_credits_uid)
    dp.message.register(admin_deduct_amt, AdminState.deduct_credits_amt)
    dp.message.register(admin_ban_uid, AdminState.ban_uid)
    dp.message.register(admin_unban_uid, AdminState.unban_uid)
    dp.message.register(admin_delete_key_text, AdminState.delete_key)
    dp.message.register(admin_view_user_uid, AdminState.view_user_uid)
    dp.message.register(admin_broadcast_msg, AdminState.broadcast)

    dp.callback_query.register(cb_admin_back, F.data == "admin_back")
    dp.callback_query.register(cb_admin_stats, F.data == "admin_stats")
    dp.callback_query.register(cb_admin_add_outline, F.data == "admin_add_outline")
    dp.callback_query.register(cb_admin_add_v2ray, F.data == "admin_add_v2ray")
    dp.callback_query.register(cb_admin_add_ehi, F.data == "admin_add_ehi")
    dp.callback_query.register(cb_admin_delete_key, F.data == "admin_delete_key")
    dp.callback_query.register(cb_admin_add_credits, F.data == "admin_add_credits")
    dp.callback_query.register(cb_admin_deduct_credits, F.data == "admin_deduct_credits")
    dp.callback_query.register(cb_admin_view_user, F.data == "admin_view_user")
    dp.callback_query.register(cb_admin_ban, F.data == "admin_ban")
    dp.callback_query.register(cb_admin_unban, F.data == "admin_unban")
    dp.callback_query.register(cb_admin_pending, F.data == "admin_pending")
    dp.callback_query.register(cb_admin_broadcast, F.data == "admin_broadcast")
    dp.callback_query.register(cb_approve_req, F.data.startswith("apv_req_"))
    dp.callback_query.register(cb_reject_req, F.data.startswith("rej_req_"))
    dp.callback_query.register(cb_approve_direct, F.data.startswith("apv_"))
