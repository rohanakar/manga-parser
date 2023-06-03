# Manga Parser

## Project Overview

The Manga Parser project is designed to parse images from a Discord server and convert them into videos using OCR (Optical Character Recognition), TTS (Text-to-Speech), and moviepy libraries. The project aims to automate the process of creating manga videos from images shared on a Discord server. By extracting manga images, processing them, and generating videos with or without TTS, the Manga Parser simplifies the creation of manga video content.

## Features

The Manga Parser project offers the following features:

- **Discord Server Integration**: The project can read messages from a Discord server and parse URLs related to manga content.

- **URL Crawling**: It can crawl the provided URLs to fetch manga images and store them in a file storage system.

- **Batch Job Processing**: The project includes batch jobs that process the stored manga images, generating manga videos. The batch jobs utilize OCR, TTS, and moviepy libraries for text extraction, text-to-speech conversion, and video creation.

- **Video Generation Options**: The project provides two video generation options: with TTS and without TTS. The version with TTS ensures that the dialogues from the manga are spoken in the generated video.

- **Database Persistence**: All relevant data, such as Discord messages, manga images, and generated videos, are persisted in a database. This ensures proper functioning and easy retrieval of data.

## Dependencies

The Manga Parser project relies on the following dependencies, which can be installed using the provided `requirements.txt` file:

pip install -r requirements.txt


Make sure to run the above command after setting up the project to install all the necessary dependencies.

## Configuration

The project's configuration files are located in the `config` directory. The configuration files provide settings for API connections, application-specific configurations, and logging. Make sure to configure these files according to your requirements before running the project.

- `api.ini`: Contains API configuration settings.
- `app.ini`: Includes application-specific settings.
- `logging.conf`: Configures the logging behavior of the project.

## Setup

To set up the Manga Parser project locally, follow these steps:

1. Clone the project repository from GitHub:


2. Navigate to the project directory:


3. Create and activate a virtual environment:

    python -m venv venv

    source venv/bin/activate

4. Install the project dependencies:

    pip install -r requirements.txt

    This command will install all the necessary dependencies required for the project.

5. Run the main job to initiate the processing of manga images and video generation:

    python -m jobs.main

    This is a ideally a batch job . It looks for directories as per app.ini 


6. Start the Discord server to interact with the Discord server and parse manga-related messages:

    python -m servers.discord-server


7. The generated manga videos will be stored in the file storage system, and the relevant data will be persisted in the database.

Make sure to complete all the steps mentioned above to properly set up and run the Manga Parser project.

## Usage

To use the Manga Parser project, follow these steps:

1. Make sure you have completed the setup instructions and activated the virtual environment.

2. Run the main job to initiate the processing of manga images and video generation:

