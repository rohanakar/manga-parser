import discord
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import os
from domain.manga import Manga
from utils import database

# def add_manga(folder):
#     manga = Manga(folder=folder,status=0)
#     database.save(manga)

discord_key = os.getenv('discord_key','discord_key')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def save_images_from_url(url,folder_name):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <img> tags in the HTML
    img_tags = soup.find_all('img')

    # Create a directory to save the images
    

    folder_path = 'resources/inbox/'+folder_name

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Download and save each image
    for img in img_tags:
        img_url = img['src']
        img_name = img_url.split('/')[-1]
        headers = {'User-Agent': 'Mozilla/5.0'}
        if(img_url.startswith("http") == False):
            continue
        if not ( img_url.endswith("png") == True or img_url.endswith("jpg") == True or img_url.endswith("jpeg") == True):
            continue
        if(img_url.endswith("_01.png")):
            continue

        req = urllib.request.Request(img_url, headers=headers)
        print(os.path.join(folder_path,img_name))
        try:
            with urllib.request.urlopen(req) as response:
                with open(os.path.join(folder_path,img_name), 'wb') as f:
                    f.write(response.read())
            print(f"Image saved: {img_name}")
        except Exception as e:
            print(e)
            print(f"Failed to save image: {img_name}")

    add_manga(folder_name)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    for url_pair in extract_url_pair(message.content):
        save_images_from_url(url_pair[0],url_pair[1])

def extract_url_pair(text):
    # Regular expression pattern to match URLs
    url_pattern = re.compile(r'https?://\S+')

    # Find all matches in the text
    matches = re.findall(url_pattern, text)
    url_pair = []
    for url in matches:
        print(url)
        last_slash_index = url.rfind('/')
        page_name = url[last_slash_index + 1:].split("review")[0]
        url_pair.append((url,page_name))


    return url_pair

client.run(discord_key)




