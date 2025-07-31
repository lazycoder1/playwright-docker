# 🛠️ Setup and Technical Documentation

This document provides a deeper dive into the technical components and setup of the Hybrid Automation Agent.

## 1. 📦 Core Components

### 1.1 Dockerfile
-   **Base Image**: `python:3.11-slim`
-   **Core Runtimes**: `python3`, `nodejs`, `npm`
-   **GUI Stack**:
    -   `xvfb`: In-memory virtual screen.
    -   `fluxbox`: Lightweight window manager.
    -   `x11vnc`: VNC server to stream the framebuffer.
    -   `novnc`: Web-based VNC client and WebSocket proxy.
-   **Automation Libraries**:
    -   `pyautogui` dependencies: `scrot`, `python3-tk`, `libx11-dev`, `libxtst-dev`.
    -   `playwright`: For browser automation and DOM inspection.
-   **Python Application**: `fastapi`, `uvicorn`.

### 1.2 `entrypoint.sh`
This script orchestrates the container's startup sequence. It is the `ENTRYPOINT` of the Docker image and performs the following steps in order:
1.  **Start Xvfb**: Creates the virtual display `:0` with a resolution of 1280x720.
2.  **Start Fluxbox**: Runs the window manager on the virtual display.
3.  **Start x11vnc**: Starts the VNC server, listening on localhost and connected to the Xvfb display.
4.  **Start noVNC**: Launches the `websockify` proxy to bridge WebSocket connections on port `7900` to the VNC server's TCP port.
5.  **Launch Browser**: Opens Google Chrome in a maximized state to fill the virtual screen. This is critical for ensuring coordinate alignment between Playwright and PyAutoGUI.
6.  **Start API Server**: Launches the `uvicorn` server to serve the FastAPI application on port `8080`.

## 2. 🚀 Build and Run

### Prerequisites
-   [Docker](https://www.docker.com/get-started) installed on your local machine.

### Step 1: Build the Docker Image
Navigate to the root of the `playwright-docker` directory and run the build command. This will download the base image, install all dependencies, and copy the application code.

```bash
docker build -t playwright-hybrid-agent .
```

### Step 2: Run the Docker Container
Run the container using the following command. This maps the required ports and allocates sufficient shared memory for the browser to run smoothly.

```bash
docker run -it --rm -p 8080:8080 -p 7900:7900 --shm-size=2g playwright-hybrid-agent
```
-   `-p 8080:8080`: Maps the FastAPI application port.
-   `-p 7900:7900`: Maps the noVNC web client port.
-   `--shm-size=2g`: Provides 2GB of shared memory to the container, which is recommended for browser stability.

### Step 3: Access the Services
Once the container is running, you can access the following resources:
-   **API Documentation (Swagger UI)**: Open your browser to `http://localhost:8080/docs`.
-   **Live GUI Stream**: Open your browser to `http://localhost:7900/`.

## 3. 🔌 API Specification
The API is documented via OpenAPI and is accessible at the `/docs` endpoint. For a detailed list of endpoints and their request/response models, please refer to the live documentation provided by the running application.
