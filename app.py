import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
print(f"Token exists: {bool(BOT_TOKEN)}")
print("Bot starting...")

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

print("Imports done")

def main():
    print("Creating app...")
    app = Application.builder().token(BOT_TOKEN).build()
    print("App created, running polling...")
    app.run_polling()

if __name__ == "__main__":
    main()