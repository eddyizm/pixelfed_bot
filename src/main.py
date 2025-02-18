import argparse
import random
import requests
import logging as log
from logging.handlers import RotatingFileHandler

from config import Settings, PixelFedBotException
from dal import create_tables, load_followers
from timelines import get_timeline_url, get_timeline
from utils import random_time

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


timeline_types = ['home', 'public', 'notifications', 'global', 'tag']
verify_cred_endpoint = 'accounts/verify_credentials'


def parse_timeline_for_favorites(data: list, limit: int = None) -> list:
    # filter only unfavorited status and ignore your own id.
    result = [d for d in data if not d['favourited'] and d['account']['id'] != settings.account_id]
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
    url = f'{settings.base_url}{settings.api_version}statuses/{status_id}/favourite'
    response = requests.post(url, headers=settings.headers)

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


def get_status_by_id(id: str, limit: int = 6, follower: str = None) -> dict:
    url = f'{settings.base_url}{settings.api_version}accounts/{id}/statuses'
    param = {'limit': str(limit)}
    log.info(f'getting timeline {follower or id} @ {url}')
    response = requests.get(url, headers=settings.headers, params=param)
    return response.json()


def fave_unfaved(server_response: dict, limit: int = 6):
    unfaved = parse_timeline_for_favorites(server_response, limit=limit)
    liked_count = 0
    for post in unfaved:
        random_time()
        liked_count = liked_count + fave_post(post['id'])
    return liked_count


def is_like_per_session_fulfilled(like_count: int) -> bool:
    return like_count >= settings.likes_per_session


def process_notification_timeline(url_args: tuple, like_count: int = 0) -> int:
    server_response = get_timeline(url=url_args[0], settings=settings, timeline_type=url_args[1])
    id_list = filter_notification_faves(server_response)
    for id in id_list:
        server_response = get_status_by_id(id, limit=6)
        random_time()
        like_count += fave_unfaved(server_response)
        if is_like_per_session_fulfilled(like_count):
            return like_count
    return like_count


def process_timeline(url_args: tuple) -> int:
    server_response = get_timeline(url=url_args[0], settings=settings, timeline_type=url_args[1])
    return fave_unfaved(server_response, limit=settings.likes_per_session)


def process_follower_timeline() -> int:
    log.info('Getting follower for timeline processing')
    followers = get_random_followers()
    server_response = get_status_by_id(followers[0][0], limit=5, follower=followers[0][1])
    random_time()
    return fave_unfaved(server_response, limit=settings.likes_per_session)


def handle_timeline(url_args: tuple, like_count: int = 0):
    match url_args[1]:
        case 'notifications':
            return process_notification_timeline(url_args, like_count)
        case _:
            return process_timeline(url_args)


def main():
    try:
        parser = argparse.ArgumentParser(
            description='Get home, public, notification timelines and like posts.',
            epilog='the pixels go on and on...',
            prog='Pixelfed Bot'
        )
        parser.add_argument('-t', '--timeline_type', type=str, choices=(timeline_types), help="timeline type", required=True)
        parser.add_argument('-l', '--limit', type=int, help="override session like limit", required=False)
        parser.add_argument('--version', action='version', version='%(prog)s 0.4')
        args = parser.parse_args()
        log.info('starting pixelfed bot')
        create_tables()
        settings.likes_per_session = args.limit or settings.likes_per_session
        url_args = get_timeline_url(args.timeline_type, settings)
        like_count = handle_timeline(url_args)
        log.info(f'first pass count: {like_count}')
        while not is_like_per_session_fulfilled(like_count):
            log.info(f'Like count: {like_count}, per session value: {settings.likes_per_session}')
            random_time()
            new_likes = process_follower_timeline()
            like_count += new_likes
            log.info(f'Liked {new_likes} posts from follower timeline. Total likes: {like_count}')
            if is_like_per_session_fulfilled(like_count):
                break
            random.shuffle(timeline_types)
            new_likes = handle_timeline(get_timeline_url(timeline_types[0], settings), like_count)
            like_count += new_likes
            log.info(f'Liked {new_likes} posts from {timeline_types[0]} timeline. Total likes: {like_count}')
            # TODO add following list
            log.info(f'Reached total like count: {like_count} exceeding {settings.likes_per_session}')
    except PixelFedBotException as ex:
        log.error(ex, exc_info=True)


if __name__ == '__main__':
    main()
    log.info('closing shop...')
