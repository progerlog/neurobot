import os
import asyncio
from datetime import datetime
import requests
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
AGENT_ID = os.getenv("TIMEWEB_AGENT_ID")
ACCESS_TOKEN = os.getenv("TIMEWEB_ACCESS_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Промт для GPT
PROMPT = (
    "You are the editor of the satirical and ironic inform. agencies. Your task is to write humorous news in a satirical and ironic way, which you can laugh at for the telegram channel. The news can be both from Russia, USA, Germany, China or France."

    "Emphasize the absurdity and subtle humor. Write in the following format.\n\n *Only one news item in one message*\n"

    "⚡️ Post headline\n"

    "The text of the news item. \n 2-3 sentences without explanations\n"

    "*Important: when translating a text into Russian, review the text again because sometimes the meaning is very difficult to understand*"
)

# Для "цепочки сообщений", можно хранить parent_message_id
PARENT_MESSAGE_ID = None


def request_agent(prompt: str, parent_message_id: str = None) -> str:
    """
    Отправка запроса к Timeweb Agent (нативный API)
    """
    now_time = datetime.now().strftime("%H:%M")
    url = f"https://api.timeweb.cloud/api/v1/cloud-ai/agents/{AGENT_ID}/call"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": prompt,
        "parent_message_id": parent_message_id  # None для нового диалога
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    # Обновляем parent_message_id для цепочки, если есть
    new_parent_id = data.get("response_id")
    if new_parent_id:
        global PARENT_MESSAGE_ID
        PARENT_MESSAGE_ID = new_parent_id
    # Возвращаем текст
    print(f"[INFO][{now_time}] Запрос отработан")
    return data.get("message", "")


async def send_news():
    """
    Отправка новости в Telegram
    """
    now_hour = datetime.now().hour
    now_time = datetime.now().strftime("%H:%M")

    if not (5 <= now_hour < 23):
        return

    try:
        text = request_agent(PROMPT, PARENT_MESSAGE_ID)
        final_text = (
            f"{text}\n\n"
            f'<a href="{CHANNEL_URL}">Подписаться на канал 🔥</a>'
        )
        if text:
            await bot.send_message(chat_id=CHANNEL_ID, text=final_text, parse_mode="HTML",
                                   disable_web_page_preview=True)
            print(f"[INFO][{now_time}] Отправлено в Telegram: {text[:50]}...")
    except Exception as e:
        print(f"[ERROR][{now_time}] Ошибка при запросе к Timeweb Agent: {e}")


async def main():
    """
    Основная функция
    """
    now_time = datetime.now().strftime("%H:%M")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_news, "interval", minutes=30)
    # scheduler.add_job(send_news, "interval", seconds=15)
    scheduler.start()

    print(f"[INFO][{now_time}] Бот запущен. Рассылка новостей каждые 30 минут с 11:00 до 23:00.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
