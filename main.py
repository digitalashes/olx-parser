import time

from requests import session as RequestsSession
from telegram import Bot

from config import logger
from config import settings
from olx import fetch_ads
from olx import filter_new_ads
from tg import send_message_into_telegram


def main():
    new_ads = []
    bot = Bot(token=settings.TELEGRAM_BOT_KEY)

    with RequestsSession() as session:
        ads = fetch_ads(session)
        if ads:
            new_ads = filter_new_ads(session, ads)
    if new_ads:
        send_message_into_telegram(bot, new_ads)


if __name__ == '__main__':
    start_time = time.time()
    logger.info('=== Script has been started ===')
    try:
        main()
    except KeyboardInterrupt:
        logger.info('=== Script has been stopped manually! ===')
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e)
    else:
        logger.info('=== Script has been finished successfully ===')
    finally:
        logger.info('=== Operating time is %s seconds ===', (time.time() - start_time))
