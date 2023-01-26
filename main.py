from bs4 import BeautifulSoup
import requests
import datetime
import random
import tweepy
import os
import logging
from keys import *

# Set the basic logging configuration --> In here we are stocking the tweets made in a file post.log
logging.basicConfig(filename='post.log', level=logging.INFO)
LOGGER = logging.getLogger()

def api():
    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    return tweepy.API(auth)

def tweet(api:tweepy.API, message:str, image_path=None):
    if image_path:
        id = api.update_status_with_media(message, image_path)
    else:
        id = api.update_status(message)
    
    print('Twitted successfully')

    return id

# if __name__ == '__main__':
#     api = api()
#     tweet(api, 'Hello twitter')


# Get the page of the list of foods
URL = 'https://www.dietetic-international.com/meilleures-ventes?p=7'
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}

r = requests.get(URL, headers=headers).text

soup1 = BeautifulSoup(r, 'html.parser')

products = soup1.select('a[class=product-name]')

# Choose one randomly and check if it is in the csv file of posted.csv if True then we choose another one else we go to his link
recipe_of_the_day = random.choice(products)

r2 = requests.get(recipe_of_the_day['href'], headers).text
soup2 = BeautifulSoup(r2, 'html.parser')

# and we get the image of the product in a temporary file, after that we go and get the recipe which will be displayed as a response
product_image = soup2.select('img[itemprop=image]')

image_url = product_image[0]['src']

response = requests.get(image_url)
# We post the title of the product and his image as a tweet and the recipe as a response
if response.status_code == 200:
    with open('temp.png', 'wb+') as f:
        f.write(response.content)

    recipe = soup2.select('div[class=rte]')
    api = api()
    link = '\nRecipe at {}'.format(recipe_of_the_day['href'])
    id = tweet(api, product_image[0]['title'] + link, 'temp.png')
    # api.update_status(in_reply_to_status_id=id, status='Recipe at {}'.format(recipe_of_the_day['href']))
    # use a logging system to save the tweet posted and their date time
    LOGGER.info('tweet-{} and {} at {}'.format(product_image[0]['title'], 'temp.png', str(datetime.datetime.now())))
    # We delete the image because we don't need it anymore
    os.remove('temp.png')

else:
    print('Unable to get the image')