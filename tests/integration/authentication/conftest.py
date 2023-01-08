import pytest


@pytest.fixture
def assert_session_response():
    def _assert_session_response(json: dict = ..., email: str = ..., admin: bool = ...):
        assert json.get("email") == email
        assert json.get("admin") == admin

    return _assert_session_response


@pytest.fixture
def assert_user_auth_response(assert_session_response):
    def _assert_user_auth_response(
        json: dict = ..., email: str = ..., admin: bool = ...
    ):
        assert "accessToken" in json
        assert "tokenType" in json
        assert "user" in json
        assert_session_response(json=json["user"], email=email, admin=admin)

    return _assert_user_auth_response
