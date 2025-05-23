
#BOT_TOKEN = "7976024276:AAE_HjIssXdorIanEo6-nO8qfWnamlk__eg"
#WEATHER_API_KEY = "8b2e89c0b6fa00bf89ce6a1a0accd3a1"
import logging
import requests
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7976024276:AAE_HjIssXdorIanEo6-nO8qfWnamlk__eg"
WEATHER_API_KEY = "8b2e89c0b6fa00bf89ce6a1a0accd3a1"
ADMIN_ID = 536614171  # Adminning sonli Telegram ID raqami bilan almashtiring

# Foydalanuvchi holati uchun xotira
user_data_store = {}

# Tilga mos matnlar
messages = {
    "welcome": {
        "uz": "Assalomu alaykum, {}! Xush kelibsiz. Quyidagilardan birini tanlang:",
        "ru": "Здравствуйте, {}! Добро пожаловать. Выберите один из вариантов:",
        "en": "Hello, {}! Welcome. Please choose one of the options below:"
    },
    "choose_lang": {
        "uz": "Tilni tanlang:",
        "ru": "Выберите язык:",
        "en": "Choose a language:"
    },
    "weather_menu": {
        "uz": "⬇ Quyidagi menyudan tanlang:",
        "ru": "⬇ Выберите из меню:",
        "en": "⬇ Choose from the menu below:"
    },
    "help": {
        "uz": "Yordam uchun @silence_offf bilan bog'laning.",
        "ru": "Для помощи свяжитесь с @silence_offf.",
        "en": "For help, contact @silence_offf."
    },
    "weather_info": {
        "uz": "🌡 {} hududidagi harorat: {}°C\n🌥 Ob-havo: {}\n💨 Shamol tezligi: {} m/s\n💧 Namlik: {}%",
        "ru": "🌡 Погода в {}: {}°C\n🌥 Состояние: {}\n💨 Скорость ветра: {} м/с\n💧 Влажность: {}%",
        "en": "🌡 Weather in {}: {}°C\n🌥 Condition: {}\n💨 Wind speed: {} m/s\n💧 Humidity: {}%"
    },
    "not_found": {
        "uz": "Manzil topilmadi. Qayta urinib ko‘ring.",
        "ru": "Город не найден. Попробуйте снова.",
        "en": "Location not found. Please try again."
    },
    "send_location": {
        "uz": "Joylashuv bo‘yicha ob-havoni bilish",
        "ru": "Узнать погоду по геолокации",
        "en": "Get weather by location"
    },
    "enter_location": {
        "uz": "Manzil nomini kiriting:",
        "ru": "Введите название местоположения:",
        "en": "Enter location name:"
    },
    "back": {
        "uz": "◀ Orqaga",
        "ru": "◀ Назад",
        "en": "◀ Back"
    },
    "search_again": {
        "uz": "🔁 Yana qidirish",
        "ru": "🔁 Искать снова",
        "en": "🔁 Search again"
    }
}

def t(user_id, key):
    lang = user_data_store.get(user_id, {}).get("lang", "uz")
    return messages[key].get(lang, messages[key]["uz"])

def main_menu(user_id):
    keyboard = [
        [InlineKeyboardButton("📍 " + t(user_id, "send_location"), callback_data="weather_location")],
        [InlineKeyboardButton("🌍 " + t(user_id, "enter_location"), callback_data="world_search")],
        [InlineKeyboardButton("🌐 " + t(user_id, "choose_lang"), callback_data="change_lang")],
        [InlineKeyboardButton("❓ Yordam", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def language_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name or update.effective_user.username or "Foydalanuvchi"
    if user_id not in user_data_store:
        user_data_store[user_id] = {}
        await update.message.reply_text("Assalomu alaykum, {}!".format(username))
        await update.message.reply_text(messages["choose_lang"]["uz"], reply_markup=language_menu())
    else:
        lang = user_data_store[user_id].get("lang", "uz")
        welcome_msg = messages["welcome"][lang].format(username)
        await update.message.reply_text(welcome_msg, reply_markup=main_menu(user_id))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(t(user_id, "help"))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_data_store[user_id]["lang"] = lang
        username = query.from_user.first_name or query.from_user.username or "Foydalanuvchi"
        await query.edit_message_text(messages["welcome"][lang].format(username), reply_markup=main_menu(user_id))

    elif data == "weather_location":
        kb = [[KeyboardButton("📍 " + t(user_id, "send_location"), request_location=True)]]
        await query.message.reply_text(t(user_id, "send_location"), reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True))

    elif data == "world_search":
        await query.message.reply_text(t(user_id, "enter_location"), reply_markup=ReplyKeyboardRemove())
        context.user_data["search_mode"] = True

    elif data == "change_lang":
        await query.edit_message_text(t(user_id, "choose_lang"), reply_markup=language_menu())

    elif data == "help":
        await query.edit_message_text(t(user_id, "help"))

    elif data == "back_to_menu":
        lang = user_data_store.get(user_id, {}).get("lang", "uz")
        username = query.from_user.first_name or query.from_user.username or "Foydalanuvchi"
        welcome_msg = messages["welcome"][lang].format(username)
        await query.edit_message_text(welcome_msg, reply_markup=main_menu(user_id))

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.first_name or update.effective_user.username or "Foydalanuvchi"
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    lang = user_data_store.get(user_id, {}).get("lang", "uz")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang={lang}"
    response = requests.get(url).json()

    if response.get("cod") == 200:
        city = response.get("name", "")
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        wind = response["wind"].get("speed", "N/A")
        humidity = response["main"].get("humidity", "N/A")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"user_{user_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"🕒 Sana: {now}\n")
            f.write(f"👤 Username: {username}\n")
            f.write(f"🆔 ID: {user_id}\n")
            f.write(f"📍 Latitude: {lat}, Longitude: {lon}\n")
            f.write(f"🌡 Harorat: {temp}°C\n🌥 Ob-havo: {desc}\n💨 Shamol: {wind} m/s\n💧 Namlik: {humidity}%\n")

        with open(filename, "rb") as f:
            await context.bot.send_document(chat_id=ADMIN_ID, document=f, filename=filename, caption=f"📝 {username} ({user_id}) foydalanuvchi ma'lumoti")

        os.remove(filename)

        keyboard = [[InlineKeyboardButton(t(user_id, "back"), callback_data="back_to_menu")]]
        await update.message.reply_text(
            messages["weather_info"][lang].format(city, temp, desc, wind, humidity),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(t(user_id, "not_found"))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("search_mode"):
        city = update.message.text
        lang = user_data_store.get(user_id, {}).get("lang", "uz")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang={lang}"
        response = requests.get(url).json()
        if response.get("cod") == 200:
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            wind = response["wind"].get("speed", "N/A")
            humidity = response["main"].get("humidity", "N/A")
            keyboard = [
                [InlineKeyboardButton(t(user_id, "search_again"), callback_data="world_search")],
                [InlineKeyboardButton(t(user_id, "back"), callback_data="back_to_menu")]
            ]
            await update.message.reply_text(messages["weather_info"][lang].format(city, temp, desc, wind, humidity), reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            keyboard = [
                [InlineKeyboardButton(t(user_id, "search_again"), callback_data="world_search")],
                [InlineKeyboardButton(t(user_id, "back"), callback_data="back_to_menu")]
            ]
            await update.message.reply_text(messages["not_found"][lang], reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["search_mode"] = False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async def set_commands():
        await app.bot.set_my_commands([
            BotCommand("start", "Botni ishga tushirish"),
            BotCommand("help", "Yordam olish")
        ])

    app.post_init = lambda _: set_commands()
    app.run_polling()
