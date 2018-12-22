from datetime import datetime
from typing import NamedTuple, List
from urllib.parse import urlencode
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

from config import settings


class Ad(NamedTuple):
    id: int
    title: str
    price: int
    is_fresh: bool
    url: str
    name: str = None
    phones: List[str] = None
    posted_at: datetime = None


def build_url() -> str:
    filters = urlencode({
        'search[district_id]': settings.DISTRICT_ID,
        'search[filter_float_price:from]': settings.MIN_PRICE,
        'search[filter_float_price:to]': settings.MAX_PRICE,
        'search[filter_float_number_of_rooms:from]': settings.MIN_ROOMS,
        'search[filter_float_number_of_rooms:to]': settings.MAX_ROOMS,
        'search[photos]': settings.WITH_PHOTOS,
        'search[order]': 'created_at:desc'
    })
    url = urlparse(
        urljoin(settings.BASE_URL, '/'.join([settings.CATEGORY,
                                             settings.SUB_CATEGORY,
                                             settings.SUB_SUB_CATEGORY,
                                             settings.CITY]))
    )
    return urlunparse((url.scheme, url.netloc, url.path, None, filters, None))
