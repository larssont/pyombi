"""A python module to interact with Ombi.

For license information, see the LICENSE.txt file.
"""


def request(f):
    r = f().json()
    if r["isError"]:
        raise OmbiError(r["errorMessage"])
    return r


class Ombi(object):
    """A class for handling connections with an Ombi instance."""

    def __init__(
        self,
        ssl,
        host,
        port=None,
        urlbase="",
        username=None,
        password=None,
        api_key=None,
    ):

        self._base_url = None
        self.set_base_url(ssl, host, port, urlbase)

        self._api_key = api_key
        self._username = username
        self._password = password
        self._auth = None

    def set_base_url(self, ssl, host, port, urlbase):

        protocol = "https://" if ssl else "http://"
        port_suffix = "" if port is None else ":" + str(port)
        self._base_url = f"{protocol}{host}{port_suffix}{urlbase}/api/v1/"

    def test_connection(self):

        self._request_connection(path="Status")

    def _request_connection(self, path, post_data=None, put_data=None, auth=True):
        import requests

        url = f"{self._base_url}{path}"
        timeout = 10

        headers = {}
        if auth:
            headers.update(**self._auth)
        if self._username:
            headers["UserName"] = self._username

        try:
            if post_data is None and put_data is None:
                res = requests.get(url=url, headers=headers, timeout=timeout)
            elif put_data:
                res = requests.put(
                    url=url, headers=headers, json=put_data, timeout=timeout
                )
            else:
                res = requests.post(
                    url=url, headers=headers, json=post_data, timeout=timeout
                )

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
            if status == 403:
                raise OmbiError("Forbidden URL. Check user roles.")
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
        data = {"theMovieDbId": movie_id, "languageCode": "en"}
        request(lambda: self._request_connection(path="Request/movie", post_data=data))

    def request_tv(
        self,
        tv_id,
        season,
        episode,
        request_all=False,
        request_latest=False,
        request_first=False,
    ):
        data = {
            "tvDbId": tv_id,
            "latestSeason": request_latest,
            "requestAll": request_all,
            "firstSeason": request_first,
            "seasons": [
                {"seasonNumber": season, "episodes": [{"episodeNumber": episode}]}
            ],
        }
        request(lambda: self._request_connection(path="Request/tv", post_data=data))

    def request_music(self, album_id):
        data = {"foreignAlbumId": album_id}
        request(lambda: self._request_connection(path="Request/music", post_data=data))

    def approve_movie_request(self, movie_id):
        data = {"id": movie_id}
        request(
            lambda: self._request_connection(
                path="Request/movie/approve", post_data=data
            )
        )

    def approve_tv_request(self, tv_id):
        data = {"id": tv_id}
        request(
            lambda: self._request_connection(path="Request/tv/approve", post_data=data)
        )

    def approve_music_request(self, album_id):
        data = {"id": album_id}
        request(
            lambda: self._request_connection(
                path="Request/music/approve", post_data=data
            )
        )

    def deny_tv_request(self, tv_id, reason="N/A"):
        data = {"id": tv_id, "reason": reason}
        request(lambda: self._request_connection(path="Request/tv/deny", put_data=data))

    def deny_movie_request(self, movie_id, reason="N/A"):
        data = {"id": movie_id, "reason": reason}
        request(
            lambda: self._request_connection(path="Request/movie/deny", put_data=data)
        )

    def deny_music_request(self, album_id, reason="N/A"):
        data = {"id": album_id, "reason": reason}
        request(
            lambda: self._request_connection(path="Request/music/deny", put_data=data)
        )

    def get_movie_requests(self):
        return self._request_connection("Request/movie").json()

    def get_tv_requests(self):
        return self._request_connection("Request/tv").json()

    def get_music_requests(self):
        return self._request_connection("Request/music").json()

    def get_total_movie_requests(self):
        requests = self._request_connection("Request/movie/total").text
        return 0 if requests is None else requests

    def get_total_tv_requests(self):
        requests = self._request_connection("Request/tv/total").text
        return 0 if requests is None else requests

    def get_total_music_requests(self):
        requests = self._request_connection("Request/music/total").text
        return 0 if requests is None else requests

    def get_total_all_requests(self):
        return self._request_connection("Request/count").json()


class OmbiError(Exception):
    pass
