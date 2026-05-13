import asyncio
import os
import re
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    exit(1)

ADV_TEXT = "Загрузка..."

JOKE_RESPONSES = {
    "бот": ["👀"],
}

def check_for_joke(text):
    text_lower = text.lower()
    for trigger, responses in JOKE_RESPONSES.items():
        if trigger in text_lower:
            return random.choice(responses)
    return None

async def download_video(url):
    loop = asyncio.get_running_loop()
    
    def blocking_download():
        os.makedirs("downloads", exist_ok=True)
        
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            
            if not os.path.exists(video_path):
                base = os.path.splitext(video_path)[0]
                for ext in ['.mp4', '.mkv', '.webm']:
                    if os.path.exists(base + ext):
                        video_path = base + ext
                        break
            return video_path
    return await loop.run_in_executor(None, blocking_download)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    url_match = re.search(r'https?://\S+', text)
    
    if url_match:
        url = url_match.group(0)
        status_msg = await update.message.reply_text(f"📥 Идёт загрузка из TikTok...\n\n{ADV_TEXT}\n\nОжидайте.")
        
        try:
            video_path = await download_video(url)
            
            with open(video_path, 'rb') as video_file:
                await update.message.reply_video(video=video_file, caption="✅")
            
            await status_msg.delete()
            os.remove(video_path)
            return
        except Exception as e:
            await status_msg.edit_text(f"❌ Ошибка: {str(e)}")
            return
    
    joke_response = check_for_joke(text)
    if joke_response:
        await update.message.reply_text(joke_response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, Exception):
        error_str = str(context.error)
        if "TimedOut" in error_str or "timeout" in error_str.lower():
            print("⚠️ Тайм-аут соединения с Telegram, бот продолжает работу...")
            return
    print(f"❌ Ошибка: {context.error}")


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    
    def log_message(self, format, *args):
        pass 

def run_webserver():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🌐 Веб-сервер запущен на порту {port} (для Render)")
    server.serve_forever()


def main():
    os.makedirs("downloads", exist_ok=True)
    
    print("🤖 Бот запускается...")
    print(f"Токен загружен: {'Да' if BOT_TOKEN else 'Нет'}")
    
   
    web_thread = threading.Thread(target=run_webserver, daemon=True)
    web_thread.start()
    
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print("🚀 Бот запущен на сервере!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
