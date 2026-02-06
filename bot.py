import asyncio
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8207638006:AAF4LmPUl3n4uB3kcw2BbFQQrshIWylMYY0"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_video_info(url):
    ydl_opts = {'format': 'best', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        size = info.get('filesize') or info.get('filesize_approx') or 0
        return info, size

def download_video(url):
    ydl_opts = {
        'format': 'best[height<=480][ext=mp4]/best',
        'outtmpl': 'video_%(id)s.mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024: return f"{bytes:.2f} {unit}"
        bytes /= 1024

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Salom! Video linkini yuboring. 🎥\nMen uni server orqali yuklab beraman!")

@dp.message()
async def handle_message(message: types.Message):
    if message.text and message.text.startswith("http"):
        status = await message.answer("Tahlil qilinmoqda... ⏳")
        try:
            loop = asyncio.get_event_loop()
            info, size = await loop.run_in_executor(None, get_video_info, message.text)
            readable_size = format_size(size)
            
            if 0 < size < 50 * 1024 * 1024:
                await status.edit_text(f"🎬 {info.get('title')[:50]}...\n📦 Hajmi: {readable_size}\n\nYuklanmoqda... 📥")
                f_path = await loop.run_in_executor(None, download_video, message.text)
                await message.answer_video(FSInputFile(f_path), caption=f"✅ {info.get('title')}")
                os.remove(f_path)
                await status.delete()
            else:
                direct_url = info.get('url')
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Videoni yuklab olish 🚀", url=direct_url)]])
                await status.edit_text(f"🎬 {info.get('title')[:50]}\n📦 Hajmi: {readable_size}\n\nHajm katta, brauzerda yuklab oling:", reply_markup=kb)
        except:
            await status.edit_text("Xatolik! Link noto'g'ri yoki sayt himoyalangan. ❌")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
