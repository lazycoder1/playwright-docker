# 📄 Spec Sheet — Hybrid Automation Agent (`pyautogui` + `Playwright`)

## 1. ✨ Purpose

To build a Dockerized environment that serves a custom automation API. This API allows an external AI agent to control a headful browser with truly **human-like interactions**, including smooth mouse movements and visible keyboard typing. The system is designed to provide rich contextual information, enabling the agent to navigate complex web applications like HubSpot.

## 2. 🧱 Core Architecture: "Eyes" and "Hands"

This system uses a hybrid model that separates the ability to "see" from the ability to "act."

-   **The Eyes (Playwright):** A Playwright instance runs inside the container, connected to a headful browser. Its sole purpose is to inspect the DOM, find elements, and read their properties and coordinates. It is our source of truth for the state of the web page.
-   **The Hands (`pyautogui`):** This library has direct control over the container's operating system GUI. It moves the *real OS mouse cursor*, performs clicks, and types on the keyboard, making its actions visible, smooth, and human-like.

```txt
+--------------+       +-------------------------+       +----------------------+
|  AI Agent 🧠 | <---> | Custom Automation API 🐍 | ---> | PyAutoGUI (Hands) 🖱️ |
| [HTTP Client]|       |   (FastAPI Server)      |       | [Controls OS Cursor] |
+--------------+       +-------------------------+       +----------------------+
                                |      ^
      (Sense: "What's on           |      | (Act: "Click this")
       the page?")        (Inspects)v      |
                       +-------------------------+
                       | Playwright (Eyes) 👁️    |
                       | [Finds elements in      |
                       |  headful browser]       |
                       +-------------------------+
```

## 3. 🖥️ GUI Streaming Explained: How noVNC Works

The GUI is not magic; it's a chain of four components that bring the container's virtual desktop to your browser.

1.  **Xvfb (X Virtual Framebuffer):** This is the foundation. It creates an in-memory virtual screen. The browser application renders its windows, buttons, and pages onto this invisible screen, thinking it's a real monitor.
2.  **Fluxbox (Window Manager):** A lightweight window manager runs on top of Xvfb. Its job is to draw the title bars, borders, and manage window placement (e.g., maximizing the browser) within the virtual screen.
3.  **x11vnc (VNC Server):** This program constantly reads the pixel data from the Xvfb framebuffer and serves it using the standard VNC protocol.
4.  **noVNC (Web Client + Proxy):** This is the final piece. It runs a small web server providing an HTML/JavaScript VNC client that you access in your browser. Its `websockify` component acts as a bridge, translating the WebSocket traffic from your browser into the raw TCP traffic the x11vnc server understands.

```txt
[ Browser App ] → Renders to → [ Xvfb Virtual Screen ] → Managed by → [ Fluxbox ]
                                       ↑
                                       | (Pixel data is read by)
                                       ↓
     (Web Browser) ← HTTP/WS → [ noVNC / Websockify ] ← TCP → [ x11vnc Server ]
```

## 4. 📦 API-Driven Interaction Loop

The agent follows a **Sense -> Decide -> Act** loop via simple HTTP requests.

1.  **Sense:** The agent calls a "sensing" endpoint like `GET /context/interactive_elements` to get a structured JSON list of everything it can interact with on the page.
2.  **Decide:** The agent's logic processes this JSON to decide its next action (e.g., "I need to click the button with the text 'Log In'").
3.  **Act:** The agent calls an "action" endpoint like `POST /actions/click` with the element's selector to have `pyautogui` perform the physical interaction.

## 5. 🔧 Components

### 5.1 Dockerfile

-   **Base image**: `python:3.11-slim`
-   **System Dependencies**:
    -   `python3`, `nodejs`, `npm`: Core runtimes.
    -   `xvfb`, `fluxbox`, `x11vnc`, `novnc`: The complete GUI streaming stack.
    -   `scrot`, `python3-tk`, `libx11-dev`, `libxtst-dev`: Critical libraries for `pyautogui` to control the X server.
-   **Python Dependencies (`requirements.txt`)**: `playwright`, `pyautogui`, `fastapi`, `uvicorn[standard]`.
-   **Build Steps**:
    1.  Install all `apt-get` system dependencies.
    2.  Install Python dependencies via `pip`.
    3.  Run `npx playwright install --with-deps` to download browser binaries.
    4.  Copy the application code (`app/`, `entrypoint.sh`, etc.) into the container.
    5.  Set the `entrypoint.sh` as the startup command.

### 5.2 `entrypoint.sh`

A shell script that orchestrates the container's startup sequence in the correct order.

```bash
#!/bin/bash

# 1. Start the virtual screen on display :0
Xvfb :0 -screen 0 1280x720x16 &

# 2. Start the window manager
fluxbox &

# 3. Start the VNC server, pointing to the virtual display
x11vnc -display :0 -nopw -listen localhost -forever &

# 4. Start the noVNC WebSocket proxy, bridging the web port to the VNC server
/usr/share/novnc/utils/launch.sh --listen 7900 --vnc localhost:5900 &

# 5. Launch the browser in a maximized/kiosk state.
# This is CRITICAL for aligning Playwright's coordinates with pyautogui's.
google-chrome --no-sandbox --start-maximized --disable-infobars &

# 6. Start our custom automation API
cd /app
uvicorn main:app --host 0.0.0.0 --port 8080
```

### 5.3 Directory Structure

```
playwright-mcp-docker/
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
├── app/
│   ├── main.py              # FastAPI app setup and endpoints
│   ├── services/
│   │   ├── browser_service.py # "Eyes": Playwright logic
│   │   └── mouse_service.py   # "Hands": PyAutoGUI logic
│   └── models.py            # Pydantic models for API requests
├── docs/
│   └── SETUP.md
└── README.md
```

## 6. 🔌 API Endpoint Specification

The server exposes a RESTful API. All endpoints are fully documented via OpenAPI at `http://localhost:8080/docs`.

---

### 6.1 Sensing Endpoints (The "Eyes")

#### **`GET /context/interactive_elements`**
Returns a structured list of all visible, interactable elements on the page. This is the primary "sense" for the agent.

-   **Response `200 OK`:**
    ```json
    {
      "url": "https://app.hubspot.com/login",
      "elements": [
        {
          "selector": "input[id='username']",
          "text": null,
          "aria_label": "Email address",
          "role": "textbox"
        },
        {
          "selector": "input[id='password']",
          "text": null,
          "aria_label": "Password",
          "role": "textbox"
        },
        {
          "selector": "button[data-test-id='login-button']",
          "text": "Log In",
          "aria_label": null,
          "role": "button"
        },
        {
          "selector": "a[href*='google.com/a/hubspot.com']",
          "text": "Sign in with Google",
          "aria_label": null,
          "role": "link"
        }
      ]
    }
    ```

#### **`GET /page/url`**
Gets the current URL of the page.

-   **Response `200 OK`:**
    ```json
    {
      "url": "https://app.hubspot.com/dashboard"
    }
    ```

#### **`GET /page/screenshot`**
Captures a PNG of the current page view.

-   **Response `200 OK`:** The raw `image/png` data.

---

### 6.2 Action Endpoints (The "Hands")

#### **`POST /actions/navigate`**
Navigates the browser to a new URL.

-   **Request Body:**
    ```json
    {
      "url": "https://google.com"
    }
    ```
-   **Response `200 OK`:**
    ```json
    {
      "status": "navigation_successful",
      "url": "https://google.com"
    }
    ```

#### **`POST /actions/click`**
Finds an element, moves the OS cursor smoothly to it, and performs a click.

-   **Request Body:**
    ```json
    {
      "selector": "button[data-test-id='login-button']"
    }
    ```
-   **Response `200 OK`:**
    ```json
    {
      "status": "click_successful"
    }
    ```
-   **Response `404 Not Found`:**
    ```json
    {
      "detail": "Element not found for selector: button[data-test-id='login-button']"
    }
    ```

#### **`POST /actions/type`**
Finds an element, clicks it to focus, and types text with human-like delays.

-   **Request Body:**
    ```json
    {
      "selector": "input[id='username']",
      "text": "agent@example.com"
    }
    ```
-   **Response `200 OK`:**
    ```json
    {
      "status": "type_successful"
    }
    ```

#### **`POST /actions/scroll`**
Scrolls the main page window up or down.

-   **Request Body:**
    ```json
    {
      "direction": "down"
    }
    ```
-   **Response `200 OK`:**
    ```json
    {
      "status": "scroll_successful"
    }
    ```

---
## 7. 🚀 Build & Run

### Build Docker Image
```bash
docker build -t playwright-hybrid-agent .
```

### Run Container
```bash
docker run -it --rm -p 8080:8080 -p 7900:7900 --shm-size=2g playwright-hybrid-agent
```
*Note: `--shm-size=2g` is recommended to prevent browser crashes in memory-intensive applications.*

### Access
-   **Automation API Docs**: `http://localhost:8080/docs`
-   **GUI via Web**: `http://localhost:7900` 