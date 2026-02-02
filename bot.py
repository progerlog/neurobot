import asyncio
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

PROMPT = (
    "Пришли абсурдную новость России или мира в формате «Пездузы» "
    "или в любом другом сатирично-ироничном ключе. "
    "Коротко, 3–6 предложений. Без пояснений."
)

async def send_news():
    print("Пошла функция запроса новости...")
    now = datetime.now().hour
    if not (9 <= now < 23):
        return

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты сатирический новостной редактор."},
            {"role": "user", "content": PROMPT}
        ],
        temperature=1.1
    )

    text = response.choices[0].message.content


    await bot.send_message(chat_id=CHAT_ID, text=text)


async def main():
    print("Пошла функция отправки новости...")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_news, "interval", minutes=1)
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Запущено...")
    asyncio.run(main())