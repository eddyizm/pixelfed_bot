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
    log.info('saving followers')
    with create_connection() as cursor:
        for record in server_response:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT OR REPLACE INTO followers (id, username, last_updated)
            VALUES (?, ?, ?)
            ''', (record['id'], record['username'], current_time))


def load_followers() -> list:
    ''' returns list of follower ids '''
    with create_connection() as cursor:
        cursor.execute('''
            select id, username from followers;
        ''')
        data = cursor.fetchall()
        return [id for id in data]
