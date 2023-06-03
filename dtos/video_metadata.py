from enum import Enum
from typing import List

class FileType(str,Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"

class VideoMetadata:
    def __init__(self, src: str, file_type: FileType, panels: List):
        self.src = src
        self.file_type = file_type
        self.panels = panels
