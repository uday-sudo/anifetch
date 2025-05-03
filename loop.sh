#!/bin/bash

FRAME_DIR="/tmp/anifetch/output"

# Gracefully handle Ctrl+C
trap "echo -e '\nExiting...'; exit 0" SIGINT

framerate=$1
top=$2
left=$3
right=$4
bottom=$5

# Compute 1 / FRAMERATE using bc
sleep_time=$(echo "scale=4; 1 / $framerate" | bc)

index=0
index+=1
while true; do
  for frame in $(ls "$FRAME_DIR" | sort -n); do
    clear
    
    for (( i=0; i<top; i++ )); do
      echo
    done
    
    cat "$FRAME_DIR/$frame"
    sleep "$sleep_time"
  done
done
