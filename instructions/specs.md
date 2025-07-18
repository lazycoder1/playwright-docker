# 📄 Spec Sheet — Playwright MCP with Visual Overlays

## 1. ✨ Purpose

To build a Dockerized environment that runs a standard **Playwright MCP Server** and enhances it with **JavaScript-based visual overlays**. This provides a GUI-accessible, headful browser where an external AI agent's actions (mouse movements, clicks, typing) are made clearly visible for observation and debugging.

## 2. 🧱 Core Architecture: MCP Server + JS Injection

This architecture uses the standard Playwright server and intercepts its commands to inject visual feedback into the browser session.

-   **Playwright MCP Server:** The core of the system. It listens for commands from a standard Playwright client library (e.g., in Python or Node.js) and executes them against the browser.
-   **Command Interception (`mcp_customization.py`):** A custom Python script that acts as a middleware layer. It catches outgoing Playwright commands, injects custom JavaScript into the page to create a visual effect (like moving a fake cursor), and then allows the original command to proceed.
-   **JavaScript Overlays (`browser_scripts/`):** These are JS files injected into the browser. They are responsible for rendering and animating the fake cursor, click effects, and keyboard feedback directly in the DOM.

```txt
+--------------+       +-------------------------+       +----------------------+
|  AI Agent 🧠 | <---> | Playwright MCP Server 🔁 | <---> | Headful Browser 🧭   |
| [PW Client]  |       | [Intercepted Commands]  |       | [GUI + JS Overlays]  |
+--------------+       +-------------------------+       +----------------------+
                               ↑
                               | (GUI Stream)
                               v
                   +-----------------------+
                   | noVNC 🖥️              |
                   | GUI Stream to Browser |
                   +-----------------------+
```

## 3. 🖥️ GUI Streaming Explained: How noVNC Works

The GUI is a chain of components that bring the container's virtual desktop to your browser.

1.  **Xvfb (X Virtual Framebuffer):** Creates an in-memory virtual screen.
2.  **Fluxbox (Window Manager):** Manages window placement (e.g., maximizing the browser) within the virtual screen.
3.  **x11vnc (VNC Server):** Reads the pixel data from the Xvfb framebuffer and serves it using the VNC protocol.
4.  **noVNC (Web Client + Proxy):** Provides an HTML/JavaScript VNC client in your browser and uses `websockify` to connect to the x11vnc server.

## 4. 🔧 Components

### 4.1 Dockerfile

-   **Base image**: `python:3.11-slim`
-   **System Dependencies**:
    -   `python3`, `nodejs`, `npm`: Core runtimes.
    -   `xvfb`, `fluxbox`, `x11vnc`, `novnc`: The complete GUI streaming stack.
-   **Python Dependencies (`requirements.txt`)**: `playwright`.
-   **Build Steps**:
    1.  Install all `apt-get` system dependencies.
    2.  Install Python dependencies via `pip`.
    3.  Run `npx playwright install --with-deps` to download browser binaries.
    4.  Copy all project scripts (`playwright_config/`, `browser_scripts/`, etc.) into the container.
    5.  Set the `entrypoint.sh` as the startup command.

### 4.2 `entrypoint.sh`

Orchestrates the startup sequence. Launches the Playwright server with a custom initialization script.

```bash
#!/bin/bash

# 1. Start GUI components (Xvfb, fluxbox, x11vnc, noVNC)
Xvfb :0 -screen 0 1280x720x16 &
fluxbox &
x11vnc -display :0 -nopw -listen localhost -forever &
/usr/share/novnc/utils/launch.sh --listen 7900 --vnc localhost:5900 &

# 2. Launch the Playwright Server
# The key is to launch it via a Python script that can apply our patches.
# This starts the server and our customization logic.
python /app/playwright_config/launch_server.py
```

### 4.3 `playwright_config/launch_server.py`

This script starts the Playwright server programmatically and attaches the interception logic.

```python
# pseudo-code
import asyncio
from playwright.server import run

async def main():
    # The server is started with a "pre-dispatch" hook
    await run(
        port=8080,
        host='0.0.0.0',
        pre_dispatch_hook=mcp_customization.intercept_command
    )

asyncio.run(main())
```

### 4.4 `playwright_config/mcp_customization.py`

The core logic for intercepting commands and injecting JS.

```python
# pseudo-code
async def intercept_command(dispatch_func, command, params):
    page = find_page_for_command(command) # Logic to get the page object

    if command.name == 'mouse.move':
        # Inject JS to animate the fake cursor
        await page.evaluate(f"window.animateFakeCursor({params['x']}, {params['y']})")

    elif command.name == 'mouse.click':
        # Inject JS to show a click animation
        await page.evaluate(f"window.showClickAnimation({params['x']}, {params['y']})")
    
    elif command.name == 'keyboard.type':
        # Inject JS to show typed text
        await page.evaluate(f"window.showKeyboardInput('{params['text']}')")

    # Finally, allow the original command to execute
    return await dispatch_func(command, params)
```

### 4.5 `browser_scripts/mouse_overlay.js`

Contains the client-side JavaScript functions that are called from Python.

```javascript
// Injected into every page
window.fakeCursor = document.createElement('div');
// ... style the cursor div ...
document.body.appendChild(window.fakeCursor);

window.animateFakeCursor = (x, y) => {
    // JS logic to smoothly move the div from its current position to (x, y)
    // using CSS transitions or a library like GSAP.
};

window.showClickAnimation = (x, y) => {
    // JS logic to create a ripple or flash effect at (x, y).
};
```

## 5. 🚀 Build & Run

### Build Docker Image
```bash
docker build -t playwright-mcp-overlay .
```

### Run Container
```bash
docker run -it --rm -p 8080:8080 -p 7900:7900 --shm-size=2g playwright-mcp-overlay
```

### Access
-   **Playwright MCP Endpoint**: `ws://localhost:8080`
-   **GUI via Web**: `http://localhost:7900`

