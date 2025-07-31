from .mouse_service import mouse_service
from .browser_service import browser_service

class MCPService:
    """
    Master Control Program (MCP) Service.
    Orchestrates complex, multi-step tasks by combining the atomic actions
    of the 'eyes' (BrowserService) and 'hands' (MouseService).
    """

    def __init__(self):
        self._tasks = {
            "login_to_website": self._login_to_website
        }

    async def run_task(self, task_name: str, parameters: dict):
        """
        Runs a registered high-level task.
        """
        if task_name not in self._tasks:
            raise ValueError(f"Task '{task_name}' not found.")
        
        task_function = self._tasks[task_name]
        return await task_function(**parameters)

    async def _login_to_website(self, username_selector: str, password_selector: str, login_button_selector: str, username: str, password: str):
        """
        A high-level task to perform a complete login sequence.
        """
        try:
            # Type username
            await mouse_service.type(selector=username_selector, text=username)
            
            # Type password
            await mouse_service.type(selector=password_selector, text=password)

            # Click login button
            await mouse_service.click(selector=login_button_selector)

            # Wait for navigation to complete after click
            await browser_service.page.wait_for_load_state('networkidle', timeout=5000)

            current_url = await browser_service.get_current_url()
            return {"status": "login_successful", "final_url": current_url}
            
        except Exception as e:
            return {"status": "login_failed", "error": str(e)}

mcp_service = MCPService()
