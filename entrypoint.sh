#!/bin/bash
set -e

export DISPLAY=:99
export XAUTHORITY=/home/playwright/.Xauthority

# Clean up possible old sockets
rm -f /tmp/.X11-unix/X99

echo "Starting Xorg server..."
Xorg -noreset +extension GLX +extension RANDR +extension RENDER -ac -listen tcp :99 &

echo "Waiting for Xorg server to be ready..."
timeout 15s bash -c 'until [ -S /tmp/.X11-unix/X99 ]; do echo "Waiting for X socket..."; sleep 0.5; done'
if [ ! -S /tmp/.X11-unix/X99 ]; then
    echo "Xorg failed to start, see /home/playwright/Xorg.99.log"
    cat /home/playwright/Xorg.99.log
    exit 1
fi
echo "Xorg server is ready."

# (Optional) Fix X socket permissions
sudo chown -R playwright:playwright /tmp/.X11-unix || true

echo "Starting Window Manager (XFCE4)..."
startxfce4 >/dev/null 2>&1 &

sleep 2 # Give WM a moment to start drawing

echo "Starting unclutter..."
# unclutter -idle 0.5 -root &  # Disable or set a higher timeout for now

echo "Starting VNC server (x11vnc)..."
x11vnc -display :99 -forever -nopw -noshm -listen 0.0.0.0 -rfbport 5900 -solid black -xfixes -cursor_drag &> /home/playwright/x11vnc.log &

echo "Waiting for VNC server (port 5900)..."
timeout 30s bash -c 'until echo > /dev/tcp/localhost/5900; do echo "waiting for VNC..."; sleep 0.5; done 2>/dev/null'
echo "VNC server is ready."

# Start noVNC Web Client Proxy immediately after VNC is ready
echo "Starting noVNC proxy..."
/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 0.0.0.0:7900 --web /opt/novnc &
sleep 2

# Start FastAPI application early (it can handle Chromium connection later)
echo "Starting FastAPI application..."
cd /home/playwright
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 3000 &
sleep 3

# Now try to start Chromium in the background (non-blocking)
echo "Starting Chromium Browser (in background)..."
chromium-browser --no-sandbox --disable-dev-shm-usage --disable-gpu --disable-software-rasterizer --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0 --window-size=1280,800 --display=:99 &> /home/playwright/chromium.log &

echo "All essential services started. Chromium will start in background."
echo "noVNC: http://localhost:7900"
echo "FastAPI: http://localhost:3000"

# Keep the container running
tail -f /dev/null
