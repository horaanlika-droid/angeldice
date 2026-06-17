from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_IDS
from database import *
import random
import time
import asyncio

router = Router()
bot = None

PAYMENT_LINK = "https://yoomoney.ru/to/4100119149767529"

# Цены и количество бросков
PRICE_TIERS = {
    1: {"price": 250, "rolls": 1, "label": "1 бросок - 250 ₽"},
    2: {"price": 350, "rolls": 2, "label": "2 броска - 350 ₽"},
    3: {"price": 500, "rolls": 3, "label": "3 броска - 500 ₽"},
}

# ========== ТРИ КУБИКА ==========

# КУБИК 1: Классический
DICE_1_PRIZES = {
    1: "1️⃣ КРУЖОЧЕК С НОЖКАМИ\n\n🦶 Отправь кружочек с ножками в ЛС @milla_femdomqueen",
    2: "2️⃣ НИЧЕГО\n\n🫪🙇🏻🙏🏻 Можешь попросить переброс в ЛС",
    3: "3️⃣ ОЦЕНКА 🤏\n\n👀 Богиня Мила оценит твой член на видео (10 секунд)",
    4: "4️⃣ ПЕРЕБРОС\n\n🔄 Ты можешь перебросить кубик! Напиши в ЛС @milla_femdomqueen",
    5: "5️⃣ СЕССИЯ 10 МИНУТ\n\n👑 Бесплатная 10-минутная сессия с Богиней Милой!",
    6: "6️⃣ ФОТОСЕТ (5 ФОТО)\n\n📸 Эксклюзивный фотосет из 5 фото в ЛС"
}

# КУБИК 2: Экстрим
DICE_2_PRIZES = {
    1: "1️⃣ ЧМОР В ГОЛОСОВОМ\n\n🎤 Запиши голосовое с чмором 30 секунд",
    2: "2️⃣ ЗАДАНИЕ С ОТЧЕТОМ\n\n📝 Выполни задание и пришли отчет в ЛС",
    3: "3️⃣ НИЧЕГО\n\n🫪🙇🏻🙏🏻 Попробуй ещё раз",
    4: "4️⃣ ВХОД В ПРИВАТКУ\n\n🔞 Доступ к закрытому каналу с контентом",
    5: "5️⃣ FF ВИДЕО\n\n🎥 Запиши FF видео 10 секунд в ЛС",
    6: "6️⃣ 1 БЕСПЛАТНЫЙ БРОСОК\n\n🎲 Получи бесплатный бросок в любом кубике!"
}

# КУБИК 3: Премиум
DICE_3_PRIZES = {
    1: "1️⃣ СКИДКА 50% НА СЕССИЮ\n\n💰 Сессия со скидкой 50%!",
    2: "2️⃣ ЗАДАНИЕ НА ВЫНОСЛИВОСТЬ\n\n🏋️ Выполни сложное задание на выносливость",
    3: "3️⃣ ПОДПИСКА НА ТГК\n\n📢 Подписка на Telegram-канал Богини Милы",
    4: "4️⃣ НИЧЕГО\n\n🫪🙇🏻🙏🏻 Попробуй ещё раз",
    5: "5️⃣ ЧМОР В КРУЖОЧКЕ\n\n🔄 Отправь кружочек с чмором 15 секунд",
    6: "6️⃣ ДЕМО-ПОСТОЯНКА (3 ДНЯ)\n\n⛓️ 3 дня демо-постоянки с заданиями"
}

# Все кубики в одном месте
DICE_SETS = {
    1: {"name": "🎲 КЛАССИЧЕСКИЙ", "prizes": DICE_1_PRIZES},
    2: {"name": "🔥 ЭКСТРИМ", "prizes": DICE_2_PRIZES},
    3: {"name": "👑 ПРЕМИУМ", "prizes": DICE_3_PRIZES},
}

def set_bot(bot_instance):
    global bot
    bot = bot_instance

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎲 ВЫБРАТЬ КУБИК")],
            [KeyboardButton(text="💰 КУПИТЬ БРОСКИ")],
            [KeyboardButton(text="📊 МОЯ СТАТИСТИКА")],
            [KeyboardButton(text="❓ ПОМОЩЬ")]
        ],
        resize_keyboard=True
    )

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    await create_player(user_id, username)
    
    await message.answer(
        f"🎲 Добро пожаловать в КУБИКИ, {username}!\n\n"
        "🔥 Выбери один из трёх кубиков и бросай!\n"
        "🫪🙇🏻🙏🏻",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "🎲 ВЫБРАТЬ КУБИК")
async def choose_dice(message: Message):
    user_id = message.from_user.id
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 КЛАССИЧЕСКИЙ", callback_data="dice_1")],
        [InlineKeyboardButton(text="🔥 ЭКСТРИМ", callback_data="dice_2")],
        [InlineKeyboardButton(text="👑 ПРЕМИУМ", callback_data="dice_3")],
    ])
    
    await message.answer(
        "🎲 ВЫБЕРИ КУБИК 🎲\n\n"
        "🎲 Классический — стандартные призы\n"
        "🔥 Экстрим — более жёсткие задания\n"
        "👑 Премиум — лучшие призы\n\n"
        "🫪🙇🏻🙏🏻",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("dice_"))
async def roll_selected_dice(callback: CallbackQuery):
    user_id = callback.from_user.id
    dice_id = int(callback.data.split("_")[1])
    
    rolls_left = await get_rolls_left(user_id)
    
    if rolls_left <= 0:
        await callback.message.answer(
            "🎲 У ТЕБЯ НЕТ БРОСКОВ! 🎲\n\n"
            "Купи пакет бросков:\n"
            "1 бросок - 250 ₽\n"
            "2 броска - 350 ₽\n"
            "3 броска - 500 ₽\n\n"
            "Нажми «💰 КУПИТЬ БРОСКИ»\n"
            "🫪🙇🏻🙏🏻"
        )
        await callback.answer()
        return
    
    dice_name = DICE_SETS[dice_id]["name"]
    prizes = DICE_SETS[dice_id]["prizes"]
    
    # Бросаем кубик
    result = random.randint(1, 6)
    
    # Уменьшаем количество бросков
    await set_rolls_left(user_id, rolls_left - 1)
    await increment_used_rolls(user_id)
    
    prize_text = prizes[result]
    
    await callback.message.answer(
        f"🎲 {dice_name} 🎲\n\n"
        f"🎲 РЕЗУЛЬТАТ: {result}\n\n"
        f"{prize_text}\n\n"
        f"📊 Осталось бросков: {rolls_left - 1}\n"
        f"🫪🙇🏻🙏🏻"
    )
    
    # Уведомление админу
    username = callback.from_user.username or callback.from_user.first_name
    await bot.send_message(
        ADMIN_IDS[0],
        f"🎲 КУБИКИ!\n\n"
        f"👤 Пользователь: @{username}\n"
        f"🎲 Кубик: {dice_name}\n"
        f"🎲 Результат: {result}\n"
        f"🎁 Приз: {prize_text.split(chr(10))[0][:50]}\n"
        f"📊 Осталось бросков: {rolls_left - 1}"
    )
    
    await callback.answer()

@router.message(F.text == "💰 КУПИТЬ БРОСКИ")
async def buy_rolls_menu(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 бросок - 250 ₽", callback_data="buy_tier_1")],
        [InlineKeyboardButton(text="2 броска - 350 ₽", callback_data="buy_tier_2")],
        [InlineKeyboardButton(text="3 броска - 500 ₽", callback_data="buy_tier_3")],
    ])
    
    await message.answer(
        "🎲 ВЫБЕРИ ПАКЕТ БРОСКОВ 🎲\n\n"
        "1 бросок - 250 ₽\n"
        "2 броска - 350 ₽\n"
        "3 броска - 500 ₽\n\n"
        "🫪🙇🏻🙏🏻",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("buy_tier_"))
async def buy_tier(callback: CallbackQuery):
    tier = int(callback.data.split("_")[2])
    price = PRICE_TIERS[tier]["price"]
    rolls = PRICE_TIERS[tier]["rolls"]
    
    await callback.message.answer(
        f"🎲 ОПЛАТА ПАКЕТА 🎲\n\n"
        f"📦 {PRICE_TIERS[tier]['label']}\n"
        f"💰 Сумма: {price} ₽\n\n"
        f"💳 Оплатить: {PAYMENT_LINK}\n\n"
        "📌 После оплаты напиши в ЛС @milla_femdomqueen и пришли чек.\n"
        "Богиня проверит и активирует броски.\n\n"
        "🫪🙇🏻🙏🏻",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 ОПЛАТИТЬ", url=PAYMENT_LINK)]
        ])
    )
    await callback.answer()

@router.message(Command("activate"))
async def cmd_activate(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав")
        return
    
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ /activate @username tier(1-3)")
        return
    
    username = args[1].replace("@", "").lower()
    try:
        tier = int(args[2])
    except ValueError:
        await message.answer("❌ Уровень должен быть числом (1-3)")
        return
    
    if tier not in PRICE_TIERS:
        await message.answer("❌ Уровень должен быть 1, 2 или 3")
        return
    
    async with aiosqlite.connect("dice_game.db") as db:
        async with db.execute("SELECT user_id FROM players WHERE LOWER(username) = ?", (username,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                await message.answer(f"❌ Пользователь @{username} не найден")
                return
            user_id = row[0]
    
    rolls = PRICE_TIERS[tier]["rolls"]
    await set_payment_tier(user_id, tier)
    await set_rolls_left(user_id, rolls)
    
    await message.answer(
        f"✅ АКТИВИРОВАНО!\n\n"
        f"👤 @{username}\n"
        f"📦 {PRICE_TIERS[tier]['label']}\n"
        f"🎲 Осталось бросков: {rolls}"
    )
    
    try:
        await bot.send_message(
            user_id,
            f"🎲 БОГИНЯ МИЛА АКТИВИРОВАЛА ТВОИ БРОСКИ! 🎲\n\n"
            f"📦 {PRICE_TIERS[tier]['label']}\n"
            f"🎲 Осталось бросков: {rolls}\n\n"
            "Нажми «🎲 ВЫБРАТЬ КУБИК» и испытай удачу!\n"
            "🫪🙇🏻🙏🏻"
        )
    except:
        pass

@router.message(F.text == "📊 МОЯ СТАТИСТИКА")
async def my_stats(message: Message):
    user_id = message.from_user.id
    
    tier = await get_payment_tier(user_id)
    rolls_left = await get_rolls_left(user_id)
    used = await get_used_rolls(user_id)
    
    tier_label = PRICE_TIERS[tier]["label"] if tier in PRICE_TIERS else "Нет"
    
    await message.answer(
        f"📊 ТВОЯ СТАТИСТИКА 📊\n\n"
        f"📦 Пакет: {tier_label}\n"
        f"🎲 Осталось бросков: {rolls_left}\n"
        f"🎲 Использовано бросков: {used}\n"
        f"🫪🙇🏻🙏🏻"
    )

@router.message(Command("reset_dice"))
async def cmd_reset_dice(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ /reset_dice @username")
        return
    
    username = args[1].replace("@", "").lower()
    
    async with aiosqlite.connect("dice_game.db") as db:
        async with db.execute("SELECT user_id FROM players WHERE LOWER(username) = ?", (username,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                await message.answer(f"❌ Пользователь @{username} не найден")
                return
            user_id = row[0]
    
    await reset_player(user_id)
    await message.answer(f"✅ Прогресс сброшен для @{username}")

@router.message(Command("broadcast_dice"))
async def cmd_broadcast_dice(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ /broadcast_dice текст_сообщения")
        return
    
    text = args[1]
    users = await get_all_players()
    
    success = 0
    fail = 0
    
    for (user_id, username, tier, rolls_left, used) in users:
        try:
            await bot.send_message(user_id, text)
            success += 1
        except:
            fail += 1
        await asyncio.sleep(0.05)
    
    await message.answer(f"✅ РАССЫЛКА ЗАВЕРШЕНА\n\n📨 Отправлено: {success}\n❌ Ошибок: {fail}")

@router.message(F.text == "❓ ПОМОЩЬ")
async def help_button(message: Message):
    await message.answer(
        "📖 ПОМОЩЬ КУБИКИ 🎲\n\n"
        "🎲 ВЫБРАТЬ КУБИК — выбрать один из трёх кубиков и бросить\n"
        "💰 КУПИТЬ БРОСКИ — выбрать пакет бросков\n"
        "📊 МОЯ СТАТИСТИКА — посмотреть остаток бросков\n\n"
        "📦 ПАКЕТЫ:\n"
        "1 бросок - 250 ₽\n"
        "2 броска - 350 ₽\n"
        "3 броска - 500 ₽\n\n"
        "🎲 ТРИ КУБИКА:\n"
        "🎲 Классический — стандартные призы\n"
        "🔥 Экстрим — жёсткие задания\n"
        "👑 Премиум — лучшие призы\n\n"
        "💰 Оплата: {PAYMENT_LINK}\n"
        "📌 После оплаты напиши в ЛС @milla_femdomqueen и пришли чек.\n\n"
        "🫪🙇🏻🙏🏻"
    )

@router.message(Command("a"))
async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 СПИСОК ИГРОКОВ", callback_data="admin_players_dice")],
        [InlineKeyboardButton(text="📊 СТАТИСТИКА", callback_data="admin_stats_dice")]
    ])
    await message.answer("🔧 АДМИН-ПАНЕЛЬ КУБИКОВ", reply_markup=keyboard)

@router.callback_query(F.data == "admin_players_dice")
async def admin_players_dice(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return
    
    users = await get_all_players()
    if not users:
        await callback.message.answer("📭 Нет игроков")
        return
    
    text = "👥 СПИСОК ИГРОКОВ:\n\n"
    for user_id, username, tier, rolls_left, used in users[:20]:
        tier_label = PRICE_TIERS[tier]["label"] if tier in PRICE_TIERS else "Нет"
        text += f"• {username} | {tier_label} | Осталось: {rolls_left} | Сыграно: {used}\n"
    
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "admin_stats_dice")
async def admin_stats_dice(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return
    
    users = await get_all_players()
    total = len(users)
    total_rolls = 0
    total_used = 0
    
    for user_id, username, tier, rolls_left, used in users:
        total_rolls += rolls_left
        total_used += used
    
    await callback.message.answer(
        f"📊 СТАТИСТИКА КУБИКОВ:\n\n"
        f"👥 Всего игроков: {total}\n"
        f"🎲 Всего бросков куплено: {total_rolls + total_used}\n"
        f"🎲 Использовано бросков: {total_used}\n"
        f"🎲 Осталось бросков: {total_rolls}\n"
        f"🫪🙇🏻🙏🏻"
    )
    await callback.answer()