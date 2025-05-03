#!/bin/bash

# attempt at making rendering faster by only updating the parts where there is an animation.

FRAME_DIR="/tmp/anifetch/output"
FRAMERATE=$1
TOP=$2
LEFT=$3
RIGHT=$4
BOTTOM=$5

# Check for FRAMERATE input
if [ $# -ne 5 ]; then
  echo "Usage: <framerate> <top> <left> <right> <bottom>"
  exit 1
fi

# Compute 1 / FRAMERATE using bc
SLEEP_TIME=$(echo "scale=4; 1 / $FRAMERATE" | bc)

# Hide cursor
tput civis
trap "tput cnorm; tput cup $(tput lines) 0; exit" INT

# Optional: print static layout here (once)
clear
cat "/tmp/anifetch/layout.txt"
# Make space for animation or leave it blank

# Main loop
while true; do
  for frame in $(ls "$FRAME_DIR" | sort -n); do
    tput cup "$TOP" "$LEFT"

    # Print frame at the specified position
    while IFS= read -r line; do
      tput cup $TOP $LEFT
      echo -ne "$line"
      TOP=$((TOP + 1))
      if [[ $TOP -gt $BOTTOM ]]; then
        break
      fi
    done < "$FRAME_DIR/$frame"

    sleep "$SLEEP_TIME"
    TOP=$2  # Reset vertical position
  done
done
