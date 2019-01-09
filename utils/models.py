from datetime import datetime
from typing import List
from typing import NamedTuple


class AdModel(NamedTuple):
    external_id: str
    title: str
    price: int
    url: str
    created: datetime = None
    author_id: str = None


class NewAdModel(NamedTuple):
    title: str
    price: int
    url: str
    created: datetime
    author: str
    phones: List[str]


class LandLordModel(NamedTuple):
    external_id: str
    url: str
    name: str
    platform_created_at: datetime.date
    other_ads: int
