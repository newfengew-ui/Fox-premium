import os
import json
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# База ключей
KEYS_FILE = "premium_keys.json"

def load_keys():
    try:
        with open(KEYS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"keys": {}, "used_keys": []}

def save_keys(data):
    with open(KEYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_key():
    return "PREM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def start(update: Update, context):
    await update.message.reply_text(
        "🦊 **FOX CHEATS PREMIUM**\n\n"
        "💎 Доступ к 5 премиум клиентам Minecraft\n"
        "💰 Цена: 50 ⭐ Telegram Stars\n"
        "⏰ Доступ навсегда!\n\n"
        "Нажми кнопку ниже 👇",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Купить премиум (50 ⭐)", callback_data='buy_premium')]
        ])
    )

async def buy_premium(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_invoice(
        title="🦊 FOX CHEATS PREMIUM",
        description="5 премиум клиентов + доступ навсегда",
        payload="premium_50stars",
        provider_token="",
        currency="XTR",
        prices=[{"label": "Premium Access", "amount": 50}]
    )

async def successful_payment(update: Update, context):
    keys = load_keys()
    key = generate_key()
    
    while key in keys["keys"]:
        key = generate_key()
    
    keys["keys"][key] = {
        "user_id": update.effective_user.id,
        "username": update.effective_user.username,
        "used": False
    }
    save_keys(keys)
    
    await update.message.reply_text(
        f"✅ **ОПЛАТА ПРОШЛА!**\n\n"
        f"🔑 Твой ключ: `{key}`\n\n"
        f"Введи его на сайте для активации!",
        parse_mode='Markdown'
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy_premium, pattern='buy_premium'))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    
    print("🤖 Бот FoxCheats Premium запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
