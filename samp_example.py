from shopping_client import shopping_client

# this is very raw.
# Officially it doesn't work because a AAI token is required,
# but in 'development mode' that part is skipped in the backend, so that the results are returned anyway
# A proper client should log in with AAI though.
client = shopping_client(username="vermaas",host="http://localhost:5555/")
client.get_basket()
