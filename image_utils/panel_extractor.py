import argparse
import json
import logging
import os
import sys
import cv2
import numpy as np
from functools import cmp_to_key
import logging.config
from utils.fileutils import writeToFile

def sort_rectangles(rectangles):
    def compare(rect1, rect2):
        # Check if rect1 is inside the height of rect2
        if  rect1[1]+25 >= rect2[1] and rect1[3] <= rect2[3]+25:
            return rect2[2] - rect1[2]  
        elif rect2[1] +25 >= rect1[1] and rect2[3] <= rect1[3] +25:
            return rect2[2] - rect1[2]  
        else:
            return rect1[1] - rect2[1]  # Sort by y1 in ascending order

    sorted_rectangles = sorted(rectangles, key=cmp_to_key(compare))

    return sorted_rectangles

def is_inside(rect1, rect2):
    
    x1, y1, x2, y2 = rect1[0:4]
    x3, y3, x4, y4 = rect2[0:4]
    return x3 <= x1 and y3 <= y1 and x4 >= x2 and y4 >= y2

def remove_inside_rectangles(rectangles):
    rectangles.sort(key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
    non_overlapping = []

    for i, rect in enumerate(rectangles):
        is_inside_rect = False
        for j in range(i + 1, len(rectangles)):
            if is_inside(rect, rectangles[j]):
                is_inside_rect = True
                break
        if not is_inside_rect:
            non_overlapping.append(rect)

    return non_overlapping

def generate_panels(image_path,show_panels):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform Canny edge detection
    edges = cv2.Canny(grayscale, 50, 150)

    # Create a kernel for dilation
    kernel = np.ones((3, 3), np.uint8)

    # Perform dilation to thicken the edges
    thickened_edges = cv2.dilate(edges, kernel, iterations=1)

    # Create a copy of the thickened edges
    filled_edges = thickened_edges.copy()
    contours, _ = cv2.findContours(filled_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        cv2.drawContours(filled_edges, [contour], 0, (255, 255, 255), -1)


    contours, _ = cv2.findContours(filled_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    panels = []
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        panel = image[y:y+h, x:x+w]
        # output_path = os.path.join(output_folder, f"panel_{i+1}.png")
        if cv2.contourArea(contour) > 0.01*image.shape[0]*image.shape[1]:  # Set a threshold to ignore small patches
            panels.append((x, y, x+w, y+h,panel))


    panels = remove_inside_rectangles(panels)
    panels = sort_rectangles(panels)
    if(show_panels == False):
        return panels
    
    image = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    for i,rectangle in enumerate(panels):
       
        x1, y1, x2, y2, panel = rectangle
        color = colors[i % len(colors)]  # Select color from the palette
        cv2.rectangle(image, (x1, y1), (x2, y2),colors[0],1)
        cv2.putText(image, str(i+1), (x1+50, y1+50 ), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow("Labeled Image", image)
    # cv2.imshow("Edges", edges)
    # cv2.imshow("Thickened Edges", thickened_edges)
    # cv2.imshow("Filled Black Patches", filled_edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return panels
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Manga Panel Extractor , return co-ordinates of panels")

    parser.add_argument("--image_path", help="Input image")
    parser.add_argument("--output_metadata_file", help="out metdata file ")
    parser.add_argument("--show_panels", action="store_true", help="Folder path for processed")

    args = parser.parse_args()

    # Convert args namespace to a dictionary
    arguments = vars(args)
    logger.info(arguments)

    panels = generate_panels(arguments['image_path'],arguments['show_panels'])

    logger.debug(f'panels extracted - {len(panels)}')
    metadata_string = json.dumps([panel[0:4] for panel in panels])
    writeToFile(arguments['output_metadata_file'],metadata_string,'w');

if __name__ == "__main__":
    main()

#python -m image_utils.panel_extractor --show_panels --output_metadata_file a.txt --image_path resources/inbox/black-clover-chapter-359/clovertcb_359_002.png 