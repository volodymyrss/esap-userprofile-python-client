from shopping_client import shopping_client
from alta import alta_connector
from astron_vo import astron_vo_connector
from samp import samp_connector

esap_api_host = "https://sdc-dev.astron.nl:5555/"
#access_token = ""

# Instantiate alta connector
ac = alta_connector()
vo = astron_vo_connector()

# Instantiate ESAP User Profile shopping client, passing alta connector
#sc = shopping_client(host=esap_api_host, token=access_token, connectors=[ac,vo])
sc = shopping_client(host=esap_api_host, connectors=[ac])

# 'apertif'and 'astron_vo' items converted to pandas dataframe
basket_pandas=sc.get_basket(filter_archives=True, convert_to_pandas=True)

print('------------------------------------')
print("'apertif'and 'astron_vo' items converted to pandas dataframe")
print(basket_pandas)

# 'apertif'and 'astron_vo' items as json
basket_json=sc.get_basket(filter_archives=True, convert_to_pandas=False)

print('-----------------------------------')
print("'apertif'and 'astron_vo' items as json")
print(basket_json)

samp_connector = samp_connector()
sc = shopping_client(host=esap_api_host, token=access_token, connectors=[samp_connector])

# "'SAMP' items converted to pandas dataframe:"
basket_pandas=sc.get_basket(convert_to_pandas=True, filter_archives=True)

print('------------------------------------')
print("'SAMP' items converted to pandas dataframe:")
print(basket_pandas)

# 'SAMP' items as json:
basket_json=sc.get_basket(convert_to_pandas=False, filter_archives=True)
print('------------------------------------')
print("'SAMP' items as json:")
print(basket_json)