# pull official base image
FROM python:3.10.12-slim

COPY  ./utils .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
