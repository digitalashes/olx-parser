import time
from typing import List

from telegram import Bot

from config import settings
from utils.models import NewAdModel


def send_message_into_telegram(bot: Bot, new_ads: List[NewAdModel]) -> None:
    for item in reversed(new_ads):
        text = f'''<a href='{item.url}'>{item.title} ({item.price})</a>
                   <pre>{'; '.join(item.phones)}\n{item.author}\n{item.created}</pre>'''
        for chat in settings.TELEGRAM_CHAT_IDS:
            bot.send_message(chat_id=chat, text=text, parse_mode='HTML')
            time.sleep(0.250)
