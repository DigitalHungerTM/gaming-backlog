from flask import Flask
import requests
from requests import Response

API_URL = 'https://api.igdb.com/v4'
ACCESS_TOKEN_URL = 'https://id.twitch.tv/oauth2/token'

class IGDB:
    _client_id: str
    _client_secret: str
    _access_token: str
    _expires_in: int


    def init_app(self, app: Flask):
        self._client_id = app.config['IGDB_CLIENT_ID']
        self._client_secret = app.config['IGDB_CLIENT_SECRET']
        self._authorize()


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