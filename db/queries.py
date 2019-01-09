from sqlite3 import Cursor as SqliteCursor
from typing import List

from config import logger
from utils.models import AdModel
from utils.models import LandLordModel
from .utils import db_cache


def get_exists_ads(db_cursor: SqliteCursor,
                   external_ids: List[str]) -> List[int]:
    logger.info('=== Fetching existing ads ===')

    result = db_cursor.execute(f"""
        select external_id
        from ads
        where external_id in ({",".join(external_ids)});
    """).fetchall()

    if result:
        result = [item[0] for item in result]
        logger.info('=== Found %s ads ===', len(result))
        return result

    logger.info('=== Existing ads not found ===')
    return result


@db_cache
def get_author_id(db_cursor: SqliteCursor,
                  external_id: str) -> int:
    logger.info('=== Trying get author with %s external id ===', external_id)

    result = db_cursor.execute("""
        select id
        from authors
        where external_id = ?;
    """, (external_id,)).fetchone()

    if result:
        result = result[0]
        logger.info('=== Found author with id - %s ===', result)
        return result

    logger.info('=== Author not found ===')
    return result


def create_author(db_cursor: SqliteCursor,
                  data: LandLordModel) -> int:
    logger.info('=== Adding a new author - %s ===', repr(data))

    db_cursor.execute("""
        insert into authors(external_id, url, name, platform_created_at, other_ads) 
        values (?,?,?,?,?);
    """, (data.external_id, data.url, data.name, data.platform_created_at, data.other_ads))
    return db_cursor.lastrowid


def create_ad(db_cursor: SqliteCursor,
              data: AdModel) -> None:
    logger.info('=== Adding a new ad - %s ===', repr(data))

    db_cursor.execute("""
    insert into ads(external_id, title, price, url, author_id, platform_created_at)
    values (?,?,?,?,?,?);
    """, (data.external_id, data.title, data.price, data.url, data.author_id, data.created))


def add_phones(db_cursor: SqliteCursor,
               author_id: int, phones: List[str]) -> None:
    logger.info('Add new phones - %s for author with id - %s ===', phones, author_id)

    for phone in phones:
        db_cursor.execute("""
            insert into phones(phone, author_id)
            select :phone, :author_id
            where not exists(select 1 from phones where author_id = :author_id and phone = :phone)
        """, {'author_id': author_id, 'phone': phone})
