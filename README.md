[![PyPI version](https://badge.fury.io/py/pyombi.svg)](https://badge.fury.io/py/pyombi)
[![Downloads](https://pepy.tech/badge/pyombi)](https://pepy.tech/project/pyombi)

# pyombi

This is a project for interacting with an Ombi instance using their API.


# Installation

Run the following to install:
```python
pip install pyombi
```


# Usage


#### Creating an object of your Ombi instance

**Note:** You have to supply either a `password` or an `api_key` to successfully authenticate. The `api_key` will take precedence if both are supplied.

```python
import pyombi

ombi = pyombi.Ombi(
    ssl=True,
    host="192.168.1.120",
    port="5000",
    urlbase="/ombi",
    username="MyUsername",
    password="MyPassword",
    api_key="pixf64thuh2m7kbwwgkqp52yznbj4oyo"
)
```

#### Testing connection to Ombi

```python
try:
    ombi.test_connection()
except pyombi.OmbiError as e:
    print(e)
    return
```

#### Retrieving data
```python
movies = ombi.movie_requests
tv = ombi.tv_requests
music = ombi.music_requests

total = ombi.total_requests
```

#### Searching

```python
movie_search = ombi.search_movie("Movie Name")  
tv_search = ombi.search_tv("TV show name")
music_search = ombi.search_music_album("Album name")
```

#### Requesting
```python
ombi.request_movie("theMovieDbId")
ombi.request_tv("theTvDbId", "seasonNumber", "episodeNumber")
ombi.request_music("foreignAlbumId")
```

#### Approving
```python
ombi.approve_movie_request("theMovieDbId")
ombi.approve_tv_request("theTvDbId")
```

#### Denying
```python
ombi.deny_movie_request("theMovieDbId")
ombi.deny_tv_request("theTvDbId")
```

# License

This project is licensed under the MIT License - see the LICENSE.txt file for details.
