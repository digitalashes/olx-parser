import time
from typing import List

from telegram import Bot

from config import logger
from config import settings
from utils.models import NewAdModel


def send_message_into_telegram(bot: Bot, new_ads: List[NewAdModel]) -> None:
    for item in reversed(new_ads):
        text = f'''<a href='{item.url}'>{item.title} ({item.price})</a>
                   <pre>{'; '.join(item.phones)}\n{item.author}\n{item.created}</pre>'''
        for chat in settings.TELEGRAM_CHAT_IDS:
            try:
                bot.send_message(chat_id=chat, text=text, parse_mode='HTML')
                time.sleep(0.250)
            except Exception:  # pylint: disable=broad-except
                logger.exception('=== Error during sending message via Telegram ===')
