from playwright.async_api import async_playwright, Browser, Page
from fastapi.responses import Response
from app.models import Element, InteractiveElementsResponse
import asyncio

class BrowserService:
    """
    Manages all browser-related interactions using Playwright.
    This service acts as the 'eyes' of the agent, inspecting the DOM and
    providing context about the web page.
    """
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.playwright = None

    async def launch_browser(self):
        """
        Connects to the remotely running Chromium instance and injects necessary scripts.
        This is a crucial step in the hybrid architecture, allowing Playwright
        to control a browser that is visible and controllable by PyAutoGUI.
        """
        try:
            self.playwright = await async_playwright().start()
            
            # Connect to the Chromium instance with remote debugging
            self.browser = await self.playwright.chromium.connect_over_cdp("http://localhost:9222")
            
            # Get the first context, which is the default one
            context = self.browser.contexts[0]
            
            # Inject the script into the context if it exists
            try:
                with open("app/static/get_path.js", "r") as f:
                    js_script = f.read()
                    await context.add_init_script(js_script)
            except FileNotFoundError:
                print("Warning: get_path.js not found, skipping script injection")
            
            self.page = context.pages[0]
            
            # Navigate to a default page if not already on one
            current_url = self.page.url
            if current_url == "about:blank" or "chrome://" in current_url:
                await self.page.goto("https://app.hubspot.com", wait_until="domcontentloaded", timeout=30000)
            
        except Exception as e:
            print(f"Error connecting to browser: {e}")
            # Fallback: launch a new browser instance
            try:
                self.browser = await self.playwright.chromium.launch(
                    headless=False,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--window-size=1280,800',
                        '--remote-debugging-port=9222'
                    ]
                )
                context = await self.browser.new_context(
                    viewport={'width': 1280, 'height': 800}
                )
                self.page = await context.new_page()
                await self.page.goto("https://duckduckgo.com")
            except Exception as fallback_error:
                print(f"Fallback browser launch failed: {fallback_error}")

    async def close_browser(self):
        """Closes the browser connection."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_interactive_elements(self) -> InteractiveElementsResponse:
        """
        Finds all interactive elements on the page and returns them.
        """
        print("🤖 Finding interactive elements...")
        
        if not self.page:
            return InteractiveElementsResponse(url="", elements=[])
        
        try:
            # Get current URL
            current_url = self.page.url
            
            # Find all interactive elements
            elements = []
            
            # Get buttons
            buttons = await self.page.locator("button:visible").all()
            for i, button in enumerate(buttons):
                try:
                    text = await button.inner_text()
                    if text.strip():
                        elements.append(Element(
                            selector=f"button:nth-of-type({i+1})",
                            text=text.strip()[:50],  # Limit text length
                            aria_label=await button.get_attribute("aria-label"),
                            role="button"
                        ))
                except:
                    pass
            
            # Get links
            links = await self.page.locator("a:visible").all()
            for i, link in enumerate(links):
                try:
                    text = await link.inner_text()
                    if text.strip():
                        elements.append(Element(
                            selector=f"a:nth-of-type({i+1})",
                            text=text.strip()[:50],
                            aria_label=await link.get_attribute("aria-label"),
                            role="link"
                        ))
                except:
                    pass
            
            # Get inputs
            inputs = await self.page.locator("input:visible").all()
            for i, input_elem in enumerate(inputs):
                try:
                    placeholder = await input_elem.get_attribute("placeholder")
                    input_type = await input_elem.get_attribute("type")
                    elements.append(Element(
                        selector=f"input:nth-of-type({i+1})",
                        text=placeholder or f"{input_type} input",
                        aria_label=await input_elem.get_attribute("aria-label"),
                        role="textbox"
                    ))
                except:
                    pass
            
            return InteractiveElementsResponse(url=current_url, elements=elements)
            
        except Exception as e:
            print(f"Error getting interactive elements: {e}")
            return InteractiveElementsResponse(url=self.page.url if self.page else "", elements=[])

    async def get_element_center_coordinates(self, selector: str) -> dict:
        """
        Finds an element by its selector and returns its center coordinates.
        Raises an exception if the element is not found or not visible.
        """
        element = self.page.locator(selector).first
        try:
            bounding_box = await element.bounding_box(timeout=5000)
            if not bounding_box:
                raise ValueError("Element is not visible or has no size.")
        except Exception:
            raise ValueError(f"Element not found for selector: {selector}")

        center_x = bounding_box['x'] + (bounding_box['width'] / 2)
        center_y = bounding_box['y'] + (bounding_box['height'] / 2)

        return {"x": center_x, "y": center_y}

    async def find_element_by_text(self, text: str):
        """
        Finds a single interactive element by its exact text content.
        This is a more targeted way to find elements than getting all of them.
        """
        if not self.page:
            return None

        # Try to find the element by text. Playwright's text selector is powerful.
        # It searches for buttons, links, and other elements containing the text.
        try:
            # First, try a general text search
            element_locator = self.page.get_by_text(text, exact=True)
            count = await element_locator.count()

            # If not found, try common interactive roles
            if count == 0:
                element_locator = self.page.locator(f'button:has-text("{text}"), a:has-text("{text}"), [role="button"]:has-text("{text}")').first
                await element_locator.wait_for(timeout=2000) # Wait a bit for the element to be ready
            else:
                element_locator = element_locator.first

            # Get details of the found element
            if await element_locator.is_visible():
                text_content = await element_locator.inner_text()
                aria_label = await element_locator.get_attribute("aria-label")
                role = await element_locator.get_attribute("role") or "element"

                # We need a reliable selector. We'll generate one.
                # NOTE: This is a simplified approach. A more robust solution might
                # involve a more complex selector generation strategy.
                selector = f'text="{text}"'

                return {
                    "found": True,
                    "selector": selector,
                    "text": text_content,
                    "aria_label": aria_label,
                    "role": role,
                }
        except Exception:
            # If any error occurs (e.g., element not found), return not found.
            pass

        return {"found": False}

    async def navigate(self, url: str):
        """Navigates the page to a new URL."""
        if self.page:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

    async def get_current_url(self) -> str:
        """Returns the current URL of the page."""
        return self.page.url if self.page else "about:blank"

    async def get_screenshot(self) -> Response:
        """Takes a screenshot of the current page and returns it as a PNG response."""
        if self.page:
            screenshot_bytes = await self.page.screenshot()
            return Response(content=screenshot_bytes, media_type="image/png")
        else:
            # Return empty response if no page
            return Response(content=b"", media_type="image/png")

    async def highlight_element_css(self, selector: str, duration: int = 3, style: str = "border"):
        """
        Highlights an element using CSS styling instead of mouse movement.
        This is more reliable when mouse automation is not available.
        """
        if not self.page:
            raise ValueError("No active page")
        
        try:
            element = self.page.locator(selector).first
            await element.wait_for(timeout=5000)
            
            # Define different highlight styles
            styles = {
                "border": "border: 3px solid #ff4444 !important; border-radius: 4px !important;",
                "background": "background-color: rgba(255, 255, 0, 0.3) !important;",
                "shadow": "box-shadow: 0 0 20px #ff4444 !important;"
            }
            
            highlight_style = styles.get(style, styles["border"])
            
            # Add highlight styling
            await element.evaluate(f"""
                element => {{
                    element.setAttribute('data-original-style', element.style.cssText);
                    element.style.cssText += '{highlight_style}';
                }}
            """)
            
            # Wait for the specified duration
            await asyncio.sleep(duration)
            
            # Remove highlight styling
            await element.evaluate("""
                element => {
                    const originalStyle = element.getAttribute('data-original-style');
                    if (originalStyle !== null) {
                        element.style.cssText = originalStyle;
                        element.removeAttribute('data-original-style');
                    }
                }
            """)
            
            return {"status": "highlight_successful", "selector": selector, "duration": duration, "style": style}
            
        except Exception as e:
            raise ValueError(f"Could not highlight element {selector}: {str(e)}")

    async def click_element_dom(self, selector: str):
        """
        Clicks an element using pure Playwright DOM interaction.
        This is more reliable than mouse automation and works without OS mouse dependencies.
        """
        if not self.page:
            raise ValueError("No active page")
        
        try:
            element = self.page.locator(selector).first
            await element.wait_for(timeout=5000, state="visible")
            await element.click(timeout=10000)
            
            return {"status": "click_successful", "selector": selector, "method": "dom"}
            
        except Exception as e:
            raise ValueError(f"Could not click element {selector}: {str(e)}")

    async def debug_element_visibility(self, selector: str):
        """
        Debug why an element might not be clickable even if it's visible.
        Returns detailed information about element state.
        """
        if not self.page:
            raise ValueError("No active page")
        
        try:
            element = self.page.locator(selector).first
            
            # Check if element exists
            count = await element.count()
            if count == 0:
                return {"error": "Element not found in DOM", "selector": selector}
            
            # Get basic properties
            is_visible = await element.is_visible()
            is_enabled = await element.is_enabled()
            is_editable = await element.is_editable()
            
            # Get bounding box
            bounding_box = await element.bounding_box()
            
            # Get computed styles that affect visibility
            styles = await element.evaluate("""
                element => {
                    const computed = window.getComputedStyle(element);
                    return {
                        display: computed.display,
                        visibility: computed.visibility,
                        opacity: computed.opacity,
                        zIndex: computed.zIndex,
                        position: computed.position,
                        overflow: computed.overflow,
                        width: computed.width,
                        height: computed.height,
                        pointerEvents: computed.pointerEvents
                    };
                }
            """)
            
            # Check viewport
            viewport = self.page.viewport_size
            
            # Check if element is in viewport
            in_viewport = False
            if bounding_box:
                in_viewport = (
                    bounding_box['x'] >= 0 and 
                    bounding_box['y'] >= 0 and
                    bounding_box['x'] < viewport['width'] and
                    bounding_box['y'] < viewport['height']
                )
            
            # Get element tag and attributes
            tag_name = await element.evaluate("element => element.tagName.toLowerCase()")
            attributes = await element.evaluate("""
                element => {
                    const attrs = {};
                    for (let attr of element.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            """)
            
            return {
                "selector": selector,
                "found": True,
                "count": count,
                "is_visible": is_visible,
                "is_enabled": is_enabled,
                "is_editable": is_editable,
                "bounding_box": bounding_box,
                "computed_styles": styles,
                "viewport": viewport,
                "in_viewport": in_viewport,
                "tag_name": tag_name,
                "attributes": attributes,
                "diagnosis": self._diagnose_clickability_issues(is_visible, bounding_box, styles, in_viewport)
            }
            
        except Exception as e:
            return {"error": f"Debug failed: {str(e)}", "selector": selector}

    def _diagnose_clickability_issues(self, is_visible, bounding_box, styles, in_viewport):
        """Diagnose why an element might not be clickable."""
        issues = []
        
        if not is_visible:
            issues.append("Element is not visible to Playwright")
        
        if not bounding_box:
            issues.append("Element has no bounding box (zero size or not rendered)")
        elif bounding_box['width'] == 0 or bounding_box['height'] == 0:
            issues.append("Element has zero width or height")
        
        if styles:
            if styles['display'] == 'none':
                issues.append("Element has display: none")
            if styles['visibility'] == 'hidden':
                issues.append("Element has visibility: hidden")
            if float(styles['opacity']) == 0:
                issues.append("Element has opacity: 0")
            if styles['pointerEvents'] == 'none':
                issues.append("Element has pointer-events: none")
        
        if not in_viewport:
            issues.append("Element is outside the viewport")
        
        if not issues:
            issues.append("Element appears clickable - might be covered by another element")
        
        return issues

    async def click_element_dom_force(self, selector: str):
        """
        Force click an element that might not pass standard clickability checks.
        Uses multiple strategies to click the element.
        """
        if not self.page:
            raise ValueError("No active page")
        
        element = self.page.locator(selector).first
        
        try:
            # Strategy 1: Standard click
            await element.wait_for(timeout=3000, state="visible")
            await element.click(timeout=5000)
            return {"status": "click_successful", "selector": selector, "method": "standard"}
        except:
            pass
        
        try:
            # Strategy 2: Scroll into view first
            await element.scroll_into_view_if_needed()
            await element.click(timeout=5000)
            return {"status": "click_successful", "selector": selector, "method": "scroll_then_click"}
        except:
            pass
        
        try:
            # Strategy 3: Force click (bypasses actionability checks)
            await element.click(force=True, timeout=5000)
            return {"status": "click_successful", "selector": selector, "method": "force_click"}
        except:
            pass
        
        try:
            # Strategy 4: JavaScript click (most permissive)
            await element.evaluate("element => element.click()")
            return {"status": "click_successful", "selector": selector, "method": "javascript_click"}
        except:
            pass
        
        # Strategy 5: Try clicking the center coordinates
        try:
            bounding_box = await element.bounding_box()
            if bounding_box:
                center_x = bounding_box['x'] + bounding_box['width'] / 2
                center_y = bounding_box['y'] + bounding_box['height'] / 2
                await self.page.mouse.click(center_x, center_y)
                return {"status": "click_successful", "selector": selector, "method": "coordinate_click"}
        except:
            pass
        
        raise ValueError(f"All click strategies failed for element {selector}")

    async def type_into_element_dom(self, selector: str, text: str):
        """
        Types text into an element using pure Playwright DOM interaction.
        This is more reliable than mouse automation and works without OS dependencies.
        """
        if not self.page:
            raise ValueError("No active page")
        
        try:
            element = self.page.locator(selector).first
            await element.wait_for(timeout=5000, state="visible")
            
            # Clear the element first, then fill with new text
            await element.clear(timeout=5000)
            await element.fill(text, timeout=10000)
            
            return {"status": "type_successful", "selector": selector, "text": text, "method": "dom"}
            
        except Exception as e:
            raise ValueError(f"Could not type into element {selector}: {str(e)}")

browser_service = BrowserService() 