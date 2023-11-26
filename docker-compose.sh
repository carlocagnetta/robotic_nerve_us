#!/bin/bash

set -e 

# build image
gpu_info=$(glxinfo -B | grep 'Vendor\|vendor')
gpu="intel"
printf '%s\n' "$gpu_info"

if [[ $gpu_info == *'Nvidia'* ]]; then
  printf 'Nvidia GPU is present. Build respective docker image...\n'
  gpu="nvidia"
else
  printf 'Nvidia GPU is not present. Build respective docker image for intel GPU...\n'
  gpu="intel"
fi

docker compose -f docker-compose.yaml up rob-us-${gpu} -d --build