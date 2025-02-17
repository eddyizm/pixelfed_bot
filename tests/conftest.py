import pytest
from unittest.mock import patch
from main import settings  # Import settings from main
from config import Settings  # Import Settings from config


@pytest.fixture
def mock_settings(monkeypatch):
    # Create a mock Settings object
    mock_settings = Settings()
    # Add the mock values
    mock_settings.headers = {"Authorization": "Bearer mock_token"}
    mock_settings.account_id = 4
    mock_settings.base_url = "https://example.com/"
    mock_settings.api_version = "v1/"
    mock_settings.tags = ["tag1", "tag2", "tag3"]
    # Patch the `settings` object in the `main` module
    monkeypatch.setattr("main.settings", mock_settings)
    return mock_settings  # Return the mock_settings object


# Mock the `headers` attribute within `settings`
@pytest.fixture
def mock_headers(mock_settings):
    with patch.object(settings, "headers", mock_settings.headers) as mock_header:
        yield mock_header


@pytest.fixture
def mock_logger():
    with patch("main.log.info") as mock_log:
        yield mock_log


@pytest.fixture
def parse_timeline_for_favorites_sample_data():
    yield [
        {
            "favourited": False,
            "account": {"id": 1, "username": "user1"}
        },
        {
            "favourited": True,
            "account": {"id": 2, "username": "user2"}
        },
        {
            "favourited": False,
            "account": {"id": 3, "username": "user3"}
        },
        {
            "favourited": False,
            "account": {"id": 4, "username": "your_username"}  # This should be ignored (your own account)
        }
    ]


@pytest.fixture
def notification_sample_data():
    yield [
        {'type': 'favourite', 'account': {'id': 1, 'name': 'user1'}},
        {'type': 'favourite', 'account': {'id': 2, 'name': 'user2'}},
        {'type': 'reblog', 'account': {'id': 3, 'name': 'user3'}},
        {'type': 'favourite', 'account': {'id': 1, 'name': 'user1'}},  # Duplicate account id
        {'type': 'favourite', 'account': {'id': 4, 'name': 'user4'}},
        {'type': 'favourite', 'account': {'id': 5, 'name': 'user5'}},
        {'type': 'favourite', 'account': {'id': 6, 'name': 'user6'}},
        {'type': 'favourite', 'account': {'id': 7, 'name': 'user7'}},
        {'type': 'favourite', 'account': {'id': 8, 'name': 'user8'}},
        {'type': 'favourite', 'account': {'id': 9, 'name': 'user9'}},
        {'type': 'favourite', 'account': {'id': 10, 'name': 'user10'}},
    ]
