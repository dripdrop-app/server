from urllib import parse

from dripdrop.http_client import http_client
from dripdrop.settings import settings, ENV
from dripdrop.logging import logger


class GoogleAPI:
    YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
            "https://www.googleapis.com/auth/youtube.readonly",
        ]
        self.base_headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/51.0.2704.103 Safari/537.36"
            )
        }

    def create_oauth_url(self, callback_url: str = ..., user_id: str = ...):
        if settings.env == ENV.PRODUCTION:
            callback_url = callback_url.replace("http", "https", 1)
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": callback_url,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "access_type": "offline",
            "include_granted_scopes": "true",
            "state": user_id,
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{parse.urlencode(params)}"

    async def get_oauth_tokens(self, callback_url: str = ..., code: str = ...):
        if settings.env == ENV.PRODUCTION:
            callback_url = callback_url.replace("http", "https", 1)
        params = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": callback_url,
            "grant_type": "authorization_code",
        }
        response = await http_client.post(
            "https://oauth2.googleapis.com/token",
            data=params,
            headers=self.base_headers,
        )
        if response.is_success:
            return response.json()
        logger.warning(response.text)
        raise Exception("Failed to retrieve oauth tokens")

    async def refresh_access_token(self, refresh_token: str = ...):
        params = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        response = await http_client.post(
            "https://oauth2.googleapis.com/token",
            params=params,
            headers=self.base_headers,
        )
        if response.is_success:
            return response.json()
        logger.warning(response.text)
        raise Exception("Failed to refresh access token")

    async def get_user_email(self, access_token: str = ...):
        params = {"fields": "email"}
        headers = {"Authorization": f"Bearer {access_token}", **self.base_headers}
        response = await http_client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers=headers,
            params=params,
        )
        if response.is_success:
            json = response.json()
            return json.get("email")
        logger.warning(response.text)
        raise Exception("Failed to retrieve email")

    async def get_video_categories(self):
        params = {
            "key": settings.google_api_key,
            "part": "snippet",
            "regionCode": "US",
        }
        response = await http_client.get(
            f"{GoogleAPI.YOUTUBE_API_URL}/videoCategories",
            params=params,
            headers=self.base_headers,
        )
        if response.is_success:
            json = response.json()
            return json.get("items", [])
        logger.warning(response.text)
        raise Exception("Failed to get video categories")

    async def get_user_subscriptions(self, access_token: str = ...):
        params = {
            "part": "snippet",
            "mine": True,
            "maxResults": 50,
            "pageToken": "",
        }
        headers = {"Authorization": f"Bearer {access_token}", **self.base_headers}
        while params.get("pageToken") is not None:
            response = await http_client.get(
                f"{GoogleAPI.YOUTUBE_API_URL}/subscriptions",
                params=params,
                headers=headers,
            )
            if response.is_success:
                json = response.json()
                yield json.get("items")
                params["pageToken"] = json.get("nextPageToken", None)
            else:
                logger.warning(response.text)
                raise Exception("Failed to get user subscriptions")


google_api = GoogleAPI()
