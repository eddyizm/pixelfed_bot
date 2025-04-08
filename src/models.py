from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RelationshipStatus:
    id: str
    following: bool
    followed_by: bool
    blocking: bool
    muting: bool
    muting_notifications: Optional[bool]
    requested: bool
    domain_blocking: Optional[bool]
    showing_reblogs: Optional[bool]
    endorsed: bool


@dataclass
class Account:
    id: str
    username: str
    display_name: str
    created_at: datetime
    acct: Optional[str] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    statuses_count: Optional[int] = None
    last_updated: Optional[datetime] = None


def map_account(account_response) -> Account:
    try:
        account = Account(
            id=account_response['id'],
            username=account_response['username'],
            acct=account_response['acct'],
            display_name=account_response['display_name'],
            followers_count=account_response['followers_count'],
            following_count=account_response['following_count'],
            statuses_count=account_response['statuses_count'],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
    except Exception:
        account = {}
    finally:
        return account
