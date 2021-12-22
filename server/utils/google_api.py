from urllib import parse
from server.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
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
    return await response.json()


async def get_user_email(access_token: str):
    response = await client.get('https://www.googleapis.com/oauth2/v2/userinfo', headers={'Authorization': f'Bearer {access_token}'}, params={'fields': 'email'})
    json = await response.json()
    return json.get('email')
