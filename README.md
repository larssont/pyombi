# pyombi

This is a project for retrieving information from an Ombi instance using their API.


# Installation

Run the following to install:
```python
pip install pyombi
```


# Usage

```python
from pyombi import Ombi

# Creating an object of your Ombi instance. 

hello = Ombi(
    ssl=True,
    host="192.168.1.120",
    port="5000",
    apikey="pixf64thuh2m7kbwwgkqp52yznbj4oyo",
)

# Updating stored data (Note: updates all retrievable data in the object).

hello.update()

# Retrieving data

movie_requests = hello.movie_requests
tv_requests = hello.tv_requests

pending_requests = hello.pending_requests

recently_added_movies = hello.recently_added_movies
recently_added_tv = hello.recently_added_tv
```
# License

This project is licensed under the MIT License - see the LICENSE.txt file for details.