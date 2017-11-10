# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import logging
import re
import time
from collections import namedtuple
from urllib.parse import urlparse, urljoin

import pyrebase
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests import session

from settings import config
from utils import build_url

logging.basicConfig(format='%(levelname)-6s [%(asctime)s] %(message)s',
                    filename='{}.log'.format(config.LOG_FILENAME))
logger = logging.getLogger('olx-parser')
logger.setLevel(logging.DEBUG)

Ad = namedtuple('Ad', 'id title name phones price is_fresh posted_at url')


def fetch_ads_detail(url):
    """
    Method parse the detail page of ad and fetch seller name and phone(s) number and data when ad was posted.
    :param url: ad detail page url.
    :return: list of phone(s) numbers, seller name and date when ad was posted.
    """
    ua = UserAgent(fallback=config.DEFAULT_USER_AGENT)
    headers = {
        'Host': urlparse(config.BASE_URL).netloc,
        'User-Agent': ua.random,
        'Referer': url,  # Important! Must be present in headers and be equal of ad url.
        'X-Requested-With': 'XMLHttpRequest',
    }

    with session() as s:
        logger.debug('Starting to fetching seller telephone number and name.')
        response = s.get(url)
        if response.status_code != 200:
            logger.warning('Unsuccessful attempt. Empty values of phone numbers and name.')
            return [], '', ''
        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        # fetch seller name
        name = '{} ({})'.format(soup.find('h4').text.strip(),
                                soup.find('span', class_='user-since').text.strip())
        posted_at = ' '.join(
            [item for item in soup.select_one('div.offer-titlebox__details > em').text.strip().split(' ') if item]
        ).split(', Н')[0]
        # find and get phoneToken (needed for the correct request)
        raw_text = [elem for elem in soup.find_all('script') if 'phoneToken' in elem.text][0].text.strip()
        token = re.findall(r"['\"](.*?)['\"]", raw_text)[0]
        # get id of ad.
        ad_id = url.split('ID')[1].split('.')[0]
        # shaping of the correct url with ad id and phone token
        phone_url = urljoin(config.PHONE_URL, '{}/?pt={}'.format(ad_id, token))
        response = s.get(phone_url, headers=headers)
        if response.status_code != 200:
            logger.warning('Unsuccessful attempt. Empty values of phone numbers.')
            return [], name, posted_at
        phone_number = response.json().get('value')
        logger.debug('Finishing to fetching seller telephone number and name.')
        if not 'span' in phone_number:
            return [phone_number], name, posted_at
        soup = BeautifulSoup(phone_number, 'lxml')
        return [item.text.strip() for item in soup.find_all('span')], name, posted_at


def fetch_ads():
    """
    The method parses first page with ads and returns ads which created yesterday and today only.
    :return: list of Ad object.
    """

    url = build_url()
    ads = []

    with session() as s:
        logger.debug('Starting to fetching ads.')
        response = s.get(url)
        if response.status_code != 200:
            logger.critical('Unsuccessful attempt. Please check url. The script was stopped.')
            exit(0)

    soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
    ads_items = soup.find_all('table', attrs={'summary': 'Объявление'})

    for item in ads_items:

        item_url_obj = item.find('a', class_='marginright5')
        item_url, url_info, *_ = item_url_obj.attrs.get('href').split('#')

        if not config.WITH_PROMOTED and 'promoted' in url_info:
            continue

        try:
            str_price = item.find('p', class_='price').text.split(' грн.')[0].strip().replace(' ', '')
            price = int(str_price)
        except ValueError:
            logger.exception(msg='Error during fetching the price.', exc_info=True)
            continue

        item_title = item_url_obj.text.strip()
        is_fresh = item.find('p', class_='x-normal').text.strip().split(' ')[0].lower()

        ad = Ad(
            id=item.attrs.get('data-id'),
            title=item_title,
            name=None,
            phones=None,
            price=price,
            is_fresh=is_fresh in config.PUBLICATION_DATE,
            posted_at=None,
            url=item_url
        )

        if ad.is_fresh and config.MIN_PRICE <= ad.price <= config.MAX_PRICE:
            ads.append(ad)

    logger.debug('Finishing to fetching ads.')
    return ads


def filter_new_ads(ads):
    """
    The method connect to firebase DB check and if ad not present in DB adding it.
    :param ads:
    :return: list of new Ad objects
    """
    if not ads:
        return None

    new_ads = []

    firebase = pyrebase.initialize_app(config.DB_CONFIG)
    auth = firebase.auth()
    db = firebase.database()
    token = auth.sign_in_with_email_and_password(email=config.USER_EMAIL, password=config.USER_PASSWORD).get('idToken')

    for ad in ads:
        if db.child(ad.id).get(token).pyres:
            continue

        phones, name, posted_at, *_ = fetch_ads_detail(ad.url)
        ad = ad._replace(name=name, phones=phones, posted_at=posted_at)
        dct = ad._asdict()
        [dct.pop(item) for item in ['id', 'is_fresh']]
        db.child(ad.id).push(dct, token)
        new_ads.append(ad)
    return new_ads


def send_message_into_telegram(new_ads):
    """
    The method which sends information about the new ads into the telegram conversation through the bot.
    :param new_ads: list of new ads.
    :return: None
    """
    if not new_ads:
        return

    bot_url = '{}{}/{}'.format(config.TELEGRAM_BOT_API_URL, config.TELEGRAM_BOT_KEY, 'sendMessage')
    message_data = {
        'chat_id': '',
        'text': '',
        'parse_mode': 'HTML'
    }

    with session() as s:
        for item in reversed(new_ads):
            for chat in config.TELEGRAM_CHAT_IDS:
                message_data.update({
                    'chat_id': chat,
                    'text': '''<a href='{url}'>{title} ({price})</a>
                               <pre>{phones}\n{name}\n{posted_at}</pre>'''.format(url=item.url,
                                                                                  title=item.title,
                                                                                  price=item.price,
                                                                                  phones='; '.join(item.phones),
                                                                                  name=item.name,
                                                                                  posted_at=item.posted_at)
                })
                s.post(bot_url, message_data)
                time.sleep(0.250)


def run():
    ads = fetch_ads()
    new_ads = filter_new_ads(ads)
    send_message_into_telegram(new_ads)


if __name__ == '__main__':
    logger.info('The script is launching.')
    run()
    logger.info('The script it stopped.\n\t')
