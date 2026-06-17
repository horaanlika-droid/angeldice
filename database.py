import aiosqlite
import sqlite3

DB_NAME = "dice_game.db"

def init_db_sync():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            payment_tier INTEGER DEFAULT 0,
            rolls_left INTEGER DEFAULT 0,
            last_roll_time INTEGER DEFAULT 0,
            used_rolls INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных кубиков инициализирована")

init_db_sync()

async def create_player(user_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO players (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()

async def get_player(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def set_payment_tier(user_id: int, tier: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET payment_tier = ? WHERE user_id = ?",
            (tier, user_id)
        )
        await db.commit()

async def get_payment_tier(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT payment_tier FROM players WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def set_rolls_left(user_id: int, rolls: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET rolls_left = ? WHERE user_id = ?",
            (rolls, user_id)
        )
        await db.commit()

async def get_rolls_left(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT rolls_left FROM players WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def set_last_roll_time(user_id: int, timestamp: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET last_roll_time = ? WHERE user_id = ?",
            (timestamp, user_id)
        )
        await db.commit()

async def get_last_roll_time(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT last_roll_time FROM players WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def increment_used_rolls(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET used_rolls = used_rolls + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def get_used_rolls(user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT used_rolls FROM players WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def reset_player(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE players SET payment_tier = 0, rolls_left = 0, used_rolls = 0 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def get_all_players():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id, username, payment_tier, rolls_left, used_rolls FROM players") as cursor:
            return await cursor.fetchall()