#!/bin/bash

# attempt at making rendering faster by only updating the parts where there is an animation.

FRAME_DIR="/tmp/anifetch/output"

# Gracefully handle Ctrl+C
# TODO: the cursor should be placed at end when the user does ctrl + c
trap "echo -e '\nExiting...'; exit 0" SIGINT

# Check for FRAMERATE input
if [ $# -ne 5 ]; then
  echo "Usage: <framerate> <top> <left> <right> <bottom>"
  exit 1
fi

framerate=$1
top=$2
left=$3
right=$4
bottom=$5


num_lines=$((bottom - top))

# Compute 1 / FRAMERATE using bc
sleep_time=$(echo "scale=4; 1 / $framerate" | bc)

# Adjust sleep time based on number of lines
adjusted_sleep_time=$(echo "$sleep_time / $num_lines" | bc -l)

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

