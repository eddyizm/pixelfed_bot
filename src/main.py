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

# TODO get notifications:
# curl https://pixelfed.social/api/v1/notifications \
#   -H "Authorization: Bearer {token}"

token = settings.token
BASE_URL = 'https://pixelfed.social/'
API_VERSION = 'api/v1/'
verify_cred_endpoint = 'accounts/verify_credentials'
timeline_endpoint = f'{BASE_URL}{API_VERSION}timelines/home'
headers = {
    "Authorization": f"Bearer {token}"
}


def random_time():
    '''Use this to randomize actions'''
    sleep_time = randrange(5, 60)
    log.info(f'sleeping for {sleep_time} seconds...')
    return time.sleep(sleep_time)


def get_timeline(url) -> dict:
    log.info(f'getting timeline @ {url}')
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        log.info('Response successful, returning response.json')
        return response.json()
    else:
        log.info(f"Failed to fetch data. Status code: {response.status_code}")
        log.info(response.text)


def parse_timeline_for_favorites(data: list) -> list:
    # filter only unfavorited status and ignore your own id.
    result = [d for d in data if d['favourited'] is False and d['account']['id'] != settings.account_id]
    log.info(f'found {len(result)} posts to favorite from list of {len(data)}')
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


def main():
    log.info('starting pixelfed bot')
    timeline_response = get_timeline(timeline_endpoint)
    unfaved = parse_timeline_for_favorites(timeline_response)
    for post in unfaved:
        random_time()
        fave_post(post['id'])


if __name__ == '__main__':
    main()
    log.info('closing shop...')
