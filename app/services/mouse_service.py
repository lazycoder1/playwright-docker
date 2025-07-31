import pyautogui
import asyncio
# Removed browser_service import since mouse methods no longer use it

class MouseService:
    """
    Provides scrolling functionality via pyautogui.
    Most mouse interactions have been replaced with DOM-based methods for reliability.
    """

    def __init__(self):
        """
        Initializes the service and configures pyautogui's safety features.
        """
        # Move mouse to a screen corner to abort if something goes wrong.
        pyautogui.FAILSAFE = True
        # Add a small delay after each pyautogui action for reliability.
        pyautogui.PAUSE = 0.1

    async def scroll(self, direction: str):
        """Scrolls the page up or down."""
        scroll_amount = -500 if direction == "down" else 500
        print(f"🔄 Scrolling {direction} by {abs(scroll_amount)} pixels")
        await asyncio.to_thread(pyautogui.scroll, scroll_amount)
        print(f"✅ Scroll {direction} completed")

mouse_service = MouseService()
