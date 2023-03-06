import mysql.connector
from flask import Flask
import pandas as pd
import cv2 as cv2
import numpy as np

import json

from BywaterImgConnect.img_connector import ImgConnector

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

def insert_preprocessed_img_to_db(filename, 
                                  tag, 
                                  r_avg, 
                                  g_avg, 
                                  b_avg, 
                                  db_name = 'bywater_road', 
                                  table_name = 'traffic_lights'):
    """Inserts the preprocessed image into the database."""
    try:
        # TODO: do the below the right way with user/pw
        img_db = mysql.connector.connect(
            host="mysqldb",
            user="root",
            password="p@ssw0rd1",
            database=db_name
        )
    except mysql.connector.Error as e:
        return "Connection error: " + str(e)
    cursor = img_db.cursor()

    insert_query = f"INSERT INTO {table_name}" \
                    "(Filename, Tag, r_avg, g_avg, b_avg)" \
                    "VALUES (%s, %s, %s, %s, %s);"
    insert_data = (filename, tag, r_avg, g_avg, b_avg)

    try:
        cursor.execute(insert_query, insert_data)
    except mysql.connector.Error as e:
        return "Insertion error: " + str(e)
    
    img_db.commit()
    cursor.close()
    img_db.close()

    return 'success!'

def load_annotations():
    """Loads the annotations in a Pandas dataframe."""
    myConnector = ImgConnector()
    annotation_path = 'archive/Annotations/Annotations/daySequence1/frameAnnotationsBOX.csv'
    annotations_df = myConnector.get_annotations_from_s3(annotation_path)
    return annotations_df

def load_image_file(annotations_df):
    """Generator to load the image files."""
    myConnector = ImgConnector()
    img_base_path = "archive/daySequence1/daySequence1/frames/"
    # TODO: ensure this is compute + memory efficient later
    for index, row in annotations_df.iterrows():
        filename = row["Filename"]
        tag = row["Annotation tag"]
        upper_left_x = row["Upper left corner X"]
        lower_right_x = row["Lower right corner X"]
        upper_left_y = row["Upper left corner Y"]
        lower_right_y = row["Lower right corner Y"]
        if filename[:8] == 'dayTest/':
            actual_name = filename[8:]
            object_name = img_base_path + actual_name
            img = myConnector.get_img_from_s3(object_name)
            yield img, upper_left_x, lower_right_x, upper_left_y, lower_right_y, filename, tag
        else:
            raise NotImplementedError

def crop_img(img, upper_left_x, lower_right_x, upper_left_y, lower_right_y):
    """Crop the image, returning the subset of the image corresponding to a box determined by 2 coordinates."""
    cropped_img = img[upper_left_y:lower_right_y, upper_left_x:lower_right_x]
    return cropped_img

# TODO: consider using sampling here, to make this more performant, especially if we run this on an edge device at any point
def average_colors(img):
    """Averages all of the colors in the image given as an OpenCV object. Returns a tuple of R, G, and B values."""
    num_pixels = 0
    r_avg = 0
    g_avg = 0
    b_avg = 0
    for row in img:
        for pixel in row:
            r_avg = get_tot_avg(r_avg, num_pixels, pixel[0])
            g_avg = get_tot_avg(g_avg, num_pixels, pixel[1])
            b_avg = get_tot_avg(b_avg, num_pixels, pixel[2])
            num_pixels += 1
    return (r_avg, g_avg, b_avg)

def get_tot_avg(prev_tot, prev_n, new_num):
    """Gets the total average after a new number is added to the series."""
    tot_avg = ((prev_tot)*(prev_n - 1) + new_num)/(prev_n + 1)
    return tot_avg

@app.route('/preprocess')
def preprocess():
    """Preprocesses the data by finding the average RGB values in the part of the image annotated as a traffic light.
    
    The following steps occur:
        1. Annotation file loaded in a dataframe.
        2. Image file retrieved as OpenCV object.
        3. OpenCV parses the section of the image file marked by the x's and y's in the annotation file, recording average RGB values.
        4. Filename, tag, r_avg, g_avg, b_avg all loaded in SQL database.

    Tests needed:
        - Able to query database for some particular filename and see the correct values read back
    """
    annotations_df = load_annotations()
    for img, upper_left_x, lower_right_x, upper_left_y, lower_right_y, filename, tag in load_image_file(annotations_df[:10]): # TODO: make this do it on more images once we optimize that function
        traffic_light_subimage = crop_img(img, upper_left_x, lower_right_x, upper_left_y, lower_right_y)
        rgb_avg = average_colors(traffic_light_subimage)
        db_errs = insert_preprocessed_img_to_db(filename, tag, rgb_avg[0], rgb_avg[1], rgb_avg[2])

    return 'done preprocessing data' + str(db_errs)

if __name__ == "__main__":
    app.run(host ='0.0.0.0')
