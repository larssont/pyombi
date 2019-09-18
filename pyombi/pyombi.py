"""A python module to retrieve information from Ombi.

For license information, see the LICENSE.txt file.
"""

import logging

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

    def test_connection(self):
        self._request_connection(path="Status", is_test=True)

    def update(self):
        self._movie_requests = self._request_connection("Request/movie/total").text
        self._tv_requests = self._request_connection("Request/tv/total").text

        pending = self._request_connection("Request/count").json().get("pending")
        self._pending_requests = pending

    def _request_connection(self, path, is_test=False):

        import requests

        url = f"{self._base_url}{path}"

        try:
            res = requests.get(url, headers={"ApiKey": self._api_key}, timeout=8)
            res.raise_for_status()
            if is_test:
                return res.status_code
            else:
                return res
        except requests.exceptions.Timeout:
            raise OmbiError("Request timed out. Check port configuration.")
        except requests.exceptions.ConnectionError:
            raise OmbiError("Connection error. Check host configuration.")
        except requests.exceptions.TooManyRedirects:
            raise OmbiError("Too many redirects.")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if status == 401:
                raise OmbiError("Authentication error. Check API key configuration.")
            else:
                raise OmbiError("HTTP Error. Check SSL configuration.")
        except ValueError:
            raise OmbiError("ValueError. Check urlbase configuration.")

    @property
    def movie_requests(self):
        return self._movie_requests

    @property
    def tv_requests(self):
        return self._tv_requests

    @property
    def pending_requests(self):
        return self._pending_requests


class OmbiError(Exception):
    pass
