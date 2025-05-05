#!/bin/bash

# attempt at making rendering faster by only updating the parts where there is an animation.

FRAME_DIR="/tmp/anifetch/output"

#trap "echo -e '\nExiting...'; exit 0" SIGINT

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

# TODO: the cursor should be placed at end when the user does ctrl + c
trap "tput cnorm; if [ -t 0 ]; then stty echo; fi; tput sgr0; tput cup $(tput lines) 0; exit 0" SIGINT

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
        echo "$adjusted_sleep_time" | awk '{system("sleep " $1)}'
    done < "$FRAME_DIR/$frame"

    top=$2  # Reset vertical position
  done
done
