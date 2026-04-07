from typing import Literal

from flask import Flask
import requests
from requests import Response

API_URL = 'https://api.igdb.com/v4'
ACCESS_TOKEN_URL = 'https://id.twitch.tv/oauth2/token'

t_image_type = Literal[
    'cover_small',
    'cover_big',
    'screenshot_med',
    'screenshot_big',
    'screenshot_huge',
    'logo_med',
    'micro',
    'thumb',
    '720p',
    '1080p'
]


def cover_url_builder(igdb_image_id: str, image_type: t_image_type = 'cover_big'):
    return f'https://images.igdb.com/igdb/image/upload/t_{image_type}/{igdb_image_id}.webp'


class IGDB:
    _client_id: str
    _client_secret: str
    _access_token: str
    _expires_in: int
    _debug: bool = False

    def init_app(self, app: Flask):
        self._client_id = app.config['IGDB_CLIENT_ID']
        self._client_secret = app.config['IGDB_CLIENT_SECRET']
        self._authorize()
        self._debug = app.config['IGDB_DEBUG']

        @app.context_processor
        def context_processor():
            return dict(igdb_build_cover_url=cover_url_builder)

    def _authorize(self):
        auth_response = requests.post(url=ACCESS_TOKEN_URL, params={
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'client_credentials'
        })
        auth_response.raise_for_status()
        self._access_token = auth_response.json()['access_token']
        self._expires_in = auth_response.json()['expires_in']

    def api_request(self, endpoint: str, query: str) -> Response:
        url = IGDB._build_url(endpoint)
        params = self._compose_request(query)

        response = requests.post(url=url, **params)
        if self._debug:
            print(f'{response.status_code}: {response.text}')
        response.raise_for_status()
        return response

    @staticmethod
    def _build_url(endpoint: str = ''):
        return f'{API_URL}{endpoint}'

    def _compose_request(self, query: str):
        if not query:
            raise Exception('No query provided!')

        if not isinstance(query, str):
            raise TypeError('Query must be a string')

        request_params = {
            'headers': {
                'Client-ID': self._client_id,
                'Authorization': f'Bearer {self._access_token}'
            },
            'data': query
        }

        return request_params


igdb = IGDB()


def init_app(app: Flask):
    igdb.init_app(app)
