from enum import Enum
import json
from typing import List

class Rectangle:
    def __init__(self,x1,y1,x2,y2) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        

class AudioMetadata:
    def __init__(self, src: str, position: 'Rectangle'):
        self.src = src
        self.position = position
        