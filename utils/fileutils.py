
import logging
import os
import string

logger = logging.getLogger(__name__)

def writeToFile(file,content,writeMode='wb'):
    logger.debug(f"preparing to write to {file} in {writeMode}")
    try:
        with open(file, writeMode) as file:
            file.write(content)
            logger.debug(f"File Written succesfully at {file.name}")
    except Exception as e:
        logger.error(f"File could not be written at {file} - {e}")    

def list_folders(folder):
    logger.debug(f"Listing all folders in {folder} ")
    return [(file) for file in os.listdir(folder) if not file.startswith('.')]
        
def get_files(folder):
    logger.debug(f"Listing all files in {folder} ")
    return [(file) for file in os.listdir(folder) if not file.startswith('.') and not os.path.isdir(os.path.join(folder, file))]

def read_file(file_path):
    logger.debug(f"Reading contents of {file_path} ")
    with open(file_path, 'r') as file:
    # Read the contents of the file
        file_contents = file.read()

    return file_contents

def create_folders(folders):
    created_folders = []

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            created_folders.append(folder)
    logger.debug(f'created {created_folders}')        
    return create_folders

def get_file_name(file:string):
    return os.path.splitext(file)[0]

def get_tts_file_name(file:string,tts):
    file =  os.path.splitext(file)[0]
    file = file.split("/")
    return os.path.join(file[0],str(tts),file[1])

def change_extension(file:string, extension:string):
    return get_file_name(file)+"."+extension
    
def get_relative_path(folder:string,*file):
    return os.path.join(folder,*file)



