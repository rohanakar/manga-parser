import os;
import os;
from PIL import Image;

def list_pending_image_pair(resources_path):
    image_pairs = {}
    processed_dir = resources_path+'/processing'
    inbox_dir = resources_path+'/inbox'
    for manga_folder in os.listdir(inbox_dir):
        manga_folder_path = os.path.join(inbox_dir, manga_folder)
        if(os.path.isdir(manga_folder_path) == False):
            continue
        image_pairs[manga_folder_path]=[]
        if os.path.isdir(manga_folder_path):
            processed_manga_folder_path = os.path.join(processed_dir, manga_folder)
            for root, dirs, files in os.walk(manga_folder_path):
                for file in files:
                    if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.jpeg'):
                        input_image_path = os.path.join(root, file)
                        output_image_path = input_image_path.replace(root, processed_manga_folder_path)
                        image_pairs[manga_folder_path].append((input_image_path, output_image_path))
    return image_pairs


def get_image(path):
    img = Image.open(path,formats=['jpeg'])
    img.load()
    return img

def replace_extension(filename,extension):
    # Find the last occurrence of "."
    last_dot_index = filename.rfind(".")

    # Check if a dot exists and replace the extension
    if last_dot_index != -1:
        new_filename = filename[:last_dot_index] + extension
        return new_filename
    else:
        # No dot found, return the original filename
        return filename

def save(file,content,writeType='wb'):
    with open(file, writeType) as file:
        file.write(content)
        print(f"File saved to: {file}")
    
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    else:
        print(f"Folder '{folder_path}' already exists.")

def open_file(file_path):
    with open(file_path, 'r') as file:
    # Read the contents of the file
        file_contents = file.read()

    return file_contents
