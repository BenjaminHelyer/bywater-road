import mysql.connector
from flask import Flask
import pandas as pd
import cv2 as cv2

import json

# TODO: figure out what's wrong with this connection class
# **May just be an out of order initialization, just try restarting the app
# after it fails once, when we try this connection class again
# from connection import InventoryDb

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/widgets')
def get_widgets():
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="inventory"
    )
    cursor = mydb.cursor()

    cursor.execute("SELECT * FROM widgets")

    row_headers=[x[0] for x in cursor.description] #this will extract row headers

    results = cursor.fetchall()
    json_data=[]
    for result in results:
        json_data.append(dict(zip(row_headers,result)))

    cursor.close()

    return json.dumps(json_data)

@app.route('/addwidgets')
def add_widgets():
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="inventory"
    )
    cursor = mydb.cursor()

    query = "INSERT INTO widgets \
(name, description) \
VALUES ('boxes', 'these are some boxes')"
    # Execute the query 
    cursor.execute(query)

    query = "INSERT INTO widgets \
(name, description) \
VALUES ('tables', 'nice tables')"
    # Execute the query 
    cursor.execute(query)

    query = "INSERT INTO widgets \
(name, description) \
VALUES ('bags', 'plastic bags')"
    # Execute the query 
    cursor.execute(query)

    return 'added widgets'

@app.route('/initdb')
def db_init():
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1"
    )
    cursor = mydb.cursor()

    cursor.execute("DROP DATABASE IF EXISTS inventory")
    cursor.execute("CREATE DATABASE inventory")
    cursor.close()

    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="inventory"
    )
    cursor = mydb.cursor()

    cursor.execute("DROP TABLE IF EXISTS widgets")
    cursor.execute("CREATE TABLE widgets (name VARCHAR(255), description VARCHAR(255))")
    cursor.close()

    return 'init database'

def load_annotations():
    """Loads the annotations in a Pandas dataframe."""
    annotation_path = "C:\\Users\\Benjamin\\Documents\\GitHub\\bywater-road\\local_data\\frameAnnotationsBOX.csv"
    annotations_df = pd.read_csv(annotation_path, sep = ';')
    return annotations_df

def load_image_file(annotations_df):
    """Generator to load the image files."""
    img_base_path = "C:\\Users\\Benjamin\\Downloads\\archive\\daySequence1\\daySequence1\\frames"
    # TODO: ensure this is compute + memory efficient later
    for index, row in annotations_df.iterrows():
        filename = row["Filename"]
        upper_left_x = row["Upper left corner X"]
        lower_right_x = row["Lower right corner X"]
        upper_left_y = row["Upper left corner Y"]
        lower_right_y = row["Lower right corner Y"]
        if filename[:8] == 'dayTest/':
            actual_name = filename[8:]
            img_full_path = img_base_path + "\\" + actual_name
            img = cv2.imread(img_full_path)
            yield img, upper_left_x, lower_right_x, upper_left_y, lower_right_y
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
    imgs = []
    for img, upper_left_x, lower_right_x, upper_left_y, lower_right_y in load_image_file(annotations_df[:10]): # TODO: make this do it on more images once we optimize that function
        traffic_light_subimage = crop_img(img, upper_left_x, lower_right_x, upper_left_y, lower_right_y)
        rgb_avg = average_colors(traffic_light_subimage)
        imgs += [rgb_avg]

    return 'preprocessing data' + str(imgs)

if __name__ == "__main__":
    app.run(host ='0.0.0.0')
