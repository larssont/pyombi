"""A python module to retrieve information from Ombi.

For license information, see the LICENSE.txt file.
"""

import logging

import requests

_LOGGER = logging.getLogger(__name__)
_BASE_URL = "http{ssl}://{host}:{port}/{urlbase}api/v1/"


class Ombi(object):
    """A class for handling connections with an Ombi instance."""

    def __init__(self, ssl, host, port, api_key, urlbase=""):
        self._api_key = api_key

        urlbase = urlbase.strip("/")
        if urlbase:
            urlbase = f"{urlbase}/"

        self._base_url = _BASE_URL.format(
            ssl="s" if ssl else "", host=host, port=port, urlbase=urlbase
        )
        self._movie_requests = (None,)
        self._tv_requests = (None,)
        self._pending_requests = (None,)
        self._recently_added_movies = ({},)
        self._recently_added_tv = ({},)

    def test_connection(self):
        try:
            res = self._request_connection("Status")
            res.raise_for_status()
            return res.status_code
        except requests.exceptions.Timeout:
            return "timeout"
        except requests.exceptions.ConnectionError:
            return "connection error"
        except requests.exceptions.TooManyRedirects:
            return "too many redirects"
        except requests.exceptions.HTTPError as e:
            return e.response.status_code

    def update(self):
        self._movie_requests = self._request_connection("Request/movie/total").text
        self._tv_requests = self._request_connection("Request/tv/total").text

        pending = self._request_connection("Request/count").json().get("pending")
        self._pending_requests = pending

        def iterate_media(path):
            media = {}
            res = self._request_connection(path)
            for entry in res.json():
                media[entry.get("title")] = entry.get("addedAt")
            return media

        self._recently_added_movies = iterate_media("RecentlyAdded/movies")
        self._recently_added_tv = iterate_media("RecentlyAdded/tv/grouped")

    def _request_connection(self, path):
        url = f"{self._base_url}{path}"
        return requests.get(url, headers={"ApiKey": self._api_key}, timeout=8)

    @property
    def movie_requests(self):
        return self._movie_requests

    @property
    def tv_requests(self):
        return self._tv_requests

    @property
    def pending_requests(self):
        return self._pending_requests

    @property
    def recently_added_movies(self):
        return self._recently_added_movies

    @property
    def recently_added_tv(self):
        return self._recently_added_tv
