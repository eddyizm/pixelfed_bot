import pytest
from unittest.mock import patch
from main import parse_timeline_for_favorites


SAMPLE_DATA = [
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


class Settings:
    account_id = 4


# TODO Move this stuff to conftest later
@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr("main.settings", Settings)


@pytest.fixture
def mock_logger():
    with patch("main.log.info") as mock_log:
        yield mock_log


def test_parse_timeline_for_favorites_no_limit(mock_settings, mock_logger):
    # Test without a limit
    result = parse_timeline_for_favorites(SAMPLE_DATA)
    assert len(result) == 2
    assert result[0]["account"]["id"] == 1
    assert result[1]["account"]["id"] == 3

    # Assert logging was called correctly
    mock_logger.assert_any_call("found 2 posts to favorite from list of 4")


def test_parse_timeline_for_favorites_with_limit(mock_settings, mock_logger):
    # Test with a limit
    result = parse_timeline_for_favorites(SAMPLE_DATA, limit=1)

    # Assert the correct number of results
    assert len(result) == 1
    assert result[0]["account"]["id"] == 1

    # Assert logging was called correctly
    mock_logger.assert_any_call("found 2 posts to favorite from list of 4")
    mock_logger.assert_any_call("Limited results to 1 posts")


def test_parse_timeline_for_favorites_all_favorited(mock_settings, mock_logger):
    # Test with all posts already favorited
    favorited_data = [
        {"favourited": True, "account": {"id": 1}},
        {"favourited": True, "account": {"id": 2}}
    ]
    result = parse_timeline_for_favorites(favorited_data)

    # Assert no results
    assert len(result) == 0
    mock_logger.assert_any_call("found 0 posts to favorite from list of 2")


def test_parse_timeline_for_favorites_empty_input(mock_settings, mock_logger):
    # Test with empty input
    result = parse_timeline_for_favorites([])

    assert len(result) == 0
    mock_logger.assert_any_call("found 0 posts to favorite from list of 0")
