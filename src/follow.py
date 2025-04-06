import logging
import random

from config import Settings
from dal import count_todays_records, load_followers, save_followers, save_following, save_relationship
from models import RelationshipStatus
from timelines import get_timeline_url, get_timeline, post_timeline
from utils import random_time


log = logging.getLogger(__name__)


def get_random_followers() -> list:
    followers = load_followers()
    log.info(f'follower count {len(followers)}')
    log.info('getting random follower list. ')
    random.shuffle(followers)
    return followers[:10]


def follow_user(id: str, settings: Settings, server_response):
    relationship = get_relationship(settings, id)
    if relationship.following:
        log.info('already following user..')
        return
    url_args = get_timeline_url('follow', settings, id)
    log.info(f'following user id: {id}')
    response = post_timeline(url_args[0], settings, url_args[1])
    log.info(f'response.text{response.text}')
    if response.status_code == 200:
        log.info('posted successfully')
        save_following(server_response[0]['account'])
    return response


def check_follow_count(settings: Settings) -> bool:
    todays_follow_count = count_todays_records()
    log.info(f'today\'s follow count: {todays_follow_count}')
    return settings.follows_per_day > todays_follow_count


# def process_follows(url_args: tuple, like_count: int = 0) -> int:
#     server_response = get_timeline(url=url_args[0], settings=settings, timeline_type=url_args[1])
#     breakpoint()
#     id_list = filter_notification_follows(server_response)
#     for id in id_list:
#         server_response = get_status_by_id(id, limit=6)
#         random_time()
#         result = check_relationship(settings, id)
#     return like_count


# def check_followers(settings: Settings):
#     log.info('check followers vs following')
#     random_time()
#     get_following_list(settings)
#     random_time()
#     get_follower_list(settings)


def get_relationship(settings: Settings, id: str):
    url_args = get_timeline_url('relationships', settings, id)
    random_time()
    server_response = get_timeline(url=url_args[0], settings=settings)
    relationship = RelationshipStatus(**server_response[0])
    save_relationship(relationship)
    return relationship


def get_follower_list(settings: Settings):
    url_args = get_timeline_url('followers', settings)
    server_response = get_timeline(url=url_args[0], settings=settings)
    log.info(f'Getting current follower count: {len(server_response)}')
    save_followers(server_response)
    # write_to_json(server_response, 'followers')


def get_following_list(settings: Settings):
    url_args = get_timeline_url('following', settings)
    server_response = get_timeline(url=url_args[0], settings=settings)
    log.info(f'Getting current following count: {len(server_response)}')
    save_following(server_response)
    # write_to_json(server_response, 'following')
