import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # 👑 Your Telegram user ID

GOFILE_API = "https://api.gofile.io/uploadFile"

# Global stats
upload_count = 0
total_size_uploaded = 0

bot = Client("gofile_uploader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G"]:
        if abs(num) < 1024.0:
            return f"{num:.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}T{suffix}"

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "👋 Welcome to **GoFile Uploader Bot**!\n\n"
        "📤 Send me any file (video/audio/document, max 4GB)\n"
        "☁️ I will upload and return a **GoFile link**.\n\n"
        "💡 /help - for how to use\n"
        "📊 /stats - admin only",
        disable_web_page_preview=True
    )

@bot.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    await message.reply(
        "📥 **Upload Instructions:**\n\n"
        "➤ Send file (max 4GB)\n"
        "➤ I will upload it to GoFile.io\n"
        "➤ You'll receive a private 🔐 download link\n\n"
        "✅ Supported: Documents, Videos, Audios\n"
        "⚡ Fast. Secure. Easy."
    )

@bot.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats(client, message: Message):
    await message.reply(
        f"📊 **Bot Stats**:\n\n"
        f"📁 Files Uploaded: `{upload_count}`\n"
        f"📦 Total Size: `{sizeof_fmt(total_size_uploaded)}`"
    )

@bot.on_message(filters.document | filters.video | filters.audio)
async def upload_file(client, message: Message):
    global upload_count, total_size_uploaded

    file = message.document or message.video or message.audio
    if file.file_size > 4 * 1024 * 1024 * 1024:
        await message.reply("❌ File is larger than 4GB limit.")
        return

    status = await message.reply("📥 Downloading your file...")
    file_path = await message.download(progress=progress_bar, progress_args=(status, "Downloading"))

    await status.edit("☁️ Uploading to GoFile...")

    with open(file_path, "rb") as f:
        response = requests.post(GOFILE_API, files={"file": (file.file_name, f)})

    os.remove(file_path)

    data = response.json()
    if data["status"] != "ok":
        await status.edit("❌ Upload failed. Try again.")
        return

    link = data["data"]["downloadPage"]
    upload_count += 1
    total_size_uploaded += file.file_size

    await status.edit(
        f"✅ **Upload Complete!**\n\n"
        f"📄 **{file.file_name}**\n"
        f"📦 Size: `{sizeof_fmt(file.file_size)}`\n\n"
        f"🔗 [Click here to download]({link})",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("📥 Open Link", url=link),
                InlineKeyboardButton("📋 Copy URL", url=link)
            ]]
        )
    )

async def progress_bar(current, total, message, stage):
    percent = int(current * 100 / total)
    filled = int(percent / 10)
    bar = "▓" * filled + "░" * (10 - filled)
    try:
        await message.edit_text(f"{stage}...\n`{sizeof_fmt(current)} / {sizeof_fmt(total)}`\n{bar} {percent}%")
    except:
        pass

bot.run()
  
