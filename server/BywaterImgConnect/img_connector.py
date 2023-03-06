"""Module for connecting to image storage and retrieving images.

Currently implemented with AWS S3.
"""

import json
import io
import os

import boto3
import numpy as np
from PIL import Image
import cv2 as cv2
import pandas as pd

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
        """Retrieves the access keys."""
        try:
            access_key, secret_key = self.get_local_keys()
        except:
            try:
                access_key, secret_key = self.get_environment_variable_keys()
            except:
                # TODO: implement a better exception here once we're done prototyping locally
                print("Tried to get access keys and failed. Exiting.")
                return None, None
        return access_key, secret_key
    
    def get_local_keys(self):
        """Retrieves the access keys for local use."""
        with open(self.access_filepath, 'r') as f:
            config = json.load(f)
        access_key = config['aws_access_key_id']
        secret_key = config['aws_secret_access_key']
        return access_key, secret_key
    
    def get_environment_variable_keys():
        """Retrieves the access keys from environment variables."""
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        return access_key, secret_key
    
    def _get_object_from_s3(self, object_name):
        """Retrieves an object from the S3 bucket and returns it as a byte stream."""
        s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        response = s3_client.get_object(Bucket=self.s3_bucket_name, Key=object_name)
        data = response['Body'].read()
        buffer = io.BytesIO(data)
        return buffer

    def get_img_from_s3(self, object_name):
        """Retrieves an image from the S3 bucket."""
        img_buffer = self._get_object_from_s3(object_name)
        # TODO: make this cleaner, try not to have to convert from PIL to OpenCV if possible. Try to just stream to OpenCV.
        pil_img = Image.open(img_buffer)
        opencvImage = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return opencvImage
    
    def get_annotations_from_s3(self, object_name):
        """Retrieves an annotation file as a pandas dataframe from the S3 bucket."""
        annotation_buffer = self._get_object_from_s3(object_name)
        annotation_df = pd.read_csv(annotation_buffer, sep = ';')
        return annotation_df
        