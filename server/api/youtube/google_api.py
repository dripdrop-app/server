import requests
from typing import List
from urllib import parse
from asgiref.sync import sync_to_async
from server.config import config

scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
    "https://www.googleapis.com/auth/youtube.readonly",
]

base_headers = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/51.0.2704.103 Safari/537.36"
    )
}


def create_oauth_url(callback_url: str, user_id: str):
    params = {
        "client_id": config.google_client_id,
        "redirect_uri": callback_url,
        "scope": " ".join(scopes),
        "response_type": "code",
        "access_type": "offline",
        "include_granted_scopes": "true",
        "state": user_id,
    }
    return {
        "params": params,
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?{parse.urlencode(params)}",
    }


@sync_to_async
def get_oauth_tokens(callback_url: str, code: str):
    params = {
        "code": code,
        "client_id": config.google_client_id,
        "client_secret": config.google_client_secret,
        "redirect_uri": callback_url,
        "grant_type": "authorization_code",
    }
    response = requests.post(
        "https://oauth2.googleapis.com/token", data=params, headers=base_headers
    )
    if response.ok:
        return response.json()
    return None


@sync_to_async
def refresh_access_token(refresh_token: str):
    params = {
        "client_id": config.google_client_id,
        "client_secret": config.google_client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(
        "https://oauth2.googleapis.com/token", params=params, headers=base_headers
    )
    if response.ok:
        return response.json()
    return None


@sync_to_async
def get_user_email(access_token: str):
    params = {"fields": "email"}
    headers = {"Authorization": f"Bearer {access_token}", **base_headers}
    response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo", headers=headers, params=params
    )
    if response.ok:
        json = response.json()
        return json.get("email")
    return None


@sync_to_async
def get_video_categories():
    params = {"key": config.google_api_key, "part": "snippet", "regionCode": "US"}
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videoCategories",
        params=params,
        headers=base_headers,
    )
    if response.ok:
        json = response.json()
        return json.get("items", [])
    return []


def get_user_subscriptions(access_token: str):
    params = {
        "part": "snippet",
        "mine": True,
        "maxResults": 50,
        "pageToken": "",
    }
    headers = {"Authorization": f"Bearer {access_token}", **base_headers}
    while params.get("pageToken") is not None:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/subscriptions",
            params=params,
            headers=headers,
        )
        if response.ok:
            json = response.json()
            yield json.get("items")
            params["pageToken"] = json.get("nextPageToken", None)
        else:
            yield []
            params["pageToken"] = None


@sync_to_async
def get_channels_info(channel_ids: List[str]):
    params = {
        "key": config.google_api_key,
        "part": "snippet,contentDetails",
        "id": ",".join(channel_ids),
        "maxResults": 50,
    }
    response = requests.get(
        "https://youtube.googleapis.com/youtube/v3/channels",
        params=params,
        headers=base_headers,
    )
    if response.ok:
        json = response.json()
        return json.get("items", [])
    return []


def get_playlist_videos(playlist_id: str):
    params = {
        "key": config.google_api_key,
        "part": "contentDetails",
        "playlistId": playlist_id,
        "maxResults": 50,
        "pageToken": "",
    }
    while params.get("pageToken") is not None:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params,
            headers=base_headers,
        )
        if response.ok:
            json = response.json()
            yield json.get("items", [])
            params["pageToken"] = json.get("nextPageToken", None)
        else:
            yield []
            params["pageToken"] = None


@sync_to_async
def get_videos_info(video_ids: str):
    params = {
        "key": config.google_api_key,
        "part": "snippet",
        "id": ",".join(video_ids),
        "maxResults": 50,
    }
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos", params=params
    )
    if response.ok:
        json = response.json()
        return json.get("items", [])
    return []
