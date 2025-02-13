import argparse
import json
import random
import requests
import time
import logging as log
from random import randrange
from logging.handlers import RotatingFileHandler

from config import Settings
from dal import create_tables, load_followers

settings = Settings()
handlers = [
    log.StreamHandler(),
    RotatingFileHandler(
        settings.app_log,
        mode='a', maxBytes=5 * 1024 * 1024,
        backupCount=5, encoding=None, delay=0
    )
]
log.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s', handlers=handlers, level=log.INFO)


timeline_types = ['home', 'public', 'notifications']
token = settings.token
BASE_URL = 'https://pixelfed.social/'
API_VERSION = 'api/v1/'
verify_cred_endpoint = 'accounts/verify_credentials'
headers = {
    "Authorization": f"Bearer {token}"
}


def random_time():
    '''Use this to randomize actions'''
    sleep_time = randrange(5, 120)
    log.info(f'sleeping for {sleep_time} seconds...')
    time.sleep(sleep_time)
    return sleep_time


def get_timeline(url: str, timeline_type: str = 'home', limit: int = 10) -> dict:
    log.info(f'getting timeline {timeline_type} @ {url}')
    params = {
        "min_id": 1,
        "limit": limit,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        log.info('Response successful')
        return response.json()
    else:
        log.info(f"Failed to fetch data. Status code: {response.status_code}")
        return {}


def parse_timeline_for_favorites(data: list, limit: int = None) -> list:
    # filter only unfavorited status and ignore your own id.
    result = [d for d in data if d['favourited'] is False and d['account']['id'] != settings.account_id]
    if not result:
        log.info(f'No posts found: {len(result)}')
        return []
    log.info(f'found {len(result)} posts to favorite from list of {len(data)}')
    if limit is not None and limit > 0:
        result = result[:limit]
        log.info(f'Limiting results to {limit} posts')
    return result


def get_random_followers() -> list:
    followers = load_followers()
    log.info(f'follower count {len(followers)}')
    log.info('getting random follower list. ')
    random.shuffle(followers)
    return followers[:10]


def fave_post(status_id) -> int:
    url = f'{BASE_URL}{API_VERSION}statuses/{status_id}/favourite'
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        log.info(f'fave id: {status_id} request successful!')
        log.debug(f'Response: {response.json()}')
        return 1
    else:
        log.info(f'Request failed with status code {response.status_code}')
        return 0


def filter_notification_faves(data: list, limit: int = 5) -> list:
    if limit < 1:
        return []
    faves = [d for d in data if d['type'] == 'favourite']
    unique_account_ids = set()
    for item in faves:
        if 'account' in item and 'id' in item['account']:
            unique_account_ids.add(item['account']['id'])

    return list(unique_account_ids)[:limit]


def get_status_by_id(id: str, limit: int = 6) -> dict:
    url = f'{BASE_URL}{API_VERSION}accounts/{id}/statuses'
    param = {'limit': str(limit)}
    log.info(f'getting timeline {id} @ {url}')
    response = requests.get(url, headers=headers, params=param)
    return response.json()


def fave_unfaved(server_response: dict, limit: int = 6):
    unfaved = parse_timeline_for_favorites(server_response, limit=limit)
    liked_count = 0
    for post in unfaved:
        random_time()
        liked_count = liked_count + fave_post(post['id'])
    return liked_count


def write_to_json(data):
    with open('response.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)


def read_json(data):
    with open(data, 'r') as json_file:
        return json.load(json_file)


def get_timeline_url(timeline_type: str) -> tuple:
    timeline_base = f'{BASE_URL}{API_VERSION}timelines'
    if timeline_type == 'notifications':
        return (f'{BASE_URL}{API_VERSION}{timeline_type}', timeline_type)
    if timeline_type == 'followers':
        return (f'{BASE_URL}{API_VERSION}accounts/{settings.account_id}/{timeline_type}?limit=50', timeline_type)
    return (f'{timeline_base}/{timeline_type}', timeline_type)


def process_notification_timeline(url_args: tuple) -> int:
    server_response = get_timeline(url=url_args[0], timeline_type=url_args[1])
    id_list = filter_notification_faves(server_response)
    count = 0
    for id in id_list:
        server_response = get_status_by_id(id, limit=3)
        random_time()
        count = count + fave_unfaved(server_response)
    return count


def process_home_timeline(url_args: tuple) -> int:
    server_response = get_timeline(url=url_args[0], timeline_type=url_args[1])
    return fave_unfaved(server_response, limit=10)


def process_public_timeline(url_args: tuple) -> int:
    server_response = get_timeline(url=url_args[0], timeline_type=url_args[1])
    return fave_unfaved(server_response, limit=10)


def process_follower_timeline() -> int:
    followers = get_random_followers()
    server_response = get_status_by_id(followers[0], limit=5)
    random_time()
    return fave_unfaved(server_response, limit=10)


def handle_timeline(url_args: tuple):
    match url_args[1]:
        case 'home':
            return process_home_timeline(url_args)
        case 'public':
            return process_public_timeline(url_args)
        case 'notifications':
            return process_notification_timeline(url_args)


def main():
    parser = argparse.ArgumentParser(
        description='Get home, public, notification timelines and like posts.',
        epilog='the pixels go on and on...',
        prog='Pixelfed Bot'
    )
    parser.add_argument('-t', '--timeline_type', type=str, choices=(timeline_types), help="timeline type", required=True)
    parser.add_argument('--version', action='version', version='%(prog)s 0.4')
    args = parser.parse_args()
    log.info('starting pixelfed bot')
    create_tables()
    url_args = get_timeline_url(args.timeline_type)
    like_count = handle_timeline(url_args)
    log.info(f'total like count: {like_count}')
    while settings.likes_per_session >= like_count:
        like_count = like_count + process_follower_timeline()
        # TODO add other options like notifications, public, and following list
    log.info(f'Reached total like count: {like_count} exceeding {settings.likes_per_session}')


if __name__ == '__main__':
    main()
    log.info('closing shop...')
