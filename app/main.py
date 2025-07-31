from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .services.browser_service import browser_service
from .services.mouse_service import mouse_service
from .services.mcp_service import mcp_service
from .models import (
    NavigateRequest,
    ClickRequest,
    TypeRequest,
    ScrollRequest,
    FindElementByTextRequest,
    FindElementByTextResponse,
    InteractiveElementsResponse,
    MCPTaskRequest,
    HighlightRequest,
)

app = FastAPI(
    title="Hybrid Automation API",
    description="An API for controlling a headful browser with human-like interactions, using a combination of Playwright and PyAutoGUI.",
    version="1.0.0",
)

# Add CORS middleware to allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initializes the browser service when the application starts."""
    await browser_service.launch_browser()

@app.on_event("shutdown")
async def shutdown_event():
    """Closes the browser service when the application shuts down."""
    await browser_service.close_browser()

@app.get("/api/status", summary="Get API status")
async def get_api_status():
    """
    Returns the current status of the API and services.
    Used by the frontend to check if the backend is running and accessible.
    """
    try:
        # Check if browser service is running
        current_url = await browser_service.get_current_url()
        return {
            "status": "running",
            "message": "Backend is operational",
            "services": {
                "browser": "active",
                "current_url": current_url
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "partial",
            "message": "Backend running but browser service unavailable",
            "services": {
                "browser": "inactive"
            },
            "error": str(e),
            "version": "1.0.0"
        }

@app.get(
    "/context/interactive_elements",
    response_model=InteractiveElementsResponse,
    summary="Get all interactive elements",
)
async def get_interactive_elements():
    """
    Retrieves a structured list of all visible, interactable elements on the current page.
    This serves as the primary 'sense' function for the AI agent.
    """
    return await browser_service.get_interactive_elements()


@app.post(
    "/context/find_element_by_text",
    response_model=FindElementByTextResponse,
    summary="Find a single element by its text",
)
async def find_element_by_text(request: FindElementByTextRequest):
    """
    Finds a single interactive element by its exact text content.
    This is a more targeted way for the agent to find specific elements
    like buttons or links before deciding to click them.
    """
    result = await browser_service.find_element_by_text(request.text)
    if not result["found"]:
        raise HTTPException(
            status_code=404, detail=f"Element with text '{request.text}' not found"
        )
    return result


@app.get("/page/url", summary="Get current page URL")
async def get_page_url():
    """Returns the current URL of the browser's active page."""
    return {"url": await browser_service.get_current_url()}

@app.get("/page/screenshot", summary="Capture a screenshot")
async def get_page_screenshot():
    """
    Captures a screenshot of the current browser view.
    Returns the image as raw PNG data.
    """
    return await browser_service.get_screenshot()

@app.post("/actions/navigate", summary="Navigate to a URL")
async def navigate(request: NavigateRequest):
    """
    Navigates the browser to the specified URL.
    """
    await browser_service.navigate(request.url)
    return {"status": "navigation_successful", "url": request.url}









@app.post("/actions/scroll", summary="Scroll the page")
async def scroll_page(request: ScrollRequest):
    """
    Scrolls the page up or down.
    """
    try:
        await mouse_service.scroll(request.direction)
        return {"status": "scroll_successful", "direction": request.direction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/actions/highlight_css", summary="Highlight an element using CSS styling")
async def highlight_element_css(request: HighlightRequest):
    """
    Highlights an element using CSS styling instead of mouse movement.
    More reliable when mouse automation is not available or working properly.
    Supports different highlight styles: border, background, or shadow.
    """
    try:
        result = await browser_service.highlight_element_css(
            request.selector, 
            request.duration, 
            request.style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/actions/click_dom", summary="Click an element using DOM interaction")
async def click_element_dom(request: ClickRequest):
    """
    Clicks an element using pure Playwright DOM interaction instead of mouse automation.
    More reliable when OS mouse automation is not available or working properly.
    This method works directly with the DOM and doesn't require physical mouse movement.
    """
    try:
        result = await browser_service.click_element_dom(request.selector)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/debug/element_visibility", summary="Debug element visibility issues")
async def debug_element_visibility(request: ClickRequest):
    """
    Debug why an element might not be clickable.
    Returns detailed information about element state and actionability.
    """
    try:
        result = await browser_service.debug_element_visibility(request.selector)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/actions/click_dom_force", summary="Force click an element using multiple strategies")
async def click_element_dom_force(request: ClickRequest):
    """
    Force click an element using multiple strategies when standard clicking fails.
    Tries different approaches including scrolling, force click, and JavaScript click.
    """
    try:
        result = await browser_service.click_element_dom_force(request.selector)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/actions/type_dom", summary="Type text using DOM interaction")
async def type_into_element_dom(request: TypeRequest):
    """
    Types text into an element using pure Playwright DOM interaction instead of mouse automation.
    More reliable when OS mouse automation is not available or working properly.
    This method works directly with the DOM and doesn't require physical mouse movement or keyboard simulation.
    """
    try:
        result = await browser_service.type_into_element_dom(request.selector, request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/mcp/run_task", summary="Run a high-level orchestrated task")
async def run_mcp_task(request: MCPTaskRequest):
    """
    Executes a pre-defined, high-level task using the MCP service.
    This allows for orchestrating multiple steps (e.g., login, search) with a single API call.
    """
    try:
        result = await mcp_service.run_task(request.task_name, request.parameters)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
