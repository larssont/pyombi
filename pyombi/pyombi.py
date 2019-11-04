"""A python module to retrieve information from Ombi.

For license information, see the LICENSE.txt file.
"""

import logging

_LOGGER = logging.getLogger(__name__)
_BASE_URL = "http{ssl}://{host}:{port}/{urlbase}api/v1/"


class Ombi(object):
    """A class for handling connections with an Ombi instance."""

    def __init__(
        self, ssl, username, host, port, urlbase="", api_key=None, password=None
    ):

        self._base_url = _BASE_URL.format(
            ssl="s" if ssl else "", host=host, port=port, urlbase=urlbase
        )

        self._api_key = api_key
        self._username = username
        self._password = password
        self._auth = self._authenticate()

    def test_connection(self):
        self._request_connection(path="Status")

    def _request_connection(self, path, post_data=None, auth=True):
        import requests

        headers = {"UserName": self._username}
        if auth:
            headers.update(**self._auth)

        try:
            if post_data is None:
                res = requests.get(
                    url=f"{self._base_url}{path}", headers=headers, timeout=8,
                )
            else:
                url = f"{self._base_url}{path}"
                res = requests.post(url=url, json=post_data, timeout=8,)

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
                raise OmbiError(
                    "Unauthorized error. Incorrect authentication credentials or insufficient permissions."
                )
            else:
                raise OmbiError(f"HTTP Error {status}. Check SSL configuration.")
        except ValueError:
            raise OmbiError("ValueError. Check urlbase configuration.")

    def _authenticate(self):

        if self._api_key:
            return {"ApiKey": self._api_key}

        credentials = {"userName": self._username, "password": self._password}

        token = (
            self._request_connection(path="Token", post_data=credentials, auth=False)
            .json()
            .get("access_token")
        )
        return {"Authorization": f"Bearer {token}"}

    def search_movie(self, query):
        return self._request_connection(f"Search/movie/{query}").json()

    def search_tv(self, query):
        return self._request_connection(f"Search/tv/{query}").json()

    def search_music_album(self, query):
        return self._request_connection(f"Search/music/album/{query}").json()

    def request_movie(self, movie_id):
        data = {"theMovieDbId": movie_id}
        return self._request_connection("Request/movie", post_data=data)

    def request_tv(
        self, tv_id, request_all=False, request_latest=False, request_first=False
    ):
        data = {
            "tvDbId": tv_id,
            "latestSeason": request_latest,
            "requestAll": request_all,
            "firstSeason": request_first,
        }
        return self._request_connection("Request/tv", post_data=data)

    def request_music(self, album_id):
        data = {"foreignAlbumId": album_id}
        return self._request_connection("Request/music", post_data=data)

    @property
    def movie_requests(self):
        requests = self._request_connection("Request/movie/total").text
        return 0 if requests is None else requests

    @property
    def tv_requests(self):
        requests = self._request_connection("Request/tv/total").text
        return 0 if requests is None else requests

    @property
    def music_requests(self):
        requests = self._request_connection("Request/music/total").text
        return 0 if requests is None else requests

    @property
    def total_requests(self):
        return self._request_connection("Request/count").json()


class OmbiError(Exception):
    pass