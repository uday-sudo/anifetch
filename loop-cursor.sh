#!/bin/bash

# attempt at making rendering faster by only updating the parts where there is an animation.

FRAME_DIR="/tmp/anifetch/output"

# Gracefully handle Ctrl+C
# TODO: the cursor should be placed at end when the user does ctrl + c
trap "echo -e '\nExiting...'; exit 0" SIGINT

framerate=$1
top=$2
left=$3
right=$4
bottom=$5


# Check for FRAMERATE input
if [ $# -ne 5 ]; then
  echo "Usage: <framerate> <top> <left> <right> <bottom>"
  exit 1
fi

# Compute 1 / FRAMERATE using bc
sleep_time=$(echo "scale=4; 1 / $framerate" | bc)

# Hide cursor
tput civis
trap "tput cnorm; tput cup $(tput lines) 0; exit" INT

# Optional: print static template here (once)
clear

for (( i=0; i<top; i++ )); do
  echo
done

cat "/tmp/anifetch/template.txt"

###############################

# Main loop
while true; do
  for frame in $(ls "$FRAME_DIR" | sort -n); do
    current_top=$top
    while IFS= read -r line; do
    tput cup "$current_top" "$left"
    echo -ne "$line"
    current_top=$((current_top + 1))
    if [[ $current_top -gt $bottom ]]; then
        break
    fi
    done < "$FRAME_DIR/$frame"


    sleep "$sleep_time"
    top=$2  # Reset vertical position
  done
done
