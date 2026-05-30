import os
import json
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройки
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PREMIUM_PRICE = 50
KEYS_FILE = "premium_keys.json"

# Загрузка базы ключей
def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"keys": {}, "used_keys": []}

def save_keys(data):
    with open(KEYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_key():
    return "PREM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Инициализация приложения
application = Application.builder().token(BOT_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦊 **FOX CHEATS PREMIUM**\n\n"
        "🔥 Получи доступ к **5 эксклюзивным клиентам** Minecraft навсегда!\n\n"
        "💎 **Что ты получишь:**\n"
        "• 5 премиум клиентов с обходом античитов\n"
        "• Приоритетная поддержка\n"
        "• Доступ навсегда (не подписка!)\n\n"
        "💰 **Цена:** 50 ⭐ Telegram Stars\n\n"
        "Нажми кнопку ниже, чтобы купить!",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Купить премиум (50 ⭐)", callback_data='buy_premium')]
        ])
    )

# Покупка премиума
async def buy_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()    
    await query.message.reply_invoice(
        title="🦊 FOX CHEATS PREMIUM",
        description="Доступ к 5 премиум клиентам Minecraft навсегда + приоритетная поддержка",
        payload="premium_access_50stars",
        provider_token="",
        currency="XTR",
        prices=[{"label": "Premium Access (Lifetime)", "amount": 50}],
        is_flexible=False,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False
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
        "purchase_date": str(update.message.date)
    }
    save_keys(key_data)
    
    await update.message.reply_text(
        "✅ **ОПЛАТА ПРОШЛА УСПЕШНО!**\n\n"
        "🎉 Спасибо за покупку!\n\n"
        "🔑 **Твой премиум ключ:**\n"
        f"`{new_key}`\n\n"
        "📱 **Как активировать:**\n"
        "1. Перейди на сайт: https://newfengew-ui.github.io/foxcheats/\n"
        "2. Нажми на кнопку **PREMIUM** в шапке сайта\n"
        "3. Введи этот ключ в поле\n"
        "4. Нажми **Активировать**\n"
        "5. Готово! Теперь у тебя есть доступ к 5 премиум клиентам! 🔥\n\n"
        "💬 Если есть вопросы — пиши @newfen",
        parse_mode='Markdown'
    )

# Регистрация обработчиковapplication.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(buy_premium, pattern='buy_premium'))
application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

# Handler для Vercel (ОБЯЗАТЕЛЬНО!)
async def handler(request):
    try:
        body = await request.json()
        update = Update.de_json(body, application.bot)
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
