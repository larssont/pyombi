"""A python module to retrieve information from Ombi.

For license information, see the LICENSE.txt file.
"""

import logging

_LOGGER = logging.getLogger(__name__)
_BASE_URL = "http{ssl}://{host}:{port}/{urlbase}api/v1/"


class Ombi(object):
    """A class for handling connections with an Ombi instance."""

    def __init__(self, api_key, username, ssl, host, port, urlbase=""):
        self._api_key = api_key
        self._username = username

        self._base_url = _BASE_URL.format(
            ssl="s" if ssl else "", host=host, port=port, urlbase=urlbase
        )

    def test_connection(self):
        self._request_connection(path="Status", return_status=True)

    def _request_connection(self, path, return_status=False, post_data=None):
        import requests

        try:
            if post_data is not None:
                res = requests.post(
                    url=f"{self._base_url}{path}",
                    headers={"ApiKey": self._api_key, "UserName": self._username},
                    json=post_data,
                    timeout=8,
                )
            else:
                res = requests.get(
                    url=f"{self._base_url}{path}",
                    headers={"ApiKey": self._api_key, "UserName": self._username},
                    timeout=8,
                )

            res.raise_for_status()
            res.json()

            if return_status:
                return res.status_code
            else:
                return res
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
                    "Authentication error. Check API key and username configuration."
                )
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
        if requests is None:
            return 0
        return requests

    @property
    def tv_requests(self):
        requests = self._request_connection("Request/tv/total").text
        if requests is None:
            return 0
        return requests

    @property
    def music_requests(self):
        requests = self._request_connection("Request/music/total").text
        if requests is None:
            return 0
        return requests

    @property
    def total_requests(self):
        return self._request_connection("Request/count").json()


class OmbiError(Exception):
    pass
