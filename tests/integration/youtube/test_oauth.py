from fastapi import status
from fastapi.testclient import TestClient

OAUTH_URL = "/api/youtube/oauth"


def test_get_oauth_link_when_not_logged_in(client: TestClient):
    response = client.get(OAUTH_URL)
    response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_oauth_link(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(OAUTH_URL)
    response.status_code == status.HTTP_200_OK
