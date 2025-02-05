import pytest
import requests
from unittest.mock import patch, Mock
from main import (
    parse_timeline_for_favorites,
    get_timeline,
    filter_notification_faves,
    read_json,
    get_status_by_id
)


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


@pytest.fixture
def mock_headers():
    with patch('main.headers') as mock_header:
        yield mock_header


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


def test_filter_notification_faves_basic(notification_sample_data):
    result = filter_notification_faves(notification_sample_data)
    assert result == [1, 2, 4, 5, 6]  # First 5 unique account ids


def test_filter_notification_faves_limit(notification_sample_data):
    result = filter_notification_faves(notification_sample_data, limit=3)
    assert result == [1, 2, 4]  # First 3 unique account ids


def test_filter_notification_faves_no_faves():
    data = [{'type': 'reblog', 'account': {'id': 3, 'name': 'user3'}}]
    result = filter_notification_faves(data)
    assert result == []  # No favourites in the data


def test_filter_notification_faves_empty_data():
    result = filter_notification_faves([])
    assert result == []  # Empty input list


def test_filter_notification_faves_missing_account():
    data = [{'type': 'favourite'}]  # Missing 'account' key
    result = filter_notification_faves(data)
    assert result == []  # No account information


def test_filter_notification_faves_missing_account_id():
    data = [{'type': 'favourite', 'account': {'name': 'user1'}}]  # Missing 'id' key
    result = filter_notification_faves(data)
    assert result == []  # No account id


def test_filter_notification_faves_all_duplicates():
    data = [
        {'type': 'favourite', 'account': {'id': 1, 'name': 'user1'}},
        {'type': 'favourite', 'account': {'id': 1, 'name': 'user1'}},
        {'type': 'favourite', 'account': {'id': 1, 'name': 'user1'}},
    ]
    result = filter_notification_faves(data)
    assert result == [1]  # Only one unique account id


def test_filter_notification_faves_limit_exceeds_unique_ids(notification_sample_data):
    result = filter_notification_faves(notification_sample_data, limit=20)
    assert len(result) == 9  # Only 9 unique account ids exist


def test_filter_notification_faves_limit_zero(notification_sample_data):
    result = filter_notification_faves(notification_sample_data, limit=0)
    assert result == []  # Limit is zero, so no results should be returned


def test_filter_notification_faves_negative_limit(notification_sample_data):
    result = filter_notification_faves(notification_sample_data, limit=-1)
    assert result == []  # Negative limit, should return empty list


def test_parse_timeline_for_favorites_no_limit(mock_settings, parse_timeline_for_favorites_sample_data, mock_logger):
    # Test without a limit
    result = parse_timeline_for_favorites(parse_timeline_for_favorites_sample_data)
    assert len(result) == 2
    assert result[0]["account"]["id"] == 1
    assert result[1]["account"]["id"] == 3

    # Assert logging was called correctly
    mock_logger.assert_any_call("found 2 posts to favorite from list of 4")


def test_parse_timeline_for_favorites_with_limit(mock_settings, parse_timeline_for_favorites_sample_data, mock_logger):
    # Test with a limit
    result = parse_timeline_for_favorites(parse_timeline_for_favorites_sample_data, limit=1)

    # Assert the correct number of results
    assert len(result) == 1
    assert result[0]["account"]["id"] == 1

    # Assert logging was called correctly
    mock_logger.assert_any_call("found 2 posts to favorite from list of 4")
    mock_logger.assert_any_call("Limiting results to 1 posts")


def test_parse_timeline_for_favorites_all_favorited(mock_settings, mock_logger):
    # Test with all posts already favorited
    favorited_data = [
        {"favourited": True, "account": {"id": 1}},
        {"favourited": True, "account": {"id": 2}}
    ]
    result = parse_timeline_for_favorites(favorited_data)

    # Assert no results
    assert len(result) == 0
    mock_logger.assert_any_call("No posts found: 0")


def test_parse_timeline_for_favorites_empty_input(mock_settings, mock_logger):
    # Test with empty input
    result = parse_timeline_for_favorites([])

    assert len(result) == 0
    mock_logger.assert_any_call("No posts found: 0")


def test_get_timeline_success(mocker, mock_settings, mock_logger, mock_headers):
    """
    Test that the function returns the correct JSON response when the request is successful.
    """
    # Mock the requests.get call
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "timeline_data"}
    mocker.patch("requests.get", return_value=mock_response)
    # Call the function
    url = "https://example.com/api/timeline"
    result = get_timeline(url)

    # Assertions
    assert result == {"data": "timeline_data"}
    requests.get.assert_called_once_with(
        url,
        headers=mock_headers,
        params={"min_id": 1, "limit": 10}
    )


def test_get_timeline_failure(mocker, mock_settings, mock_logger, mock_headers):
    """
    Test that the function returns an empty dictionary when the request fails.
    """
    # Mock the requests.get call to simulate a failure
    mock_response = Mock()
    mock_response.status_code = 404
    mocker.patch("requests.get", return_value=mock_response)
    # headers = mock_headers
    # Call the function
    url = "https://example.com/api/timeline"
    result = get_timeline(url)

    # Assertions
    assert result == {}
    requests.get.assert_called_once_with(
        url,
        headers=mock_headers,
        params={"min_id": 1, "limit": 10}
    )


def test_get_timeline_custom_limit(mocker, mock_settings, mock_logger, mock_headers):
    """
    Test that the function respects the custom limit parameter.
    """
    # Mock the requests.get call
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "timeline_data"}
    mocker.patch("requests.get", return_value=mock_response)

    # Call the function with a custom limit
    url = "https://example.com/api/timeline"
    result = get_timeline(url, limit=5)

    # Assertions
    assert result == {"data": "timeline_data"}
    requests.get.assert_called_once_with(
        url,
        headers=mock_headers,
        params={"min_id": 1, "limit": 5}
    )
