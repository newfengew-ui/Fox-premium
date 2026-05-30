import os
import json
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8022270005:AAGsG2P5tiih6CN7EZTgHEtEwl7_258VxFA"
PREMIUM_PRICE = 50  # 50 Telegram Stars
KEYS_FILE = "premium_keys.json"
# ===============================

# Загрузка базы ключей
def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"keys": {}, "used_keys": []}

# Сохранение базы ключей
def save_keys(data):
    with open(KEYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Генерация уникального ключа
def generate_key():
    return "PREM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

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
    # Создаем инвойс (счет) на 50 Stars
    await query.message.reply_invoice(
        title="🦊 FOX CHEATS PREMIUM",
        description="Доступ к множеству премиум клиентам Minecraft навсегда + приоритетная поддержка",
        payload="premium_access_50stars",
        provider_token="",  # ПУСТОЙ для Telegram Stars!
        currency="XTR",  # XTR = Telegram Stars
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
    
    # Генерируем уникальный ключ
    new_key = generate_key()
    
    # Проверяем, что ключ уникальный
    while new_key in key_data["keys"]:
        new_key = generate_key()
    
    # Сохраняем ключ
    user_id = update.effective_user.id
    username = update.effective_user.username or "No username"
    
    key_data["keys"][new_key] = {
        "user_id": user_id,
        "username": username,
        "used": False,
        "purchase_date": str(update.message.date)
    }
    save_keys(key_data)
    
    # Отправляем ключ пользователю
    await update.message.reply_text(
        "✅ **ОПЛАТА ПРОШЛА УСПЕШНО!**\n\n"
        "🎉 Спасибо за покупку!\n\n"
        "🔑 **Твой премиум ключ:**\n"
        f"`{new_key}`\n\n"
        "📱 **Как активировать:**\n"
        "1. Перейди на сайт: https://newfengew-ui.github.io/foxcheats/\n"
        "2. Нажми на кнопку **PREMIUM** в шапке сайта\n"
        "3. Введи этот ключ в поле\n"
        "4. Нажми **Активировать**\n"        "5. Готово! Теперь у тебя есть доступ к 5 премиум клиентам! 🔥\n\n"
        "💬 Если есть вопросы — пиши @newfen",
        parse_mode='Markdown'
    )
    
    # Отправляем уведомление админу (тебе)
    admin_id = 8397829176 # ЗАМЕНИ НА СВОЙ TELEGRAM ID!
    try:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"💰 **НОВАЯ ПОКУПКА!**\n\n"
                 f"👤 Пользователь: @newfen}\n"
                 f"🔑 Ключ: {new_key}\n"
                 f"💵 Сумма: 50 ⭐",
            parse_mode='Markdown'
        )
    except:
        pass

# Проверка ключа (команда /check)
async def check_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) > 0:
        key = context.args[0].upper()
        key_data = load_keys()
        
        if key in key_data["keys"]:
            key_info = key_data["keys"][key]
            if not key_info["used"]:
                await update.message.reply_text(
                    f"✅ **Ключ действителен!**\n\n"
                    f"🔑 Ключ: {key}\n"
                    f"👤 Владелец: @{key_info['username']}\n"
                    f"📅 Дата покупки: {key_info['purchase_date']}\n\n"
                    f"Используй его на сайте для активации премиума!"
                )
            else:
                await update.message.reply_text("❌ Этот ключ уже был использован.")
        else:
            await update.message.reply_text("❌ Неверный ключ. Проверь правильность ввода.")
    else:
        await update.message.reply_text(
            "🔍 **Проверка ключа**\n\n"
            "Используй: `/check <ключ>`\n\n"
            "Пример: `/check PREM-ABC123XY`"
        )

# Информация о боте
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key_data = load_keys()
    total_keys = len(key_data["keys"])    used_keys = len(key_data["used_keys"])
    
    await update.message.reply_text(
        "📊 **Статистика бота:**\n\n"
        f"🔑 Всего выдано ключей: {total_keys}\n"
        f"✅ Использовано: {used_keys}\n"
        f"💰 Цена премиума: {PREMIUM_PRICE} ⭐\n\n"
        "🦊 FOX CHEATS Premium Bot"
    )

# Главная функция
def main():
    print("🤖 Запуск бота FoxCheats Premium...")
    print(f"💰 Цена: {PREMIUM_PRICE} Telegram Stars")
    print("=" * 40)
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_key))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CallbackQueryHandler(buy_premium, pattern='buy_premium'))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    
    # Запускаем бота
    print("✅ Бот запущен и готов к работе!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
