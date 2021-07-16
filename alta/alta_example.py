from shopping_client import shopping_client
from alta import alta_connector

esap_api_host = "https://sdc-dev.astron.nl:5555/"

# Instantiate alta connector
ac = alta_connector()

# Instantiate ESAP User Profile shopping client, passing alta connector
#sc = shopping_client(host=esap_api_host, token=access_token, connectors=[ac])
sc = shopping_client(host=esap_api_host, connectors=[ac])

# Retrieve basket (prompts to enter access token obtained from ESAP GUI)
basket=sc.get_basket(filter_archives=True)

print(basket)
for item in basket:
    print(item)