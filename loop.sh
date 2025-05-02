#!/bin/bash

FRAME_DIR="/tmp/anifetch/output"
FRAMERATE = $1
TOP = $2
LEFT = $3
RIGHT = $4
BOTTOM = $5

# Compute 1 / FRAMERATE using bc
SLEEP_TIME = $(echo "scale=4; 1 / $FRAMERATE" | bc)

while true; do
  for frame in $(ls "$FRAME_DIR" | sort -n); do
    clear

    # Use -e to interpret ANSI escape codes
    cat "$FRAME_DIR/$frame"
    sleep $SLEEP_TIME
  done
done
