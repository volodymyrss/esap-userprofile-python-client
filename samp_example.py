from shopping_client import shopping_client

client = shopping_client(username="vermaas",host="http://localhost:5555/")
client.get_basket()
