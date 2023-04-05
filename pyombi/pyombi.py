"""A python module to retrieve information from Ombi.

For license information, see the LICENSE.txt file.
"""

import logging
import requests

_LOGGER = logging.getLogger(__name__)
_BASE_URL = "http{ssl}://{host}:{port}/{urlbase}api/v1/"
_BASE_URL_V2 = "http{ssl}://{host}:{port}/{urlbase}api/v2/"


def request(f):
    r = f().json()
    if r["isError"]:
        raise OmbiError(r["errorMessage"])
    return r


class Ombi(object):
    """A class for handling connections with an Ombi instance."""

    def __init__(
        self, ssl, username, host, port, urlbase="", api_key=None, password=None
    ):

        self._base_url = _BASE_URL.format(
            ssl="s" if ssl else "", host=host, port=port, urlbase=urlbase
        )

        self._base_url_v2 = _BASE_URL_V2.format(
            ssl="s" if ssl else "", host=host, port=port, urlbase=urlbase
        )


        self._api_key = api_key
        self._username = username
        self._password = password
        self._auth = None

    def test_connection(self):
        self._request_connection(path="Status")

    def _request_connection(self, path, post_data=None, auth=True, v2_api=False):
  
        if v2_api:
            url = f"{self._base_url_v2}{path}"
        else:
            url = f"{self._base_url}{path}"

        headers = {"UserName": self._username}

        if auth:
            headers.update(**self._auth)

        try:
            if post_data is None:
                res = requests.get(url=url, headers=headers, timeout=8)
            else:
                res = requests.post(url=url, headers=headers, json=post_data, timeout=8)

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

    def authenticate(self):

        if self._api_key:
            self._auth = {"ApiKey": self._api_key}
            return

        credentials = {"userName": self._username, "password": self._password}

        token = (
            self._request_connection(path="Token", post_data=credentials, auth=False)
            .json()
            .get("access_token")
        )
        self._auth = {"Authorization": f"Bearer {token}"}

    def search_movie(self, query):
        return self._request_connection(f"Search/movie/{query}").json()

    def search_tv(self, query):
        return self._request_connection(f"Search/tv/{query}").json()

    def search_music_album(self, query):
        return self._request_connection(f"Search/music/album/{query}").json()

    def request_movie(self, movie_id):
        data = {"theMovieDbId": movie_id}
        request(lambda: self._request_connection(path="Request/movie", post_data=data))

    def request_tv(
        self, tv_id, request_all=False, request_latest=False, request_first=False
    ):
        data = {
            "tvDbId": tv_id,
            "latestSeason": request_latest,
            "requestAll": request_all,
            "firstSeason": request_first,
        }
        request(lambda: self._request_connection(path="Request/tv", post_data=data))

    def request_music(self, album_id):
        data = {"foreignAlbumId": album_id}
        request(lambda: self._request_connection(path="Request/music", post_data=data))

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

    @property
    def movie_requests_unavailable(self):
        count = 30
        position = 0
        sort = "requestedDate"
        sortOrder = "asc"
        path = f"Requests/movie/unavailable/{count}/{position}/{sort}/{sortOrder}"
        requests = self._request_connection(path, v2_api=True)
        return 0 if requests is None else requests
    
class OmbiError(Exception):
    pass
