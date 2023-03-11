# bywater-road
Preprocessing pipeline for traffic light recognition in the LISA dataset.

The goal of this project is to flesh out a potential preprocessing pipeline
for the LISA dataset. The raw data is held in a S3 bucket, and the preprocessing
application and SQL database reside in a Docker container.

The post-processing data has been tested locally by building a KNN model. This
model lies outside the scope of the preprocessing pipeline, and therefore
currently lies outside the scope of this project.

The pre-processing steps are as follows for a given image:
1. Retrieve the annotation file from the S3 bucket.
2. Use the annotations to download the image from the S3 bucket.
3. Crop out the annotated traffic light from the image.
4. Average all the pixels in the cropped traffic light image.
5. Store the relevent post-processed data in the SQL database.

Note that steps (3) and (4) can be interchanged for more complex
pre-processing transformations; the basic idea remains the same.