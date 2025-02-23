import logging
import requests
import random

from config import Settings
from dal import save_followers, save_following
from utils import random_time, write_to_json

log = logging.getLogger(__name__)


def check_followers(settings: Settings):
    log.info('check followers vs following')
    random_time()
    get_following_list(settings)
    random_time()
    get_follower_list(settings)


def get_follower_list(settings: Settings):
    url_args = get_timeline_url('followers', settings)
    server_response = get_timeline(url=url_args[0], settings=settings)
    log.info(f'Getting current follower count: {len(server_response)}')
    save_followers(server_response)


def get_following_list(settings: Settings):
    url_args = get_timeline_url('following', settings)
    server_response = get_timeline(url=url_args[0], settings=settings)
    log.info(f'Getting current following count: {len(server_response)}')
    save_following(server_response)


def get_timeline_url(timeline_type: str, settings: Settings) -> tuple:
    timeline_base = f'{settings.base_url}{settings.api_version}timelines'
    if timeline_type == 'global':
        return (f'{timeline_base}/public?min_id=1&limit=6&_pe=1&remote=true', timeline_type)
    if timeline_type == 'notifications':
        return (f'{settings.base_url}{settings.api_version}{timeline_type}', timeline_type)
    if timeline_type == 'followers':
        return (f'{settings.base_url}{settings.api_version}accounts/{settings.account_id}/{timeline_type}', timeline_type)
    if timeline_type == 'following':
        return (f'{settings.base_url}{settings.api_version}accounts/{settings.account_id}/{timeline_type}?limit=50', timeline_type)    
    if timeline_type == 'tag':
        random.shuffle(settings.tags)
        return (f'{timeline_base}/{timeline_type}/{settings.tags[0]}', settings.tags[0])
    return (f'{timeline_base}/{timeline_type}', timeline_type)


def get_timeline(url: str, settings: Settings, timeline_type: str = 'home', limit: int = 10) -> dict:
    log.info(f'getting timeline {timeline_type} @ {url}')
    limit = 50 if 'tag' in url or timeline_type in ['followers', 'following'] else limit
    params = {
        "limit": limit,
    }
    response = requests.get(url, headers=settings.headers, params=params)
    if response.status_code == 200:
        log.info('Response successful')
        return response.json()
    else:
        log.info(f"Failed to fetch data. Status code: {response.status_code}")
        return {}
