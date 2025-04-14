import logging
import random

from config import Settings
from dal import (
    add_to_ignore,
    count_todays_records,
    ignore_user,
    get_relationship_record,
    load_followers,
    save_following,
    save_relationship
)
from models import RelationshipStatus, Account, map_account
from timelines import get_timeline_url, get_timeline, post_timeline
from utils import random_time


log = logging.getLogger(__name__)


def get_random_followers() -> list:
    log.info('getting random follower list. ')
    followers = load_followers()
    log.info(f'follower count {len(followers)}')
    random.shuffle(followers)
    return followers[:10]


def get_account_details(id: str, settings: Settings):
    url_args = get_timeline_url('account', settings, id)
    account_response = get_timeline(url_args[0], settings, url_args[1])
    account = map_account(account_response)
    return account


def unfollow_user(id: str, settings: Settings):
    url_args = get_timeline_url('unfollow', settings, id)
    log.info(f'unfollowing user id: {id}')
    response = post_timeline(url_args[0], settings, url_args[1])
    log.info(f'response.status_code: {response.status_code}')
    if response.status_code == 200:
        relationship = RelationshipStatus(**response.json())
        log.info('unfollowed successfully')
        save_relationship(relationship)
        add_to_ignore(relationship.id)


def follow_user(id: str, settings: Settings, server_response):
    relationship = get_relationship(settings, id)
    if relationship.following:
        log.info('already following user..')
        return
    if ignore_user(id):
        log.info('Account id found in ignore table, keep calm and carry on...')
        return
    account = get_account_details(id, settings)
    # TODO save account and check here
    # TODO move check logic to function
    log.info(f'Follower count: {account.followers_count} Following count: {account.following_count}')
    log.info(f'settings.follower_count_min: {settings.follower_count_min} account.following_count: {account.following_count}')
    if account.followers_count > settings.follower_count_min:
        log.info(f'account.followers_count: {account.followers_count} too low, skipping.')
        return
    if account.following_count > settings.following_count_max:
        log.info(f'account.following_count: {account.following_count} too high, skipping.')
        return
    url_args = get_timeline_url('follow', settings, id)
    log.info(f'following user id: {id}')
    response = post_timeline(url_args[0], settings, url_args[1])
    log.info(f'response.status_code: {response.status_code}')
    if response.status_code == 200:
        log.info('posted successfully')
        save_following(server_response[0]['account'])
    return response


def check_follow_count(settings: Settings) -> bool:
    todays_follow_count = count_todays_records()
    log.info(f'follow users? {settings.follows_per_day > todays_follow_count}')
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
    relationship = get_relationship_record(id)
    if relationship:
        return relationship
    url_args = get_timeline_url('relationships', settings, id)
    random_time()
    server_response = get_timeline(url=url_args[0], settings=settings, timeline_type='relationship')
    log.info(f'getting server response from id: {server_response}')
    relationship = RelationshipStatus(**server_response[0])
    save_relationship(relationship)
    return relationship


def get_follower_list(settings: Settings):
    url_args = get_timeline_url('followers', settings)
    server_response = get_timeline(url=url_args[0], settings=settings)
    log.info(f'Getting current follower count: {len(server_response)}')
    # save_followers(server_response)


def get_following_list(settings: Settings):
    url_args = get_timeline_url('following', settings)
    server_response = get_timeline(url=url_args[0], settings=settings)
    log.info(f'Getting current following count: {len(server_response)}')
    save_following(server_response)
