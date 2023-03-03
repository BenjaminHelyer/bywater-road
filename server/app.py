import mysql.connector
import json
from flask import Flask
import pandas as pd
import cv2 as cv2

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

# @app.route('/addcols')
# def add_cols():
#     mydb = mysql.connector.connect(
#         host="mysqldb",
#         user="root",
#         password="p@ssw0rd1",
#         database="inventory"
#     )
#     cursor = mydb.cursor()

#     query = "ALTER TABLE widgets \
# ADD widgetName VARCHAR(100)"
#     # Execute the query 
#     cursor.execute(query)

#     query = "ALTER TABLE widgets \
# ADD widgetCount INT"
#     # Execute the query 
#     cursor.execute(query)

#     return 'added cols'

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
    for filename in annotations_df['Filename'][:10]: # TODO: do this will all files later, need to find a way not to handle this large amount of data well
        if filename[:8] == 'dayTest/':
            actual_name = filename[8:]
            img_full_path = img_base_path + "\\" + actual_name
            img = cv2.imread(img_full_path)
            yield img
        else:
            raise NotImplementedError
        yield img

def crop_img(img, x1, x2, y1, y2):
    """Crop the image, returning the subset of the image corresponding to a box determined by 2 coordinates."""
    raise NotImplementedError

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
    for img in load_image_file(annotations_df):
        imgs += [img]

    return 'preprocessing data' + str(imgs)

if __name__ == "__main__":
    app.run(host ='0.0.0.0')
