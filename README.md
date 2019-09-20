[![PyPI version](https://badge.fury.io/py/pyombi.svg)](https://badge.fury.io/py/pyombi)

# pyombi

This is a project for retrieving information from an Ombi instance using their API.


# Installation

Run the following to install:
```python
pip install pyombi
```


# Usage


#### Creating an object of your Ombi instance
```python
import pyombi

ombi = pyombi.Ombi(
    ssl=True,
    host="192.168.1.120",
    port="5000",
    api_key="pixf64thuh2m7kbwwgkqp52yznbj4oyo",
    username="MyUsername"
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

pending = ombi.pending_requests
approved = ombi.approved_requests
available = ombi.available_requests
```

# License

This project is licensed under the MIT License - see the LICENSE.txt file for details.
