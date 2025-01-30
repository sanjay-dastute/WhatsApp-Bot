#!/bin/bash

# Function to capture screenshot
capture_screenshot() {
    local name=$1
    import -window root "screenshots/${name}.png"
}

# Capture login page
capture_screenshot "01_login"
sleep 2

# Capture dashboard
capture_screenshot "02_dashboard"
sleep 2

# Capture members view
capture_screenshot "03_members"
sleep 2

# Capture filtered view
capture_screenshot "04_filtered"
sleep 2

# Capture export
capture_screenshot "05_export"
sleep 2

# Create video from screenshots
convert -delay 100 -loop 0 screenshots/*.png admin_dashboard_demo.gif

echo "Demo captured and saved as admin_dashboard_demo.gif"
