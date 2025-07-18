# Technical Specification: Asynchronous Mouse & Coordinate Service

## 1. Overview

This document provides a detailed technical specification for two critical, interconnected components:

1.  **The `MouseService`:** An asynchronous wrapper around `pyautogui` that provides safe and non-blocking mouse control.
2.  **The Coordinate Retrieval System:** The logic within the `BrowserService` that uses Playwright to find the precise on-screen coordinates of a web page element.

Together, these components allow an AI agent to reliably and visibly interact with a GUI. The `BrowserService` answers the question, "**Where is the button?**" and the `MouseService` answers the command, "**Click that button.**"

## 2. The `MouseService`: The "Hands"

### 2.1. High-Level Purpose

The `MouseService` module acts as a **safe and asynchronous abstraction layer** on top of the `pyautogui` library. Its primary purpose is to translate high-level commands (e.g., "click at x, y") into low-level, visible mouse actions on the screen, without blocking the main application's event loop.

### 2.2. Core Problem: Synchronous Blocking

`pyautogui` is a powerful but fundamentally **synchronous** library. A command like `pyautogui.moveTo(x, y, duration=2)` will halt the execution of the Python script for the full 2 seconds it takes the mouse to move.

In a modern asynchronous application (like our FastAPI server), this is catastrophic. A blocking call would freeze the entire server, making it unable to respond to any other requests. The core design challenge is to use this blocking library in a non-blocking way.

### 2.3. Key Design Choices & Rationale

**Choice 1: Bridge to Asynchronicity with `asyncio.to_thread`**

This is the most critical architectural decision.

*   **What was done:** All methods in the service (`move_to`, `click_at`, etc.) are defined as `async def`. However, inside these methods, the synchronous `pyautogui` functions are not called directly. They are wrapped in `asyncio.to_thread()`.
*   **Why:** `asyncio.to_thread()` runs the blocking `pyautogui` function in a separate worker thread. This frees the main asyncio event loop to continue handling other tasks, keeping the server responsive while the mouse is moving. **This is the correct and required pattern for using any blocking library within an asyncio application.**

**Choice 2: Prioritizing Safety and Reliability**

*   **What was done:** The service configures `pyautogui`'s built-in safety features upon initialization.
    ```python
    class MouseService:
        def __init__(self):
            # Emergency Stop: Move mouse to a screen corner to abort.
            pyautogui.FAILSAFE = True
            # Universal Pause: Add a small delay after every action.
            pyautogui.PAUSE = 0.1
    ```
*   **Why:**
    *   `FAILSAFE = True` is a critical emergency brake. If a script goes haywire, slamming the mouse into a corner of the screen will raise an exception and stop the program.
    *   `PAUSE = 0.1` adds a tiny 100ms delay after every `pyautogui` action. This prevents the script from sending commands to the OS faster than it can process them, which makes the automation significantly more reliable.

## 3. The Coordinate Retrieval System: The "Eyes"

### 3.1. How Coordinates are Fetched

The `MouseService` only knows *how* to move and click; it has no concept of what a "button" is. The intelligence to find the coordinates of an element resides in the `BrowserService` and relies entirely on **Playwright**.

Here is the step-by-step process:

1.  **Receive a Selector:** The process begins when an API endpoint (e.g., `/mouse/click`) receives a request containing a CSS selector, like `{"selector": "button[data-key='CF']"}`.

2.  **Locate the Element:** The `BrowserService` uses Playwright's `page.locator(selector).first` to find the web element on the page. Using `.first` ensures we only get one element if the selector happens to match multiple.

3.  **Get the Bounding Box:** The most crucial step is calling `element_handle.bounding_box()`.
    *   This Playwright method returns a dictionary containing the element's position and size *relative to the top-left corner of the browser's viewport (the visible part of the web page)*.
    *   The returned object looks like this: `{'x': 150.5, 'y': 300, 'width': 80, 'height': 40}`.

4.  **Calculate the Center Point:** The `MouseService` should click in the middle of the button, not at its top-left corner. The `BrowserService` performs a simple calculation to find this center point:
    *   `center_x = bounding_box['x'] + (bounding_box['width'] / 2)`
    *   `center_y = bounding_box['y'] + (bounding_box['height'] / 2)`

5.  **Return Absolute Coordinates:** The `BrowserService` returns these calculated `center_x` and `center_y` coordinates. These are now absolute pixel values ready for `pyautogui` to use.

### 3.2. Why This Approach is Superior

*   **Accuracy:** It is pixel-perfect. Unlike visual AI models that guess coordinates from an image, Playwright has direct access to the browser's rendering engine and provides mathematically exact positions.
*   **Reliability:** It is not affected by screen resolution, browser zoom level, or minor visual changes to the website. As long as the CSS selector remains valid, the coordinates will be correct.
*   **Decoupling:** This design enforces a clean separation of concerns:
    *   `BrowserService`: Knows **what** things are and **where** they are.
    *   `MouseService`: Knows **how** to physically interact with a location.

## 4. Summary for Future Projects

*   **Mistake to Avoid:** Never try to guess coordinates with visual AI when you have programmatic access to the UI's structure.
*   **Best Practice:** Always separate the logic for *finding* an element from the logic for *interacting* with it.
*   **Asynchronous Rule:** If a library blocks, wrap its calls in `asyncio.to_thread` when using it in an async-native framework like FastAPI.
*   **Safety First:** Always enable `FAILSAFE` and a default `PAUSE` when using `pyautogui`. 