import requests
from unittest.mock import Mock

from main import (
    get_timeline_url,
    get_timeline,
    settings
)


def test_get_timeline_url_global(mock_settings):
    """
    Test the function for the 'global' timeline type.
    """
    url, timeline_type = get_timeline_url("global", mock_settings)
    assert url == "https://example.com/v1/timelines/public?min_id=1&limit=6&_pe=1&remote=true"
    assert timeline_type == "global"


def test_get_timeline_url_notifications(mock_settings):
    """
    Test the function for the 'notifications' timeline type.
    """
    url, timeline_type = get_timeline_url("notifications", mock_settings)
    assert url == "https://example.com/v1/notifications"
    assert timeline_type == "notifications"


def test_get_timeline_url_followers(mock_settings):
    """
    Test the function for the 'followers' timeline type.
    """
    url, timeline_type = get_timeline_url("followers", mock_settings)
    assert url == "https://example.com/v1/accounts/4/followers"
    assert timeline_type == "followers"


def test_get_timeline_url_tags(mock_settings):
    """
    Test the function for the 'tags' timeline type.
    """
    url, timeline_type = get_timeline_url("tag", mock_settings)
    assert url.startswith("https://example.com/v1/timelines/tag")
    assert timeline_type in mock_settings.tags  # Ensure the returned tag is one of the shuffled tags


def test_get_timeline_url_default(mock_settings):
    """
    Test the function for a default timeline type (e.g., 'home').
    """
    url, timeline_type = get_timeline_url("home", mock_settings)
    assert url == "https://example.com/v1/timelines/home"
    assert timeline_type == "home"


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
    result = get_timeline(url, settings)

    # Assertions
    assert result == {"data": "timeline_data"}
    requests.get.assert_called_once_with(
        url,
        headers=mock_headers,
        params={"limit": 10}
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
    result = get_timeline(url, settings, limit=5)

    # Assertions
    assert result == {"data": "timeline_data"}
    requests.get.assert_called_once_with(
        url,
        headers=mock_headers,
        params={"limit": 5}
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
    result = get_timeline(url, settings)

    # Assertions
    assert result == {}
    requests.get.assert_called_once_with(
        url,
        headers=mock_headers,
        params={"limit": 10}
    )
