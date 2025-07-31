# 🤖 Hybrid Automation Agent

This project provides a Dockerized environment for a hybrid automation agent that combines the strengths of **Playwright** (for "seeing") and **PyAutoGUI** (for "acting"). It exposes a simple FastAPI-based API that allows an external AI agent to control a web browser with human-like interactions.

## ✨ Key Features

-   **Human-Like Interaction**: Uses `pyautogui` to control the actual OS mouse cursor and keyboard, making interactions visible, smooth, and natural.
-   **Rich Contextual Awareness**: Leverages `Playwright` to inspect the DOM, identify interactive elements, and provide structured data to the controlling agent.
-   **Dockerized & Portable**: The entire environment is self-contained in a Docker image, including a headful browser, GUI, and all necessary services.
-   **Live GUI Streaming**: A built-in noVNC server allows you to watch the automation happen in real-time from your web browser.
-   **Simple REST API**: Control the browser through a clean, well-documented FastAPI interface.

## 🧱 Architecture

The system is built on a "hybrid" model:

1.  **The Eyes (Playwright)**: A Playwright instance runs connected to a headful browser. It reads the page structure and finds element coordinates.
2.  **The Hands (PyAutoGUI)**: This library controls the operating system's GUI, moving the *real* mouse cursor and typing on the keyboard.

This separation allows for robust element detection via Playwright while achieving truly human-like input via PyAutoGUI.

## 🚀 Getting Started

For detailed setup and build instructions, please see the [SETUP.md](docs/SETUP.md) file.

1.  **Build the Docker Image**:
    ```bash
    docker build -t playwright-hybrid-agent .
    ```

2.  **Run the Docker Container**:
    ```bash
    docker run -it --rm -p 8080:8080 -p 7900:7900 --shm-size=2g playwright-hybrid-agent
    ```

3.  **Access the Services**:
    -   **API Documentation (OpenAPI)**: [http://localhost:8080/docs](http://localhost:8080/docs)
    -   **Live GUI Stream (noVNC)**: [http://localhost:7900/](http://localhost:7900/)

## ⚙️ API Usage

The agent interacts with the system by calling the exposed API endpoints. The general flow is:

1.  **Sense**: Call `GET /context/interactive_elements` to see what's on the page.
2.  **Decide**: Your agent's logic determines which element to interact with.
3.  **Act**: Call an action endpoint like `POST /actions/click` or `POST /actions/type` to perform the interaction.
