#!/bin/bash

echo "TODO: fill in the docker run command"

# Run the Docker container for the serving app
docker run -p 8000:8000 -e WANDB_API_KEY=$WANDB_API_KEY ift6758-serving