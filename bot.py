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
    "Ты редактор сатиро-ироничного информ. агентства."

    "Твоя задача написать юмористичную новость в сатиро-ироничном ключе, над которой можно посмеяться для телеграм-канала.Новости могут быть как и из России, так и со всего мира"

    "Можно шутить про вечные блокировки в России, так и про файлы Эпштейна в США.Это только как пример.Одна новость - одно сообщение."

    " Пиши в следующем формате"

    "⚡️ Заголовок новости"

    "Текст новости.3-6 предложений без пояснений"
)

# Для "цепочки сообщений", можно хранить parent_message_id
PARENT_MESSAGE_ID = None


def request_agent(prompt: str, parent_message_id: str = None) -> str:
    """
    Отправка запроса к Timeweb Agent (нативный API)
    """
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
    return data.get("message", "")


async def send_news():
    """
    Отправка новости в Telegram
    """
    now_hour = datetime.now().hour
    if not (11 <= now_hour < 21):
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
            print(f"[INFO] Отправлено в Telegram: {text[:50]}...")
    except Exception as e:
        print(f"[ERROR] Ошибка при запросе к Timeweb Agent: {e}")


async def main():
    """
    Основная функция
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_news, "interval", minutes=1)
    scheduler.start()

    print("[INFO] Бот запущен. Рассылка новостей каждые 30 минут с 9:00 до 23:00.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

# import requests
#
# url = "https://api.timeweb.cloud/api/v1/cloud-ai/agents/986ff584-52c1-4135-a6b5-1764c3a4b021/call"
#
# payload = {
#     "message": "Привет",
#     "parent_message_id": "3adfea84-bcdb-44b5-8914-92035e75ec24"
# }
# headers = {
#     "content-type": "application/json",
#     "authorization": "Bearer eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoiaXM0MDA3MyIsInR5cGUiOiJhcGlfa2V5IiwiYXBpX2tleV9pZCI6IjQyOTM2NGEyLTAyMjktNGQxMy1hNTM3LTZiMjJmYTE0M2M0NSIsImlhdCI6MTc3MDAyNzk2M30.TTUi0ND9mxalnZ44ZpPykZnbn26jWt0bMGxK38fQAUGlS1dVaWjHJ3fOAIq8elVuxhJO8Lpru_JCZvq2ym6MtN4oMLH0rJFgLr_n9SHOx78sIUDVAq5xOkDJ9gxHdSOixXiAhw44A0dQADJW6vvZH71SHHtH1ROhXsadBZV-WBNJLKsV0ZMB84DO7tvM09K8XkukhWa1Sqgsm5l_cDarqn4K6fz8KdwMjlIu1TgTpiQ7bSzpIydHOuPC_N3aYqlGugRFPraEQZ4TvS75S8_cFB0g1DOcg0ykKQAGvY0Oyl8kaIkGr8pSZQj_0ycpAGsOE3lKV4_wEGMFJTRK3C2f6jxiDFjoDnjqoszsuObSwUCX9slTqC_dg2N-045lXBSzsIUTPzJjrFiYgPexRnGyg2Ni75t7l3kBMyoWdj6dD80LAF9NJyd2yg9Jlr2bZmghhwvMtlZ7n1HYBxYHBKuYF53VbtWaUpJXv_OPveSZ2KfR1wO--fALjHvjcItThHRR"
# }
#
# response = requests.post(url, json=payload, headers=headers)
#
# print(response.json())
