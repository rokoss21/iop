import openrouter
from unittest import mock


def test_validate_api_key_success():
    with mock.patch("openrouter.requests.get") as mocked_get:
        mocked_get.return_value.status_code = 200
        assert openrouter.validate_api_key("dummy") is True


def test_validate_api_key_failure():
    with mock.patch("openrouter.requests.get") as mocked_get:
        mocked_get.return_value.status_code = 401
        assert openrouter.validate_api_key("dummy") is False