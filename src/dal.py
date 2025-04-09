import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from models import RelationshipStatus, Account, map_account

log = logging.getLogger(__name__)


def create_tables():
    with create_connection() as cursor:
        log.info('creating tables if not exists')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ignore_account (
                id TEXT PRIMARY KEY,
                last_updated DATETIME default current_timestamp
            )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS account (
            id TEXT PRIMARY KEY,
            username TEXT,
            acct TEXT,
            display_name TEXT,
            followers_count INTEGER,
            following_count INTEGER,
            statuses_count INTEGER,
            created_at DATETIME default current_timestamp,
            last_updated DATETIME
        )
        ''')
        # cursor.execute('''
        # CREATE TABLE IF NOT EXISTS following (
        #     id TEXT PRIMARY KEY,
        #     username TEXT,
        #     acct TEXT,
        #     display_name TEXT,
        #     followers_count INTEGER,
        #     following_count INTEGER,
        #     statuses_count INTEGER,
        #     created_at DATETIME default current_timestamp,
        #     last_updated DATETIME
        # )
        # ''')
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            following INTEGER NOT NULL,
            followed_by INTEGER NOT NULL,
            blocking INTEGER NOT NULL,
            muting INTEGER NOT NULL,
            muting_notifications INTEGER,
            requested INTEGER NOT NULL,
            domain_blocking INTEGER,
            showing_reblogs INTEGER,
            endorsed INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)


@contextmanager
def create_connection():
    conn = sqlite3.connect('pixelfed.db')
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.commit()
        conn.close()


def count_todays_records() -> int:
    """Count how many records were created in the following table today"""
    with create_connection() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM relationships r
            WHERE r."following" = 1 AND
            DATE(created_at) = DATE('now')
        """)
        count = cursor.fetchone()[0]
    return count


def save_relationship(relationship: RelationshipStatus):
    log.info(f'Saving relationship record {relationship.id}')
    with create_connection() as cursor:
        cursor.execute("""
        INSERT OR REPLACE INTO relationships (
            id, following, followed_by, blocking, muting,
            muting_notifications, requested, domain_blocking,
            showing_reblogs, endorsed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            relationship.id,
            int(relationship.following),
            int(relationship.followed_by),
            int(relationship.blocking),
            int(relationship.muting),
            int(relationship.muting_notifications) if relationship.muting_notifications is not None else None,
            int(relationship.requested),
            int(relationship.domain_blocking) if relationship.domain_blocking is not None else None,
            int(relationship.showing_reblogs) if relationship.showing_reblogs is not None else None,
            int(relationship.endorsed)
        ))


def get_relationship(relationship_id: str) -> RelationshipStatus:
    """
    Retrieve a relationship record from the database by ID.
    Args:
        relationship_id: The ID of the relationship to retrieve
    Returns:
        RelationshipStatus object if found, None if not found
    """
    log.info(f'Retrieving relationship record {relationship_id}')
    with create_connection() as cursor:
        cursor.execute("""
        SELECT
            id, following, followed_by, blocking, muting, 
            muting_notifications, requested, domain_blocking, 
            showing_reblogs, endorsed
        FROM relationships
        WHERE id = ?
        """, (relationship_id,))
        row = cursor.fetchone()
        if not row:
            return None

        return RelationshipStatus(
            id=row[0],
            following=bool(row[1]),
            followed_by=bool(row[2]),
            blocking=bool(row[3]),
            muting=bool(row[4]),
            muting_notifications=bool(row[5]) if row[5] is not None else None,
            requested=bool(row[6]),
            domain_blocking=bool(row[7]) if row[7] is not None else None,
            showing_reblogs=bool(row[8]) if row[8] is not None else None,
            endorsed=bool(row[9])
        )


def migrate():
    log.info('migrating db to new versions')
    with create_connection() as cursor:
        log.info('inserting following to new account table')
        cursor.execute('''
            INSERT OR REPLACE INTO account
            (id, username, acct, display_name, followers_count, following_count, created_at, last_updated)
            SELECT id, username, acct, display_name, followers_count, following_count, created_at, last_updated
            FROM FOLLOWING;
        ''')
        log.info(f'successfully inserted {cursor.rowcount} records')
        log.info('inserting followers to new account table')
        cursor.execute('''
            INSERT OR REPLACE INTO account
            (id, username, acct, display_name, followers_count, following_count, created_at, last_updated)
            SELECT id, username, '', '', 0, 0, last_updated , last_updated FROM followers;
        ''')
        log.info(f'successfully inserted {cursor.rowcount} records')
        log.info('inserting following to relationship table')
        cursor.execute('''
            INSERT OR REPLACE INTO relationships
            (id, "following", followed_by, blocking, muting, muting_notifications, requested, domain_blocking, showing_reblogs, endorsed, created_at)
            SELECT id, 1, 0, 0, 0, 0, 0, 0, 0, 0, last_updated FROM following f
        ''')
        log.info('inserting followers to relationship table')
        cursor.execute('''
            INSERT OR REPLACE INTO relationships
            (id, "following", followed_by, blocking, muting, muting_notifications, requested, domain_blocking, showing_reblogs, endorsed, created_at)
            SELECT id, 0, 1, 0, 0, 0, 0, 0, 0, 0, last_updated FROM followers f
        ''')
        log.info(f'successfully inserted {cursor.rowcount} records')


def ignore_user(id: str) -> bool:
    with create_connection() as cursor:
        cursor.execute("""
            select id from ignore_account where id = ?
            """, (id,))
        return cursor.rowcount > 0


def add_to_ignore(id: str):
    with create_connection() as cursor:
        cursor.execute("""
            INSERT INTO ignore_account ( id ) VALUES (?)
            """, (id,))
        log.info(f'added {id} to ignore_account successfully!')


def save_following(json_data: dict):
    log.info('saving account')
    account = map_account(json_data)
    with create_connection() as cursor:
        cursor.execute("""
        INSERT INTO account (
            id, username, acct, display_name,
            followers_count, following_count, statuses_count,
            created_at, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account.id,
            account.username,
            account.acct,
            account.display_name,
            account.followers_count,
            account.following_count,
            account.statuses_count,
            account.created_at,
            account.last_updated
        ))
        log.info(f'Inserted {account.id}|{account.username} successfully!')


def load_followers() -> list:
    ''' returns list of follower ids '''
    with create_connection() as cursor:
        cursor.execute('''
            SELECT id FROM relationships r WHERE followed_by = 1;
        ''')
        data = cursor.fetchall()
        return [id for id in data]
