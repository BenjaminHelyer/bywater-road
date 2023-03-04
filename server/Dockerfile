# syntax=docker/dockerfile:1
FROM python:3.9-bullseye
WORKDIR /docker_server_code
ADD connection.py .
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]