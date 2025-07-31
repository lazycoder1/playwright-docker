#!/usr/bin/env python3
"""
Simple cursor visibility test script.
Run this inside the Docker container to test if the cursor is visible in noVNC.
"""

import pyautogui
import time
import sys

def test_cursor_visibility():
    """Test script to verify cursor visibility in noVNC"""
    print("🖱️  Testing cursor visibility...")
    print("👀 Watch the noVNC window at http://localhost:7900")
    print("⏰ Starting in 3 seconds...")
    
    time.sleep(3)
    
    # Disable failsafe for testing
    pyautogui.FAILSAFE = False
    
    # Get screen size
    screen_width, screen_height = pyautogui.size()
    print(f"📺 Screen size: {screen_width}x{screen_height}")
    
    # Test 1: Move to corners
    print("🔄 Test 1: Moving to screen corners...")
    corners = [
        (50, 50),                           # Top-left
        (screen_width-50, 50),              # Top-right  
        (screen_width-50, screen_height-50), # Bottom-right
        (50, screen_height-50),             # Bottom-left
        (screen_width//2, screen_height//2)  # Center
    ]
    
    for i, (x, y) in enumerate(corners, 1):
        print(f"  {i}. Moving to ({x}, {y})...")
        pyautogui.moveTo(x, y, duration=1.0)
        time.sleep(0.5)
    
    # Test 2: Draw a circle
    print("🔄 Test 2: Drawing a circle...")
    import math
    center_x, center_y = screen_width//2, screen_height//2
    radius = 100
    
    for angle in range(0, 360, 10):
        x = center_x + radius * math.cos(math.radians(angle))
        y = center_y + radius * math.sin(math.radians(angle))
        pyautogui.moveTo(x, y, duration=0.1)
    
    # Test 3: Click test
    print("🔄 Test 3: Click test at center...")
    pyautogui.moveTo(center_x, center_y, duration=1.0)
    pyautogui.click()
    print("✅ Click performed!")
    
    print("🎉 Cursor visibility test completed!")
    print("💡 If you could see the mouse moving in noVNC, the fix worked!")

if __name__ == "__main__":
    try:
        test_cursor_visibility()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1) 