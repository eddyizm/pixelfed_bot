import json
import requests
import time
import logging as log
from random import randrange
from logging.handlers import RotatingFileHandler

from config import Settings

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


token = settings.token
BASE_URL = 'https://pixelfed.social/'
API_VERSION = 'api/v1/'
verify_cred_endpoint = 'accounts/verify_credentials'
timeline_endpoint = f'{BASE_URL}{API_VERSION}timelines/home'
notification_endpoint = f'{BASE_URL}{API_VERSION}notifications'
headers = {
    "Authorization": f"Bearer {token}"
}


def random_time():
    '''Use this to randomize actions'''
    sleep_time = randrange(5, 60)
    log.info(f'sleeping for {sleep_time} seconds...')
    time.sleep(sleep_time)
    return sleep_time


def get_timeline(url) -> dict:
    log.info(f'getting timeline @ {url}')
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        log.info('Response successful, returning response.json')
        return response.json()
    else:
        log.info(f"Failed to fetch data. Status code: {response.status_code}")
        log.info(response.text)


def parse_timeline_for_favorites(data: list, limit: int = None) -> list:
    # filter only unfavorited status and ignore your own id.
    result = [d for d in data if d['favourited'] is False and d['account']['id'] != settings.account_id]
    log.info(f'found {len(result)} posts to favorite from list of {len(data)}')
    if limit is not None and limit > 0:
        result = result[:limit]
        log.info(f'Limited results to {limit} posts')
    return result


def fave_post(status_id):
    url = f'{BASE_URL}{API_VERSION}statuses/{status_id}/favourite'
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        log.info(f'fave id: {status_id} request successful!')
        log.debug(f'Response: {response.json()}')
    else:
        log.info(f'Request failed with status code {response.status_code}')
        log.info(f'Response: {response.text}')


def filter_notification_faves(data: list, limit: int = None) -> list:
    # and d['account']['id'] != settings.account_id
    result = [d for d in data if d['type'] == 'favourite']
    unique_account_ids = set()  # Use a set to automatically handle duplicates
    for item in result:
        if 'account' in item and 'id' in item['account']:
            unique_account_ids.add(item['account']['id'])

    # Convert the set to a list (optional, for easier handling)
    unique_account_ids = list(unique_account_ids)
    log.info(len(result))
    breakpoint()

    # write_to_json(result)

def get_status_by_id(id: str, limit: int = None):
    url = f'{BASE_URL}{API_VERSION}accounts/{id}/statuses'
    param = {'limit': str(limit)}
    response = requests.get(url, headers=headers, params=param)

def write_to_json(data):
    with open('response.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)


def read_json(data):
    with open(data, 'r') as json_file:
        return json.load(json_file)


def main():
    log.info('starting pixelfed bot')
    # endpoint = notification_endpoint if random_time() % 2 == 0 else timeline_endpoint
    # timeline_response = get_timeline(timeline_endpoint)
    # notification_response = get_timeline(notification_endpoint)
    # write_to_json(notification_response)
    data = read_json('response.json')
    filter_notification_faves(data)
    
    # unfaved = parse_timeline_for_favorites(timeline_response, limit=10)
    # for post in unfaved:
    #     random_time()
    #     fave_post(post['id'])


if __name__ == '__main__':
    main()
    log.info('closing shop...')
