# esap-userprofile-python-client

A Python client for the ESCAPE ESAP User Profile REST API.

The `shopping_client` module, which communicates with the ESCAPE ESAP User Profile REST API is very lightweight. Archive-specific functionality is delegated to "connector" modules like the `zooniverse` module.

### Installation

The client and the Zooniverse client cat be installed using pip:

```sh
$ pip install git+https://git.astron.nl/astron-sdc/esap-userprofile-python-client.git
```

### Example - Using the Shopping Client with the Zooniverse connector

```python
from shopping_client import shopping_client
from zooniverse import zooniverse
import getpass

# Prompt for Zooniverse account password
zooniverse_password = getpass.getpass("Enter Zooniverse password:")

# Instantiate Zooniverse connector
zc = zooniverse(username="hughdickinson", password=zooniverse_password)

# Instantiate ESAP User Profile shopping client, passing zooniverse connector
sc = shopping_client(host="https://sdc-dev.astron.nl:5555/", connectors=[zc])

# Retrieve basket (prompts to enter access token obtained from ESAP GUI)
res=sc.get_basket(convert_to_pandas=True)

# ... inspect available results ...

# Retrieve data from Zooniverse based on basket item
data = zc.retrieve(res["zooniverse"].loc[3],
                   generate=False,
                   wait=True,
                   convert_to_pandas=True)

# ... analyse data ...

```

## Contributing

For developer access to this repository, please send a message on the [ESAP channel on Rocket Chat](https://chat.escape2020.de/channel/esap).
