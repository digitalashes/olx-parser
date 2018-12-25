from datetime import datetime
from typing import List
from typing import NamedTuple


class Ad(NamedTuple):
    id: int
    title: str
    price: int
    is_fresh: bool
    url: str
    name: str = None
    phones: List[str] = None
    posted_at: datetime = None
