"""A python module to interact with Ombi.

For license information, see the LICENSE.txt file.
"""

import logging

import requests

_LOGGER = logging.getLogger(__name__)


def request(f):
    r = f().json()
    if r["isError"]:
        raise OmbiError(r["errorMessage"])
    return r


class OmbiError(Exception):
    pass


class Ombi(object):
    """A class for handling connections with an Ombi instance."""

    def __init__(self, host, port=True, username=None, password=None, api_key=None,
                 urlbase="/ombi", ssl=True):

        if api_key is None and password is None:
            raise TypeError('Username/Password or API key must be set')
        self.url_fix(host, ssl, port, urlbase)

        if api_key:
            self._api_key = api_key
            self._auth = {"ApiKey": self._api_key}
        elif username:
            self._username = username
            self._password = password

    def url_fix(self, host, port, ssl, urlbase):
        if port is True:
            if 'https://' in host and ssl:
                self._base_url = f'{host}{urlbase}/api/v1/'
            elif 'http://' in host and ssl is False:
                self._base_url = f'{host}{urlbase}/api/v1/'
            elif ssl is False:
                self._base_url = f'http://{host}{urlbase}/api/v1/'
            else:
                self._base_url = f'https://{host}{urlbase}/api/v1/'
        else:
            if 'https://' in host and ssl:
                self._base_url = f'{host}:{port}{urlbase}/api/v1/'
            elif 'http://' in host and ssl is False:
                self._base_url = f'{host}:{port}{urlbase}/api/v1/'
            elif ssl is False:
                self._base_url = f'http://{host}:{port}{urlbase}/api/v1/'
            else:
                self._base_url = f'https://{host}:{port}{urlbase}/api/v1/'

        if 'https://http' in self._base_url:
            raise TypeError(f'URL is invalid: {self._base_url}')

    def test_connection(self):
        res = self._request_connection(path="Status")
        if res.ok:
            return 'ok'

    def _request_connection(self, path, post_data=None, put_data=None,
                            auth=True):
        url = f"{self._base_url}{path}"

        if auth:
            headers = self._auth

        try:
            if post_data is None and put_data is None:
                res = requests.get(url=url, headers=headers, timeout=10)
            elif put_data:
                res = requests.put(url=url, headers=headers, json=put_data,
                                   timeout=10)
            else:
                res = requests.post(url=url, headers=headers, json=post_data,
                                    timeout=10)
            res.raise_for_status()
            res.json()
            return res

        except TypeError:
            raise OmbiError("No authentication type set.")
        except requests.exceptions.Timeout:
            raise OmbiError("Request timed out. Check port configuration.")
        except requests.exceptions.ConnectionError:
            raise OmbiError("Connection error. Check host configuration.")
        except requests.exceptions.TooManyRedirects:
            raise OmbiError("Too many redirects.")
        except requests.exceptions.HTTPError as err:
            status = err.response.status_code
            if status == 401:
                raise OmbiError("Unauthorized error. Check authentication credentials.")
            else:
                raise OmbiError(f"HTTP Error {status}. Check SSL configuration.")
        except ValueError:
            raise OmbiError("ValueError. Check urlbase configuration.")

    def search_movie(self, query):
        return self._request_connection(f"Search/movie/{query}").json()

    def search_tv(self, query):
        return self._request_connection(f"Search/tv/{query}").json()

    def search_music_album(self, query):
        return self._request_connection(f"Search/music/album/{query}").json()

    def request_movie(self, movie_id):
        data = {"theMovieDbId": movie_id, "languageCode": "en"}
        request(lambda: self._request_connection(path="Request/movie",
                post_data=data))

    def request_tv(self, tv_id, season, episode, request_all=False,
                   request_latest=False, request_first=False):
        data = {
            "tvDbId": tv_id,
            "latestSeason": request_latest,
            "requestAll": request_all,
            "firstSeason": request_first,
            "seasons": [{
                "seasonNumber": season,
                "episodes": [{
                    "episodeNumber": episode
                    }]
                }]
            }
        request(lambda: self._request_connection(path="Request/tv",
                post_data=data))

    def request_music(self, album_id):
        data = {"foreignAlbumId": album_id}
        request(lambda: self._request_connection(path="Request/music", post_data=data))

    def get_movie_requests(self):
        return self._request_connection("Request/movie").json()

    def get_tv_requests(self):
        return self._request_connection("Request/tv").json()

    def approve_movie_request(self, id):
        data = {"id": id}
        request(lambda: self._request_connection(path="Request/movie/approve",
                post_data=data))

    def approve_tv_request(self, id):
        data = {"id": id}
        request(lambda: self._request_connection(path="Request/tv/approve",
                post_data=data))

    def deny_tv_request(self, id, reason="Not now"):
        data = {"id": id, "reason": reason}
        request(lambda: self._request_connection(path="Request/tv/deny",
                put_data=data))

    def deny_movie_request(self, id, reason="Not now"):
        data = {"id": id, "reason": reason}
        request(lambda: self._request_connection(path="Request/movie/deny",
                put_data=data))

    @property
    def total_movie_requests(self):
        requests = self._request_connection("Request/movie/total").text
        return 0 if requests is None else requests

    @property
    def total_tv_requests(self):
        requests = self._request_connection("Request/tv/total").text
        return 0 if requests is None else requests

    @property
    def total_music_requests(self):
        requests = self._request_connection("Request/music/total").text
        return 0 if requests is None else requests

    @property
    def total_requests(self):
        return self._request_connection("Request/count").json()
