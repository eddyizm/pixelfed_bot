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
