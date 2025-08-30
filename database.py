import aiosqlite

DB_NAME = "dorf_bot.db"

async def init_db() -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY
            )
            """
        )
        await db.commit()
        print("✅ Database initialized.")

async def add_subscriber(user_id: int) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)",
            (user_id,),
        )
        await db.commit()

async def remove_subscriber(user_id: int) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM subscribers WHERE user_id = ?",
            (user_id,),
        )
        await db.commit()

async def get_all_subscribers() -> list:
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM subscribers")
        rows = await cur.fetchall()
        return [row[0] for row in rows]

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
