#!/bin/bash
set -e
echo "🖥️ Starting VNC-enabled Playwright MCP Environment..."

# 1. Clean up previous X server lock files for a clean start.
rm -f /tmp/.X99-lock

# 2. Start the virtual display (Xvfb) in the background.
export DISPLAY=:99
Xvfb $DISPLAY -screen 0 1280x720x24 -ac +extension GLX +render -noreset &
sleep 5

# 3. Start the window manager and VNC servers.
fluxbox &
x11vnc -display $DISPLAY -nopw -forever -shared -bg
websockify --web /opt/noVNC 7900 localhost:5900 &

echo "✅ VNC server ready on port 5900"
echo "🌐 Web VNC available at: http://localhost:7900"
sleep 2

# Install Chrome browser for Playwright
# npx playwright install chrome

# Start the Playwright MCP Server with default port 8831 and no sandbox mode
echo "🎭 Starting Playwright MCP server..."
npx @playwright/mcp@latest \
    --port ${PLAYWRIGHT_MCP_PORT:-8831} \
    --host 0.0.0.0 \
    --no-sandbox \
    --cors-origins "http://localhost:3001" &

# Wait for the MCP server to be ready with a timeout of 60 seconds
echo "⏳ Waiting for MCP server to be ready..."
timeout=60
while ! curl -s -o /dev/null "http://localhost:${PLAYWRIGHT_MCP_PORT:-8831}/mcp"; do
    if [ $timeout -le 0 ]; then
        echo "❌ Timed out waiting for MCP server to start."
        exit 1
    fi
    sleep 1
    timeout=$((timeout-1))
done
echo "✅ MCP Server is ready."

# Run the client script to interact with the browser
echo "🚀 Running client script to control the browser..."
node ./startup-browser.js &

# 7. Keep the container running.
echo "✅ Setup complete. Container is running and browser should be visible in VNC."
tail -f /dev/null
