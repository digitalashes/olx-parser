from functools import partial
from functools import wraps
from typing import Callable

from config import logger

sql = """

pragma foreign_keys = on;

create table if not exists authors
(
  id                  integer primary key autoincrement,
  external_id         text     not null,
  url                 text     not null,
  name                text     not null,
  platform_created_at date     not null default current_date,
  other_ads           integer  not null default 0
);

create unique index if not exists authors_id_uindex
  on authors (id);
create unique index if not exists authors_external_id_uindex
  on authors (external_id);
create index if not exists authors_platform_created_at_index
  on authors (platform_created_at);

create table if not exists phones
(
  id        integer primary key autoincrement,
  phone     text    not null,
  author_id integer not null,

  foreign key (author_id) references authors (id)
);

create unique index if not exists phones_id_uindex
  on phones (id);
create index if not exists phones_phone_index
  on phones (phone);
create index if not exists phones_author_id_index
  on phones (author_id);

create table if not exists ads
(
  id                  integer primary key autoincrement,
  external_id         text      not null,
  title               text      not null,
  price               real      not null,
  url                 text      not null,
  author_id           integer   not null,
  platform_created_at timestamp not null default current_timestamp,

  foreign key (author_id) references authors (id)
);

create unique index if not exists ads_id_uindex
  on ads (id);
create unique index if not exists ads_external_id_uindex
  on ads (external_id);
create index if not exists ads_author_id_index
  on ads (author_id);
create index if not exists ads_platform_created_at_index
  on ads (platform_created_at);

"""


def check_db(db_connect, db_cursor) -> None:
    logger.info('=== Check database tables ===')

    db_cursor.executescript(sql)
    db_connect.commit()


def db_cache(func: Callable = None) -> Callable:
    _cache = {}

    if func is None:
        return partial(db_cache)

    @wraps(func)
    def __wrapper(*args, **kwargs):
        *_, _external_id = args
        _id = _cache.get(_external_id)
        if _id is None:
            _id = func(*args, **kwargs)
            if _id is not None:
                _cache[_external_id] = _id
        return _id

    return __wrapper
