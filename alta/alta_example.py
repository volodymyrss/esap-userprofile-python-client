from shopping_client import shopping_client
from alta import alta_connector

esap_api_host = "http://localhost:5555/"
access_token = "eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIyYzQ5YjQ2OS1kN2FkLTRlNTktYTUwMy1jYWRiYWU5YmQzMGEiLCJuYmYiOjE2MjYxNjc3NDEsInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJpc3MiOiJodHRwczpcL1wvaWFtLWVzY2FwZS5jbG91ZC5jbmFmLmluZm4uaXRcLyIsImV4cCI6MTYyNjE3MTM0MSwiaWF0IjoxNjI2MTY3NzQxLCJqdGkiOiJiMjFlNWE2MC00ZGQ3LTQxNjQtODk3ZS1jMDI0OTEwYjBkZmEiLCJjbGllbnRfaWQiOiI2NjlkN2JlZi0zMmMwLTQ5ODAtYWUzNS1kOGVkZTU2YmQ1ZWYifQ.UNbZkINze8ZgU5MtfAdUQxn7CmTzHrjEGNxYeFsEhtMQSxBCAid6anlOaCppvuegRGTqNAB0XUTOAedtTyWh3X9c-M3jWUTcjAzaeIehYRnv1d0NzjCcQay5UcQ0G5QQ3bDIWqk-iiY-SGDsb-ODiykkrTo-pNoLLtCAiO9ClhQ"
client = shopping_client(host=esap_api_host,token=access_token)

# read the basket as is, providing a token
try:
    basket = client.get_basket()
    print(basket)
except:
    print('no basket found')

# use the alta connector

# Instantiate alta connector
ac = alta_connector()

# Instantiate ESAP User Profile shopping client, passing alta connector
sc = shopping_client(host=esap_api_host, token=access_token, connectors=[ac])

# Retrieve basket (prompts to enter access token obtained from ESAP GUI)
basket=sc.get_basket(convert_to_pandas=False)

print(basket)
for item in basket:
    print(item)