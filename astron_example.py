from shopping_client import shopping_client

# for now still onboard this package, probably splitting it off later
# this is very raw.
# Officially it doesn't work because a AAI token is required,
# but in 'development mode' that part is skipped in the backend, so that the results are returned anyway
# A proper client should log in with AAI though.

token = "eyJraWQiOiJyc2ExIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIyYzQ5YjQ2OS1kN2FkLTRlNTktYTUwMy1jYWRiYWU5YmQzMGEiLCJuYmYiOjE2MjU0OTM4OTksInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJpc3MiOiJodHRwczpcL1wvaWFtLWVzY2FwZS5jbG91ZC5jbmFmLmluZm4uaXRcLyIsImV4cCI6MTYyNTQ5NzQ5OSwiaWF0IjoxNjI1NDkzODk5LCJqdGkiOiI4NmYxZDI1OC1mOTgzLTQzZWQtODhiYy03NTE2NjM2NDEyZGQiLCJjbGllbnRfaWQiOiI2NjlkN2JlZi0zMmMwLTQ5ODAtYWUzNS1kOGVkZTU2YmQ1ZWYifQ.gGwkDE5P00F-UdRsWazuU1o2QakaN-Vrc8k5vbijLdSTz-O3mrfNqFhxlkfGSno8bz-zRzV2tA8FLPoD5e3B2eOeGtqzTHwMpeJ-t29YwR09YeP5RibfoKh5yr2bEVTfMpBHYZUpZCsXj0m6PcWBvLbNeOIpypUjkseyRaCSHDk"
client = shopping_client(host="https://sdc-dev.astron.nl:5555/",token=token)

try:
    basket = client.get_basket()
    print(basket)
except:
    print('no basket found')