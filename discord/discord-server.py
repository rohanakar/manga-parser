import discord
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import os

# Create the SQLite database engine
engine = create_engine('sqlite:///sample.db', echo=True)

Base = declarative_base()

# Define the Employee model
class Manga(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    processed = Column(Boolean, default=False)

# Create the database tables (if they don't exist)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def add_manga(url,title):
    session = Session()
    manga = Manga(url=url,title=title,processed=False)
    session.add(manga)
    session.commit()
    session.close()


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
    

    folder_path = './resources/inbox/'+folder_name

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Download and save each image
    for img in img_tags:
        img_url = img['src']
        img_name = img_url.split('/')[-1]
        headers = {'User-Agent': 'Mozilla/5.0'}
        if(img_url.startswith("http") == False):
            continue
        if(img_url.endswith("png") == False):
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

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    for url_pair in extract_url_pair(message.content):
        add_manga(url_pair[0],url_pair[1])
        save_images_from_url(url_pair[0],url_pair[1])

def extract_url_pair(text):
    # Regular expression pattern to match URLs
    url_pattern = re.compile(r'https?://\S+')

    # Find all matches in the text
    matches = re.findall(url_pattern, text)
    url_pair = []
    for url in matches:
        last_slash_index = url.rfind('/')
        page_name = url[last_slash_index + 1:].split("review")[0]
        url_pair.append((url,page_name))


    return url_pair

client.run('MTExMjA1NTY5NDI1MDczNzc3NA.Glx1pv.l1IVHHXjGUirsTATopi1jdgQOMs7UPI3b4lcUg')




