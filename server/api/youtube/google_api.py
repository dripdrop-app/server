from typing import List
from urllib import parse
from server.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_API_KEY
from server.request_client import client

scopes = [
    'https://www.googleapis.com/auth/userinfo.email',
    'openid',
    'https://www.googleapis.com/auth/youtube.readonly'
]


def create_oauth_url(callback_url: str, user_id: str):
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': callback_url,
        'scope': ' '.join(scopes),
        'response_type': 'code',
        'access_type': 'offline',
        'include_granted_scopes': 'true',
        'state': user_id,
    }
    return {
        'params': params,
        'url': f'https://accounts.google.com/o/oauth2/v2/auth?{parse.urlencode(params)}'
    }


async def get_oauth_tokens(callback_url: str, code: str):
    params = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': callback_url,
        'grant_type': 'authorization_code'
    }
    response = await client.post('https://oauth2.googleapis.com/token', data=params)
    if response.ok:
        return await response.json()
    return None


async def refresh_access_token(refresh_token: str):
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = await client.get('https://oauth2.googleapis.com/token', data=params)
    if response.ok:
        return await response.json()
    return None


async def get_user_email(access_token: str):
    response = await client.get('https://www.googleapis.com/oauth2/v2/userinfo', headers={'Authorization': f'Bearer {access_token}'}, params={'fields': 'email'})
    if response.ok:
        json = await response.json()
        return json.get('email')
    return None


async def get_video_categories():
    params = {
        'key': GOOGLE_API_KEY,
        'part': 'snippet',
        'regionCode': 'US'
    }
    response = await client.get('https://www.googleapis.com/youtube/v3/videoCategories', data=params)
    if response.ok:
        json = await response.json()
        return json.get('items')
    return []


async def get_user_subscriptions(access_token: str):
    params = {
        'part': 'snippet',
        'mine': True,
        'maxResults': 50,
        'pageToken': '',
    }
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    while params.get('pageToken') != None:
        response = await client.get('https://www.googleapis.com/youtube/v3/subscriptions', data=params, headers=headers)
        if response.ok:
            json = await response.json()
            yield json.get('items')
            params['pageToken'] = json.get('nextPageToken', None)
        else:
            yield []
            params['pageToken'] = None


async def get_channels_info(channel_ids: List[str]):
    params = {
        'key': GOOGLE_API_KEY,
        'part': 'snippet, contentDetails',
        'id': ','.join(channel_ids),
        'maxResults': 50,
        'pageToken': ''
    }
    response = await client.get('https://youtube.googleapis.com/youtube/v3/channels', data=params)
    if response.ok:
        json = await response.json()
        return json.get('items')
    return []
