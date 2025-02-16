#!/bin/bash

# The script converts input video file to video with lower (but still pretty good)
# quality.

source colors.sh

base_name="$(basename $0)"

if [[ $# -eq 0 ]] ; then
  echo -e "${WARNING}Usage: ${GREEN}${base_name}${RESET} /path/to/video/file [hh:mm:ss [duration_in_seconds]]"
  exit 1
fi

name="$1"

if [[ $# -ge 2 ]]; then
  startTime=(${2//:/ })
  startTimeSec=$(float_eval.sh "${startTime[0]} * 3600 + ${startTime[1]} * 60 + ${startTime[2]}")

  if [[ $# -eq 2 ]]; then
    ffmpeg -i "$name" -ss $startTimeSec -c:a copy -c:v libx264 -crf 30 -preset medium ${name%.mp4}-crf30-start${startTimeSec}sec.mp4
  else
    ffmpeg -i "$name" -ss $startTimeSec -t ${3} -c:a copy -c:v libx264 -crf 30 -preset medium ${name%.mp4}-crf30-start${startTimeSec}sec-length${3}sec.mp4
  fi

  exit 0
fi

ffmpeg -i "$name" -c:a copy -c:v libx264 -crf 30 -preset medium ${name%.mp4}-crf30.mp4

exit 0
