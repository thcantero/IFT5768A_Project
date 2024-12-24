#!/bin/bash

# Run the Docker container for the serving app
docker-compose up --build
#docker run -p 5000:5000 -e API_KEY=$API_KEY app-image