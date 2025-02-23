import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime


log = logging.getLogger(__name__)


def create_tables():
    with create_connection() as cursor:
        log.info('creating followers table if not exists')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS followers (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                last_updated DATETIME
            )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS following (
            id TEXT PRIMARY KEY,
            username TEXT,
            acct TEXT,
            display_name TEXT,
            created_at TEXT,
            last_updated DATETIME default current_timestamp
        )
        ''')


@contextmanager
def create_connection():
    log.info('connecting to pixelfed.db')
    conn = sqlite3.connect('pixelfed.db')
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        conn.commit()
        conn.close()


def save_followers(server_response):
    log.info('saving followers to database')
    with create_connection() as cursor:
        for record in server_response:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT OR REPLACE INTO followers (id, username, last_updated)
            VALUES (?, ?, ?)
            ''', (record['id'], record['username'], current_time))


def save_following(server_response):
    log.info('saving following to database')
    with create_connection() as cursor:
        for record in server_response:
            cursor.execute('''
                INSERT INTO following (id, username, acct, display_name, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username = excluded.username,
                    acct = excluded.acct,
                    display_name = excluded.display_name,
                    created_at = excluded.created_at
            ''', (record['id'], record['username'], record['acct'], record['display_name'], record['created_at']))


def load_followers() -> list:
    ''' returns list of follower ids '''
    with create_connection() as cursor:
        cursor.execute('''
            select id, username from followers;
        ''')
        data = cursor.fetchall()
        return [id for id in data]
