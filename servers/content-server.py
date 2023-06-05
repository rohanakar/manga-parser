import configparser
import logging
from flask import Flask, send_file, render_template, send_from_directory
import os

from utils import fileutils

logger = logging.getLogger(__name__)

# Define the path to the manga chapters and videos
config = configparser.ConfigParser()
config.read('config/app.ini')

default_values = config["DEFAULT"]
inbox_path = default_values['inbox_folder']
processed_path = default_values['processed_folder']
app = Flask(__name__,static_url_path='/resources', 
            static_folder='../resources')

@app.route('/')
def index():
    # Get the list of manga titles from the inbox folder
    manga_titles = fileutils.list_folders(inbox_path)
    return render_template('index.html', manga_titles=manga_titles)

@app.route('/manga/<title>')
def manga(title):
    # Get the list of image files for the specified manga title
    manga_folder = os.path.join(inbox_path, title)
    image_files = [(image,f'/{manga_folder}/{image}') for image in sorted(fileutils.get_files(manga_folder))]
    return render_template('manga.html', title=title, image_files=image_files)

@app.route('/video/<title>')
def video(title):
    # Get the path to the processed video file for the specified manga title
    video_files = [f'/{processed_path}/{title}-True.mp4',f'/{processed_path}/{title}-False.mp4']
    return render_template('video.html', video_files = video_files)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
