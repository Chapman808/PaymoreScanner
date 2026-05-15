from bs4 import BeautifulSoup
import requests
import http.client, urllib
import os

user_id_0 = os.getenv("USER_ID_0")
user_id_1 = os.getenv("USER_ID_1")
token = os.getenv("API_KEY")

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


r = requests.get("https://bothellwa.paymore.com/collections/newly-listed-devices")

content = r.content.decode()

soup = BeautifulSoup(content, 'html.parser')
product_grid = soup.find(attrs={'id' : 'product-grid'}).contents[1]
product_1 = product_grid.find_next(attrs={'class' : 'card__information'}).get_text().strip()
#product_count = soup.find(attrs={'id' : 'ProductCount'}).contents[0].split()[0]

with open('last_item.txt', 'r') as f:
  last_item = f.read()

if product_1 != last_item:
  print('new item has been identified')
  print('old newest item: ' + last_item)
  print('new last item: ' + product_1)
  #riley
  send_notification(user_id_0, token, product_1)
  send_notification(user_id_1, token, product_1)
else:
  print('no new items found.')
  print('newest item is still: ' + last_item)
with open('last_item.txt', 'w') as f:
  f.write(product_1)
