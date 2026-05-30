import os
import json
import random
import string
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройки
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("VERCEL_URL")
if WEBHOOK_URL:
    WEBHOOK_URL = f"https://{WEBHOOK_URL}/api/"

# Инициализация приложения
application = Application.builder().token(BOT_TOKEN).build()

# База ключей (простая, через JSON файл)
KEYS_FILE = "premium_keys.json"

def load_keys():
    try:
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"keys": {}, "used_keys": []}

def save_keys(data):
    with open(KEYS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_key():
    return "PREM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦊 **FOX CHEATS PREMIUM**\n\n"
        "Получи доступ к 5 эксклюзивным клиентам Minecraft навсегда!\n\n"
        "💎 **Что ты получишь:**\n"
        "• 5 премиум клиентов\n"
        "• Приоритетная поддержка\n"
        "• Доступ навсегда\n\n"
        "💰 **Цена:** 50 ⭐ Telegram Stars\n\n"
        "Нажми кнопку ниже!",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Купить премиум (50 )", callback_data='buy_premium')]
        ])
    )
# Покупка
async def buy_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_invoice(
        title="FOX CHEATS PREMIUM",
        description="Доступ к 5 премиум клиентам навсегда",
        payload="premium_50stars",
        provider_token="",
        currency="XTR",
        prices=[{"label": "Premium", "amount": 50}],
    )

# Успешная оплата
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key_data = load_keys()
    new_key = generate_key()
    
    while new_key in key_data["keys"]:
        new_key = generate_key()
    
    user_id = update.effective_user.id
    username = update.effective_user.username or "No username"
    
    key_data["keys"][new_key] = {
        "user_id": user_id,
        "username": username,
        "used": False,
        "date": str(update.message.date)
    }
    save_keys(key_data)
    
    await update.message.reply_text(
        f"✅ **Оплата прошла!**\n\n"
        f"🔑 Твой ключ: `{new_key}`\n\n"
        f"Введи его на сайте для активации!",
        parse_mode='Markdown'
    )

# Регистрация хендлеров
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(buy_premium, pattern='buy_premium'))
application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

# Главная функция для Vercel
async def handler(request):
    try:
        body = await request.json()        update = Update.de_json(body, application.bot)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
