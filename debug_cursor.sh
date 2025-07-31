#!/bin/bash
# Cursor debugging script - run this inside the Docker container
echo "🔍 Debugging cursor visibility..."

echo "1. Checking X11 display:"
echo "   DISPLAY: $DISPLAY"
echo "   X server running: $(ps aux | grep Xvfb | grep -v grep | wc -l) processes"

echo "2. Checking cursor environment:"
echo "   XCURSOR_THEME: $XCURSOR_THEME"
echo "   XCURSOR_SIZE: $XCURSOR_SIZE"
echo "   XCURSOR_PATH: $XCURSOR_PATH"

echo "3. Checking available cursor themes:"
ls -la /usr/share/icons/*/cursors/ 2>/dev/null | head -10

echo "4. Checking VNC process:"
ps aux | grep x11vnc | grep -v grep

echo "5. Testing cursor commands:"
echo "   Setting cursor with xsetroot..."
xsetroot -cursor_name left_ptr 2>&1

echo "6. Checking window manager:"
ps aux | grep xfce | grep -v grep

echo "7. Manual cursor fixes (run if needed):"
echo "   export XCURSOR_THEME=Adwaita"
echo "   export XCURSOR_SIZE=24"
echo "   xsetroot -cursor_name left_ptr"
echo "   # or try: xsetroot -cursor_name arrow"
echo "   # or try: xsetroot -cursor_name hand1"

echo "🔧 You can also try restarting x11vnc with:"
echo "   pkill x11vnc"
echo "   x11vnc -display :99 -forever -shared -rfbauth /home/playwright/.vncpass -cursor most -cursorpos &" 