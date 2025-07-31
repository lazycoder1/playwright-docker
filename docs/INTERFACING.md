# 🤖 Interfacing with the Hybrid Automation Agent

This guide provides detailed instructions on how to interact with the automation agent, both for visual monitoring and for programmatic control by an external AI agent or script.

## 1. 🖥️ Visual Access via Web GUI (noVNC)

The Docker container streams its virtual desktop, allowing you to watch the automation in real-time. This is essential for debugging and understanding what the agent is doing.

-   **URL**: `http://localhost:7900/`
-   **Password**: There is no password.

Simply open this URL in your web browser. You will see a live view of the container's desktop, including the Chrome browser that the agent is controlling. You can watch the mouse move, see text being typed, and observe navigations as they happen.

## 2. 🔌 Programmatic Control via REST API

The agent is controlled through a two-tiered REST API. An external agent should be programmed to make HTTP requests to these endpoints.

### Tier 1: Low-Level "Sense & Act" Loop

This tier provides granular control over the browser. It's designed for a **Sense -> Decide -> Act** loop.

1.  **Sense:** The agent first needs to understand what's on the page. It does this by calling the "eyes" endpoint.

    -   **Endpoint**: `GET /context/interactive_elements`
    -   **Description**: Returns a JSON object containing the current URL and a list of all visible, interactive elements (buttons, links, inputs, etc.). Each element includes a reliable CSS selector.
    -   **Usage**: The agent should call this to get a complete picture of its environment before making any decisions.

2.  **Decide:** Based on the list of interactive elements, the agent's internal logic decides what to do next. For example, it might identify the selector for a "Log In" button it needs to click.

3.  **Act:** The agent then calls one of the "hands" endpoints to perform a physical action.

    -   **`POST /actions/click`**: Moves the mouse to the center of an element and clicks it.
        -   **Body**: `{"selector": "your-css-selector"}`
    -   **`POST /actions/type`**: Clicks an element to focus it and then types text into it.
        -   **Body**: `{"selector": "your-css-selector", "text": "text to type"}`
    -   **`POST /actions/navigate`**: Navigates the browser to a new URL.
        -   **Body**: `{"url": "https://example.com"}`
    -   **`POST /actions/scroll`**: Scrolls the page up or down.
        -   **Body**: `{"direction": "down"}`

### Tier 2: High-Level Orchestration (MCP)

This tier provides a simpler, more powerful way to execute common, multi-step tasks. Instead of making many low-level calls, the agent can make a single call to the MCP to achieve a complex goal.

-   **Endpoint**: `POST /mcp/run_task`
-   **Description**: Executes a pre-defined, high-level task.
-   **Request Body**:
    ```json
    {
      "task_name": "name_of_the_task",
      "parameters": {
        "param1": "value1",
        "param2": "value2"
      }
    }
    ```

As of now, the primary available task is `login_to_website`.

## 3. 🚀 A Practical Walkthrough: Performing a Login

Here is a step-by-step example of how an agent would use the **high-level MCP** to log into a website. This is the recommended approach for common tasks.

Let's assume the login page has the following elements:
-   Username field: `input#username`
-   Password field: `input#password`
-   Login button: `button#login-button`

### Step 1: Navigate to the Login Page

First, the agent navigates to the login page.

```bash
curl -X POST http://localhost:8080/actions/navigate \
-H "Content-Type: application/json" \
-d '{
  "url": "https://your-login-page.com"
}'
```

### Step 2: Execute the High-Level Login Task

Next, the agent makes a single call to the MCP to perform the entire login flow.

```bash
curl -X POST http://localhost:8080/mcp/run_task \
-H "Content-Type: application/json" \
-d '{
  "task_name": "login_to_website",
  "parameters": {
    "username_selector": "input#username",
    "password_selector": "input#password",
    "login_button_selector": "button#login-button",
    "username": "your_actual_username",
    "password": "your_secret_password"
  }
}'
```

### How It Works

When the MCP receives this request, it will automatically:
1.  Use the "hands" to type the username into the element matching `input#username`.
2.  Use the "hands" to type the password into the element matching `input#password`.
3.  Use the "hands" to click the element matching `button#login-button`.
4.  Wait for the page to finish loading after the click.
5.  Return a success message with the new URL after login.

By using the MCP, the agent's logic is vastly simplified. It only needs to know the high-level task name and the required selectors, rather than managing the entire sequence of low-level actions.
