import re
import sqlite3
from contextlib import closing
from typing import List
from typing import Set
from typing import Tuple
from urllib.parse import urljoin
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from dateutil import parser
from fake_useragent import UserAgent
from requests import ConnectionError as RequestsConnectionError
from requests import session as Session

from config import logger
from config import settings
from db.queries import add_phones
from db.queries import create_ad
from db.queries import create_author
from db.queries import get_author_id
from db.queries import get_exists_ads
from db.utils import check_db
from olx.utils import _get_landlord_created_at
from olx.utils import _get_landlord_id
from olx.utils import _get_landlord_name
from olx.utils import _get_landlord_other_ads_count
from olx.utils import _get_landlord_url
from utils import RussianParserInfo
from utils import build_url
from utils.models import AdModel
from utils.models import LandLordModel
from utils.models import NewAdModel


def fetch_ads(session: Session) -> Set[AdModel]:
    url = build_url()
    ads = []

    logger.info('=== Starting fetch ads ===')

    response = session.get(url)
    if response.status_code != 200:
        logger.critical('=== Unsuccessful attempt. '
                        'Please check url - %s '
                        'The script will be stopped ===', url)
        raise RequestsConnectionError('Unable to get urls')

    soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
    ads_items = soup.find_all('table', attrs={'summary': 'Объявление'})

    logger.info('=== Start processing %s ads ===', len(ads_items))
    for item in ads_items:

        item_url_obj = item.find('a', class_='marginright5')
        item_url, url_info, *_ = item_url_obj.attrs.get('href').split('#')

        if not settings.WITH_PROMOTED and 'promoted' in url_info:
            continue

        try:
            price = int(
                item.find('p', class_='price').text.split(' грн.')[0].strip().replace(' ', '')
            )
        except ValueError:
            logger.exception('=== Error during parsing a price ===')
            continue

        day = item.select('small > span')[1].text.strip().split(' ')[0].lower()

        ad = AdModel(
            external_id=item.attrs.get('data-id'),
            title=item_url_obj.text.strip(),
            price=price,
            url=item_url,
        )

        if day in settings.PUBLICATION_DATE and \
                settings.MIN_PRICE <= ad.price <= settings.MAX_PRICE:
            ads.append(ad)

    result = {ad for ad in ads}
    logger.info('=== Found %s ads after filtering ===', len(result))
    return result


def filter_new_ads(session: Session, ads: Set[AdModel]) -> List[NewAdModel]:
    new_ads = []
    result = []

    with closing(sqlite3.connect(settings.DB_NAME)) as db_connect:
        with closing(db_connect.cursor()) as db_cursor:
            check_db(db_connect, db_cursor)
            exists_ads = get_exists_ads(db_cursor, sorted([ad.external_id for ad in ads]))
            ads = [ad for ad in ads if ad.external_id not in exists_ads]
            for ad in ads:
                result.append(fetch_ads_detail(session, ad))

            for item in filter(None, result):
                ad, author, phones, *_ = item
                author_id = get_author_id(db_cursor, author.external_id)
                if author_id is None:
                    author_id = create_author(db_cursor, author)
                ad = ad._replace(author_id=author_id)

                create_ad(db_cursor, ad)
                add_phones(db_cursor, author_id, phones)

                new_ads.append(
                    NewAdModel(
                        title=ad.title,
                        price=ad.price,
                        url=ad.url,
                        created=ad.created,
                        author=author.name,
                        phones=phones,
                    )
                )
                db_connect.commit()
    return new_ads


def fetch_ads_detail(session: Session,
                     ad: AdModel) -> Tuple[AdModel, LandLordModel, List[str]] or None:
    ua = UserAgent(fallback=settings.DEFAULT_USER_AGENT)
    headers = {
        'Host': urlparse(settings.BASE_URL).netloc,
        'User-Agent': ua.random,
        'Referer': ad.url,  # Important! Must be present in headers and be equal of ad url.
        'X-Requested-With': 'XMLHttpRequest',
    }
    logger.debug('=== Starting to fetch landlord telephone number and name ===')
    response = session.get(ad.url)

    if response.status_code != 200:
        logger.warning('=== Unsuccessful attempt ===')
        return None

    soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
    if soup.select('div#ad-not-available-box'):
        return None

    # fetch landlord info
    landlord_url = _get_landlord_url(soup)
    landlord_id = _get_landlord_id(landlord_url)
    landlord_name = _get_landlord_name(soup)
    landlord_created_at = _get_landlord_created_at(soup)
    landlord_other_ads = _get_landlord_other_ads_count(soup)
    author = LandLordModel(
        external_id=landlord_id,
        url=landlord_url,
        name=landlord_name,
        platform_created_at=landlord_created_at,
        other_ads=landlord_other_ads,
    )

    posted_at = ' '.join(
        filter(None, soup.select_one('div.offer-titlebox__details > em').text.strip().split(' '))
    )
    posted_at = parser.parse(re.findall(r'\s\d+:\d+, \d+ \w+ \d+', posted_at)[0],
                             parserinfo=RussianParserInfo())
    ad = ad._replace(created=posted_at)

    # find and get phoneToken (needed for correct request)
    raw_text = [elem for elem in soup.find_all('script')
                if 'phoneToken' in elem.text][0].text.strip()
    token = re.findall(r"['\"](.*?)['\"]", raw_text)[0]

    # get id of ad
    ad_id = ad.url.split('ID')[1].split('.')[0]
    # shaping of the correct url with ad id and phone token
    phone_url = urljoin(settings.PHONE_URL, f'{ad_id}/?pt={token}')
    response = session.get(phone_url, headers=headers)

    if response.status_code != 200:
        logger.warning('=== Unsuccessful attempt. Empty values of phone numbers ===')
        return ad, author, []

    phone_numbers = response.json().get('value')

    logger.debug('=== Finishing to fetching landlord phone number and name ===')
    if 'span' not in phone_numbers:
        return ad, author, [phone_numbers]

    soup = BeautifulSoup(phone_numbers, 'lxml')
    phone_numbers = [item.text.strip() for item in soup.find_all('span')]
    return ad, author, phone_numbers
