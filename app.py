import sys
import os

print("=== ШАГ 1: Python запущен ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

print("\n=== ШАГ 2: Проверка токена ===")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    sys.exit(1)
else:
    print(f"✅ Токен найден: {BOT_TOKEN[:10]}...")

print("\n=== ШАГ 3: Импорт библиотек ===")
try:
    import re
    print("✅ re импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта re: {e}")
    sys.exit(1)

try:
    import random
    print("✅ random импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта random: {e}")
    sys.exit(1)

try:
    import asyncio
    print("✅ asyncio импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта asyncio: {e}")
    sys.exit(1)

try:
    from telegram import Update
    from telegram.ext import Application, MessageHandler, filters, ContextTypes
    print("✅ telegram импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта telegram: {e}")
    sys.exit(1)

try:
    import yt_dlp
    print(f"✅ yt_dlp импортирован (версия: {yt_dlp.__version__})")
except Exception as e:
    print(f"❌ Ошибка импорта yt_dlp: {e}")
    sys.exit(1)

print("\n=== ШАГ 4: Создание папки downloads ===")
try:
    os.makedirs("downloads", exist_ok=True)
    print("✅ Папка downloads создана")
except Exception as e:
    print(f"❌ Ошибка создания папки: {e}")
    sys.exit(1)

print("\n=== ШАГ 5: Определение функций ===")

def check_for_joke(text):
    text_lower = text.lower()
    if "бот" in text_lower or "bot" in text_lower:
        return "👀 Кто тут меня звал?"
    return None

print("✅ Функция check_for_joke определена")

async def download_video(url):
    loop = asyncio.get_running_loop()
    
    def blocking_download():
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

print("✅ Функция download_video определена")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    url_match = re.search(r'https?://\S+', text)
    
    if url_match:
        url = url_match.group(0)
        status_msg = await update.message.reply_text("📥 Загрузка...")
        try:
            video_path = await download_video(url)
            with open(video_path, 'rb') as video_file:
                await update.message.reply_video(video=video_file, caption="✅ Готово!")
            os.remove(video_path)
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"❌ Ошибка: {str(e)}")
        return
    
    joke_response = check_for_joke(text)
    if joke_response:
        await update.message.reply_text(joke_response)

print("✅ Функция handle_message определена")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")

print("✅ Функция error_handler определена")

print("\n=== ШАГ 6: Запуск бота ===")
print("🤖 Бот запускается...")

try:
    app = Application.builder().token(BOT_TOKEN).build()
    print("✅ Application создан")
except Exception as e:
    print(f"❌ Ошибка создания Application: {e}")
    sys.exit(1)

try:
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Handler добавлен")
except Exception as e:
    print(f"❌ Ошибка добавления handler: {e}")
    sys.exit(1)

try:
    app.add_error_handler(error_handler)
    print("✅ Error handler добавлен")
except Exception as e:
    print(f"❌ Ошибка добавления error_handler: {e}")
    sys.exit(1)

print("\n=== ШАГ 7: Запуск polling ===")
print("🚀 Бот готов, запускаем polling...")

try:
    app.run_polling(drop_pending_updates=True)
except Exception as e:
    print(f"❌ Ошибка при run_polling: {e}")
    sys.exit(1)
