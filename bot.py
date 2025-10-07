import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import threading
import datetime
import time
import json
import os
from flask import Flask

# --- DEFAULT VALUES ---
BOT_TOKEN = "7965256274:AAFAO0hg2dU5IOwdGqAoL5HhHB9nP02zvqk"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

ADMIN_USER_ID = 6820574331
ALLOWED_GROUPS = [-1002595397242]

REQUIRED_CHANNEL = "@snnetwork7"
REQUIRED_GROUP_ID = -1002595397242

API_LINK = "https://api-by-rajput.vercel.app"
API_KEY = "@snxram"
# -----------------------

# --- Flask Web Server ---
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)
# -----------------------

GLOBAL_LIMIT = 30
REGIONS = ["IND", "BR", "US", "NA", "SAC", "SG", "RU", "ID", "TW", "VN", "TH", "ME", "PK", "CIS", "BD", "EUROPE", "EU"]
DATA_FILE = "bot_data.json"
total_likes_used = 0
last_request_time = 0
# --- NEW: Set to store user IDs ---
users = set()
# ------------------------------------

# --- HELPER FUNCTIONS ---

def now_india():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))

def make_request(url):
    global last_request_time
    time.sleep(max(0, 1 - (time.time() - last_request_time)))
    last_request_time = time.time()
    return requests.get(url)

# --- DATA MANAGEMENT ---

def load_data():
    global total_likes_used, GLOBAL_LIMIT, API_LINK, API_KEY, ALLOWED_GROUPS, users
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                total_likes_used = data.get("total_likes_used", 0)
                GLOBAL_LIMIT = data.get("global_limit", GLOBAL_LIMIT)
                API_LINK = data.get("api_link", API_LINK)
                API_KEY = data.get("api_key", API_KEY)
                ALLOWED_GROUPS = data.get("allowed_groups", ALLOWED_GROUPS)
                # --- NEW: Load users ---
                users = set(data.get("users", []))
                # -----------------------
    except Exception as e:
        print(f"⚠️ Error loading data: {e}")

def save_data():
    global total_likes_used, GLOBAL_LIMIT, API_LINK, API_KEY, ALLOWED_GROUPS, users
    try:
        with open(DATA_FILE, "w") as f:
            data_to_save = {
                "total_likes_used": total_likes_used,
                "global_limit": GLOBAL_LIMIT,
                "api_link": API_LINK,
                "api_key": API_KEY,
                "allowed_groups": ALLOWED_GROUPS,
                # --- NEW: Save users (convert set to list for JSON) ---
                "users": list(users)
                # ----------------------------------------------------
            }
            json.dump(data_to_save, f, indent=4)
    except Exception as e:
        print(f"⚠️ Error saving data: {e}")

def get_remaining_likes():
    return max(0, GLOBAL_LIMIT - total_likes_used)

# --- MEMBERSHIP CHECK ---

def is_member(user_id):
    try:
        channel_member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        group_member = bot.get_chat_member(REQUIRED_GROUP_ID, user_id)
        return channel_member.status not in ['left', 'kicked'] and group_member.status not in ['left', 'kicked']
    except Exception as e:
        print(f"🚫 Could not check membership for user {user_id}: {e}")
        return False

# --- CALLBACK HANDLER ---

@bot.callback_query_handler(func=lambda call: call.data == 'verify_join')
def handle_verification_callback(call):
    user_id = call.from_user.id
    if is_member(user_id):
        bot.answer_callback_query(call.id, "✅ Verification successful!")
        bot.edit_message_text(
            "<b>✅ Verification successful!</b>\nYou can now send your <code>/like</code> command again.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    else:
        bot.answer_callback_query(call.id, "❌ You haven't joined the channel and group yet.", show_alert=True)

# --- PUBLIC COMMANDS ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    # --- NEW: Add user to database on start ---
    user_id = message.from_user.id
    if user_id not in users:
        users.add(user_id)
        save_data()
    # ------------------------------------------
    user_name = message.from_user.first_name
    start_text = (f"🎉 WELCOME {user_name} 🎉\n"
                  "━━━✦✦━━━\n"
                  "🔥 Ready to Fire, Ready to Win 🔥\n"
                  "😎 Enjoy the Game with our BOT 🚀\n"
                  "━━━━━━━━━━━━━━━\n"
                  "<b>Command -</b>\n"
                  "<code>/like {region} {uid}</code>")
    markup = InlineKeyboardMarkup()
    bot_username = bot.get_me().username
    add_to_group_link = f"https://t.me/{bot_username}?startgroup=true"
    markup.add(InlineKeyboardButton("✨ ADD ME TO YOUR GROUP ✨", url=add_to_group_link))
    markup.add(InlineKeyboardButton("SUPPORT 📞", url="https://t.me/snnetwork7"), InlineKeyboardButton("❤️ OWNER ❤️", url="https://t.me/snxrajput"))
    bot.reply_to(message, start_text, reply_markup=markup)

@bot.message_handler(commands=["like"])
def handle_like(message):
    if not is_member(message.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("↗️ Join Channel ↗️", url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}"))
        markup.add(InlineKeyboardButton("↗️ Join Group ↗️", url="https://t.me/+zRMS7VbMQtI2ZWE1"))
        markup.add(InlineKeyboardButton("✅ Joined! Verify Now", callback_data="verify_join"))
        bot.reply_to(message, 
            "<b>🛑 Stop! To use this command, you must join our channel and group.</b>\n\n"
            "Please join both and then click the 'Verify Now' button below.", 
            reply_markup=markup)
        return

    if message.chat.id not in ALLOWED_GROUPS:
        bot.reply_to(message, "🔐 <b>This group is not approved to use the bot.\nPlease contact: @snxrajput</b>")
        return
    
    global total_likes_used
    # ...
    args = message.text.split()
    if len(args) != 3:
        # यहाँ </b> को <b> कर दिया गया है
        bot.reply_to(message, "<b>❓ Incorrect format!</b>\nCorrect usage: <code>/like &lt;region&gt; &lt;uid&gt;</code>\nExample: <code>/like IND 1234567890</code>")
        return
    region, uid = args[1].upper(), args[2]
    if region not in REGIONS:
        bot.reply_to(message, f"🗺️ Invalid region: `{region}`")
        return
    remaining = get_remaining_likes()
    if remaining <= 0:
        bot.reply_to(message, "🚫 <b>Limit reached! Please try again later.</b>")
        return
    processing_msg = bot.reply_to(message, "⏳ <b>Processing your request...</b>")
    try:
        url = f"{API_LINK}/like?uid={uid}&server_name={region}&key={API_KEY}"
        response = make_request(url)

        if response.status_code == 200:
            result = response.json()
            
            # --- 🔴 UPDATED TO HANDLE NESTED JSON 🔴 ---
            status = result.get("status")
            response_data = result.get("response", {}) # Get the nested object
            
            likes_given = response_data.get("LikesGivenByAPI", 0)

            if status == 1:
                total_likes_used += 1
                save_data()
                nickname = str(response_data.get('PlayerNickname', 'N/A')).replace('<', '&lt;').replace('>', '&gt;')
                text = (
                    "✅ <b>Likes Sent Successfully 🥳</b>\n\n"
                    f"👤 <b>Player Nickname: {nickname}</b>\n"
                    f"🆔 <b>Player UID: {uid}</b>\n"
                    # PlayerRegion is not in your new JSON, so it will show N/A
                    f"🌍 <b>Player Region: {region}</b>\n" 
                    f"📊 <b>Player Level: {response_data.get('PlayerLevel', 'N/A')}</b>\n"
                    f"❤️ <b>Before Likes: {response_data.get('LikesbeforeCommand', 'N/A')}</b>\n"
                    f"💝 <b>After Likes: {response_data.get('LikesafterCommand', 'N/A')}</b>\n"
                    f"🤖 <b>Likes Given By Bot: {likes_given}</b>"
                )
            elif status == 2:
                text = (
                    "⚠️ <b>Failed to Send Likes</b>\n"
                    "❌ <b>Success: false</b>\n"
                    "🙅🏻 <b>Message: likes_already_send</b>"
                )
            else:
                text = (
                    "⚠️ <b>Failed to Send Likes</b>\n"
                    "❌ <b>Success: false</b>\n"
                    "🙅🏻 <b>Message: player_not_found</b>"
                )
        else:
            text = f"🔌 <b>Failed to connect to the API. Please try again later.</b>"

        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Devloper 🧑🏻‍💻", url="https://t.me/snxrajput"))
        bot.edit_message_text(text, message.chat.id, processing_msg.message_id, reply_markup=markup)
    
    except Exception as e:
        error_text = f"⚙️ <b>Error:</b> {str(e).replace('<', '&lt;').replace('>', '&gt;')}"
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Devloper 🧑🏻‍💻", url="https://t.me/snxrajput"))
        bot.edit_message_text(error_text, message.chat.id, processing_msg.message_id, reply_markup=markup)

@bot.message_handler(commands=["remain"])
def handle_remain(message):
    if message.chat.id not in ALLOWED_GROUPS:
        bot.reply_to(message, "🔐 This group is not approved to use the bot.\nPlease contact: @snxrajput")
        return
    remaining = get_remaining_likes()
    bot.reply_to(message, f"📊 <b>Remaining Requests: {remaining}/{GLOBAL_LIMIT}</b>")

@bot.message_handler(commands=['getid'])
def get_chat_id(message):
    if message.from_user.id == ADMIN_USER_ID:
        bot.reply_to(message, f"🆔 This chat's ID is: `{message.chat.id}`", parse_mode="Markdown")

# --- NEW BROADCAST COMMAND (ADMIN ONLY) ---
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "🚫 <b>Access Denied! This command is for the admin only.</b>")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❓ <b>Incorrect format!</b>\nCorrect usage: <code>/broadcast &lt;message&gt;</code>")
        return

    broadcast_message = args[1]
    
    target_chats = set(ALLOWED_GROUPS).union(users)
    
    if not target_chats:
        bot.reply_to(message, "텅텅 No users or groups to broadcast to.")
        return

    success_count = 0
    fail_count = 0

    status_msg = bot.reply_to(message, f"📢 <b>Broadcast started...</b>\nSending to {len(target_chats)} chats.")
    
    for chat_id in target_chats:
        try:
            bot.send_message(chat_id, broadcast_message)
            success_count += 1
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
            fail_count += 1
        time.sleep(0.1)

    final_report = (
        f"🏁 <b>Broadcast Finished!</b>\n\n"
        f"✅ Sent successfully: {success_count}\n"
        f"❌ Failed to send: {fail_count}"
    )
    bot.edit_message_text(final_report, message.chat.id, status_msg.message_id)
# ---------------------------------------------

@bot.message_handler(commands=["setapi", "setkey", "setlimit", "approve", "disapprove", "listgroups"])
def handle_admin_commands(message):
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "🚫 <b>Access Denied! This command is for the admin only.</b>")
        return
    command, *args = message.text.split()
    usage_text = ""
    if command == "/approve" and not args: usage_text = "/approve <group_id>"
    elif command == "/disapprove" and not args: usage_text = "/disapprove <group_id>"
    elif command == "/setapi" and not args: usage_text = "/setapi <link>"
    elif command == "/setkey" and not args: usage_text = "/setkey <key>"
    elif command == "/like" and not args: usage_text = "/like <region> <uid>"
    elif command == "/setlimit" and not args: usage_text = "/setlimit <number>"
    if usage_text:
        bot.reply_to(message, f"❓ Incorrect format!\nCorrect usage: `{usage_text}`", parse_mode="Markdown")
        return
    try:
        if command == "/approve":
            group_id = int(args[0])
            if group_id in ALLOWED_GROUPS: bot.reply_to(message, "👍 This group is already approved.")
            else:
                ALLOWED_GROUPS.append(group_id)
                save_data()
                bot.reply_to(message, f"✅ Group Approved!\nID: `{group_id}`", parse_mode="Markdown")
        elif command == "/disapprove":
            group_id = int(args[0])
            if group_id in ALLOWED_GROUPS:
                ALLOWED_GROUPS.remove(group_id)
                save_data()
                bot.reply_to(message, f"❌ Group Disapproved!\nID: `{group_id}`", parse_mode="Markdown")
            else: bot.reply_to(message, "🤷‍♂️ This group is not in the approved list.")
        elif command == "/listgroups":
            if not ALLOWED_GROUPS: bot.reply_to(message, "텅텅 No groups are currently approved.")
            else:
                text = "✅ Approved Group IDs:\n" + "\n".join([f"- `{gid}`" for gid in ALLOWED_GROUPS])
                bot.reply_to(message, text, parse_mode="Markdown")
        elif command == "/setapi":
            global API_LINK; API_LINK = args[0]; save_data(); bot.reply_to(message, "✅ API Link has been updated.")
        elif command == "/setkey":
            global API_KEY; API_KEY = args[0]; save_data(); bot.reply_to(message, "✅ API Key has been updated.")
        elif command == "/setlimit":
            global GLOBAL_LIMIT; GLOBAL_LIMIT = int(args[0]); save_data(); bot.reply_to(message, f"✅ Global limit is now set to {GLOBAL_LIMIT}.")
    except (ValueError, IndexError): bot.reply_to(message, "⚙️ Invalid command format or ID.")
    except Exception as e: bot.reply_to(message, f"⚙️ An error occurred: {e}")

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def handle_unknown_commands(message):
    bot.reply_to(message, f"🤷‍♂️ Unknown command: `{message.text}`\n\nPlease use /start to see the list of valid commands.", parse_mode="Markdown")

def reset_like_counts():
    global total_likes_used
    while True:
        now = now_india()
        next_reset = (now + datetime.timedelta(days=1)).replace(hour=4, minute=0, second=0, microsecond=0)
        time.sleep((next_reset - now).total_seconds())
        total_likes_used = 0
        save_data()
        print(f"🔄 Daily like limit has been reset at {now_india()}")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    load_data()
    reset_thread = threading.Thread(target=reset_like_counts, daemon=True)
    reset_thread.start()
    print("🤖 Bot is running with Flask server...")
    bot.infinity_polling()
