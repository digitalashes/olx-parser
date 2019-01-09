import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from config import logger
from config import settings


def _get_landlord_url(soup: BeautifulSoup) -> str:
    return soup.select('h4 > a')[0].attrs['href']


def _get_landlord_id(landlord_url: str) -> str:
    try:
        return landlord_url.split('/')[5]
    except IndexError:
        return urlparse(landlord_url)[1].split('.')[0]
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e)
        return landlord_url


def _get_landlord_name(soup: BeautifulSoup) -> str:
    return f"{soup.find('h4').text.strip()} " \
        f"({soup.find('span', class_='user-since').text})"


def _get_landlord_created_at(soup: BeautifulSoup) -> datetime.date:
    date = soup.find('span', class_='user-since').text.split('с ')[1]
    month, year = date.split(' ')
    month = settings.MONTH_MAPPING[month]
    return datetime.date(int(year), month, 1)


def _get_landlord_other_ads_count(soup: BeautifulSoup) -> int:
    return len(soup.select('td.offer'))
