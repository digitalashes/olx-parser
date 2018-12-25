from config import logger

sql = """
pragma foreign_keys = on;

create table if not exists authors
(
  id                  integer primary key autoincrement,
  internal_id         text     not null,
  url                 text     not null,
  name                text     not null,
  platform_created_at datetime not null default current_date,
  other_ads           integer           default 0
);

create unique index if not exists authors_id_uindex
  on authors (id);
create unique index if not exists authors_internal_id_uindex
  on authors (internal_id);
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
  id          integer primary key autoincrement,
  internal_id text     not null,
  title       text     not null,
  price       real     not null,
  url         text     not null,
  author_id   integer  not null,
  created     datetime not null default current_date,

  foreign key (author_id) references authors (id)
);

create unique index if not exists ads_id_uindex
  on ads (id);
create unique index if not exists ads_internal_id_uindex
  on ads (internal_id);
create index if not exists ads_author_id_index
  on ads (author_id);
create index if not exists ads_created_index
  on ads (created);"""


def check_db(db_connect, db_cursor):
    logger.info('--- Check database tables ---')
    db_cursor.executescript(sql)
    db_connect.commit()
