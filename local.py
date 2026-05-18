import json
import time
from bs4 import BeautifulSoup
import requests
import http.client, urllib
import os
import pickle

def send_notification(user_id, token, item_name):
  conn = http.client.HTTPSConnection("api.pushover.net:443")
  url = 'https://bothellwa.paymore.com/collections/newly-listed-devices'
  conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
      "token": token,
      "user": user_id,
      "message": "new List item has been found on the PayMore site. \n {}\nSee here: {} ".format(item_name, url),
    }), { "Content-type": "application/x-www-form-urlencoded" })
  conn.getresponse()


def get_stored_items():
  with open ('products1.txt', 'rb') as f:
    products = pickle.load(f)
  return products


def compare_and_notify(new_product, products, user_ids, token):

  if new_product not in products:
    print('new item has been identified')
    print('stored items: ' + str(products))

    for id in user_ids:
      send_notification(id, token, new_product)
  else:
    print('no new items found.')
    print('newest item is still: ' + new_product)

def update_stored_items(new_product, products):
  products.add(new_product)
  with open ('products1.txt', 'wb') as f:
    pickle.dump(products, f)


if __name__ == "__main__":
  user_ids = [os.getenv("USER_ID_0"), os.getenv("USER_ID_1")]
  token = os.getenv("API_KEY")

  try:
    print('getting latest product.')
    r = requests.get(f"https://bothellwa.paymore.com/collections/newly-listed-devices?{int(time.time())}", headers={'Cache-Control': 'no-cache'})
    content = r.content.decode()
    soup = BeautifulSoup(content, 'html.parser')
    import re 
    data  = soup.find_all("script")[37].string
    product_grid = soup.find(attrs={'id' : 'product-grid'}).contents[1]
    print('product grid: ' + str(product_grid))
    product = product_grid.find_next(attrs={'class' : 'card__information'}).get_text().strip()
    #product_count = soup.find(attrs={'id' : 'ProductCount'}).contents[0].split()[0]
    print('latest product is: ' + product)
  except Exception as e:
      print(e)
      print('failed to get latest product')
      for id in user_ids:
        pass
        #send_notification(id, token, "ERROR in pulling product data")
  print('getting stored products')
  
  stored_products = get_stored_items()
  print('stored items: ' + str(stored_products))
  compare_and_notify(product, stored_products, user_ids, token)
  update_stored_items(product, stored_products)