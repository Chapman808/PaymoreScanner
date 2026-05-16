import json
from bs4 import BeautifulSoup
import requests
import http.client, urllib
import os
import boto3

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

def get_latest_product():
  r = requests.get("https://bothellwa.paymore.com/collections/newly-listed-devices")
  content = r.content.decode()

  soup = BeautifulSoup(content, 'html.parser')
  product_grid = soup.find(attrs={'id' : 'product-grid'}).contents[1]
  product_1 = product_grid.find_next(attrs={'class' : 'card__information'}).get_text().strip()
  #product_count = soup.find(attrs={'id' : 'ProductCount'}).contents[0].split()[0]
  return product_1

def get_stored_item(context):
  function_arn = context.invoked_function_arn
  lambda_client = boto3.client('lambda')
  response = lambda_client.list_tags(
    Resource=function_arn
  )
  return response['Tags']['Product']

def compare_and_notify(new_product, old_product, user_ids, token):
  if new_product != old_product:
    print('new item has been identified')
    print('old newest item: ' + old_product)
    print('new last item: ' + new_product)
    for id in user_ids:
      send_notification(id, token, new_product)
  else:
    print('no new items found.')
    print('newest item is still: ' + old_product)

def update_stored_item(context, product):
  function_arn = context.invoked_function_arn
  # Define the tag(s) you want to set or update
  tags = {
      'Product': product,
  }

  # Update the tag on itself
  lambda_client = boto3.client('lambda')
  response = lambda_client.tag_resource(
      Resource=function_arn,
      Tags=tags
  )


def lambda_handler(event, context):
  user_ids = [os.getenv("USER_ID_0"), os.getenv("USER_ID_1")]
  token = os.getenv("API_KEY")

  try:
    product = get_latest_product()
  except:
      for id in user_ids:
        send_notification(id, token, "ERROR in pulling product data")
      return {
        'statusCode': 200,
        'body': json.dumps('Ran successfully')
      }
  stored_product = get_stored_item(context)
  compare_and_notify(product, stored_product, user_ids, token)
  update_stored_item(context, product)

  return {
      'statusCode': 200,
      'body': json.dumps('Ran successfully')
  }
