"""Module for connecting to image storage and retrieving images.

Currently implemented with AWS S3.
"""

import json
import io

import boto3
import numpy as np
from PIL import Image

class ImgConnector:
    """Class for connecting to the image storage and retrieving images."""
    def __init__(self, 
                 access_filepath="C:\\Users\\Benjamin\\Documents\\AWS\\bywater-road\\config.txt",
                 s3_bucket_name='bywater-road-imgs'
                 ):
        self.access_filepath = access_filepath
        self.access_key, self.secret_key = self.get_access_keys()
        self.s3_bucket_name = s3_bucket_name

    def get_access_keys(self):
        """Retrieves the access keys for local use."""
        with open(self.access_filepath, 'r') as f:
            config = json.load(f)
        access_key = config['aws_access_key_id']
        secret_key = config['aws_secret_access_key']
        return access_key, secret_key

    def get_img_from_s3(self, object_name, file_name):
        """Retrieves an image from the S3 bucket."""
        s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        response = s3_client.get_object(Bucket=self.s3_bucket_name, Key=object_name)
        image_data = response['Body'].read()
        image_buffer = io.BytesIO(image_data)
        image = Image.open(image_buffer)
        return image

if __name__ == '__main__':
    print("Trying to get an image from S3")
    myConnector = ImgConnector()

    img1 = myConnector.get_img_from_s3('archive/daySequence1/daySequence1/frames/daySequence1--00000.jpg', 
                                        'daySequence1--00000.jpg')
    img1.show()
        