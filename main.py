import random
import time
import telebot

TOKEN = "8804540037:AAHNg4QFZhvvPHFXeBdGXwYhRMG1-5vzb-E"
bot = telebot.TeleBot(TOKEN)

users_data = {}

CARDS_POOL = [
    {
        "name": "Шпион с шапкой призрачного шапокляка 🕵️‍♂️🎩",
        "rarity": "Необычный 🌟 (Unusual)",
        "image": "https://imgur.com",
        "weight": 30,
    }
]


def check_user(user_id):
    if user_id not in users_data:
        users_data[user_id] = {"backpack": [], "balance": 50, "last_roll": 0}


@bot.message_handler(commands=["start"])
def start_cmd(message):
    user_id = message.from_user.id
    check_user(user_id)
    welcome_text = (
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Я бот-коллекционер под управлением Медика! 💉\n\n"
        f"📋 **Твои команды:**\n"
        f"🎁 /tf2 — Крутить дроп предметов (Стоит 10 💰, КД — 2 часа)\n"
        f"🎒 /backpack — Твой инвентарь и баланс кошелька\n"
        f"🛠️ /work — Отправиться на миссию за монетами"
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=["work"])
def work_cmd(message):
    user_id = message.from_user.id
    check_user(user_id)
    reward = random.randint(15, 40)
    users_data[user_id]["balance"] += reward
    bot.reply_to(message, f"Ты помог Медику накрыть точку. Заработано {reward} 💰!")


@bot.message_handler(commands=["tf2"])
def drop_card(message):
    user_id = message.from_user.id
    check_user(user_id)

    current_time = time.time()
    last_roll_time = users_data[user_id]["last_roll"]
    cooldown_seconds = 7200

    if current_time - last_roll_time < cooldown_seconds:
        time_passed = current_time - last_roll_time
        time_left_seconds = cooldown_seconds - time_passed
        minutes_left = int(time_left_seconds // 60)

        bot.reply_to(
            message,
            f"⏳ **Медик запретил крутить так часто!**\n"
            f"Следующий дроп будет доступен через **{minutes_left} мин**.",
        )
        return

    if users_data[user_id]["balance"] < 10:
        bot.reply_to(
            message,
            "❌ Недостаточно монет! Прокрутка стоит 10 💰.\nЮзай /work!",
        )
        return

    users_data[user_id]["balance"] -= 10
    users_data[user_id]["last_roll"] = current_time

    list_weights = [item["weight"] for item in CARDS_POOL]
    chosen_item = random.choices(CARDS_POOL, weights=list_weights, k=1)[0]

    users_data[user_id]["backpack"].append(chosen_item["name"])

    drop_text = (
        f"🎁 **Вам выпал новый предмет!**\n\n"
        f"👤 **Название:** {chosen_item['name']}\n"
        f"⭐ **Редкость:** {chosen_item['rarity']}\n\n"
        f"🎒 Добавлено в /backpack!\n"
        f"💰 Оставшийся баланс: {users_data[user_id]['balance']} 💰\n"
        f"⏳ Включен таймер КД на 2 часа!"
    )

    bot.send_photo(
        message.chat.id,
        chosen_item["image"],
        caption=drop_text,
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["backpack"])
def show_backpack(message):
    user_id = message.from_user.id
    check_user(user_id)
    balance = users_data[user_id]["balance"]
    backpack = users_data[user_id]["backpack"]

    if len(backpack) == 0:
        bot.reply_to(
            message, f"💰 **Баланс:** {balance} 💰\n🎒 Твой рюкзак пока пуст!"
        )
        return

    items_list = "\n".join([f"• {name}" for name in backpack])
    response = f"💰 **Баланс:** {balance} 💰\n🎒 **Инвентарь ({len(backpack)} предм.):**\n\n{items_list}"
    bot.reply_to(message, response, parse_mode="Markdown")


print("Бот запущен...")
bot.infinity_polling()
