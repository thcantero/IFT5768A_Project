#!/bin/bash


# Build the Docker image for the serving app
docker build -t ift6758/serving -f Dockerfile.serving .
#docker build -t app-image -f Dockerfile.serving .