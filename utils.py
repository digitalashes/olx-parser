# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from urllib.parse import urlencode, urlparse, urljoin, urlunparse

from settings import config


def build_url():
    filters = urlencode({
        'search[district_id]': config.DISTRICT_ID,
        'search[filter_float_price:from]': config.MIN_PRICE,
        'search[filter_float_price:to]': config.MAX_PRICE,
        'search[filter_float_number_of_rooms:from]': config.MIN_ROOMS,
        'search[filter_float_number_of_rooms:to]': config.MAX_ROOMS,
        'search[photos]': config.WITH_PHOTOS,
        'search[order]': 'created_at:desc'
    })
    url = urlparse(
        urljoin(config.BASE_URL, '/'.join([config.CATEGORY, config.SUB_CATEGORY, config.SUB_SUB_CATEGORY, config.CITY]))
    )
    return urlunparse((url.scheme, url.netloc, url.path, None, filters, None))
