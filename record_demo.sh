#!/bin/bash

# Start ffmpeg screen recording
ffmpeg -video_size 1920x1080 -framerate 30 -f x11grab -i :0.0 -c:v libx264 admin_dashboard_demo.mp4 &
echo $! > recording_pid.txt

# Wait for 5 minutes
sleep 300

# Stop recording
kill $(cat recording_pid.txt)
rm recording_pid.txt
