import requests
import json

def get_product_list():
    url = "https://api.exchange.coinbase.com/products"

    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    # print(response.text)
    product_json = json.loads(response.text)
    # pprint.pprint(product_json)

    product_list = [x['id'] for x in product_json]
    product_list.sort()
    return product_list