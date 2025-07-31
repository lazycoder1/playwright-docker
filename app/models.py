from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class NavigateRequest(BaseModel):
    """Request model for the navigate action."""
    url: str

class ClickRequest(BaseModel):
    """Request model for the click action."""
    selector: str

class TypeRequest(BaseModel):
    """Request model for the type action."""
    selector: str
    text: str

class ScrollRequest(BaseModel):
    """Request model for the scroll action."""
    direction: str

class FindElementByTextRequest(BaseModel):
    text: str = Field(..., description="The exact text of the element to find.")

class FindElementByTextResponse(BaseModel):
    found: bool
    selector: Optional[str] = None
    text: Optional[str] = None
    aria_label: Optional[str] = None
    role: Optional[str] = None

class Element(BaseModel):
    """Represents a single interactive element on the page."""
    selector: str
    text: Optional[str]
    aria_label: Optional[str]
    role: Optional[str]

class InteractiveElementsResponse(BaseModel):
    """Response model for the get_interactive_elements endpoint."""
    url: str
    elements: List[Element]

class MCPTaskRequest(BaseModel):
    """Request model for the MCP to run a high-level task."""
    task_name: str
    parameters: dict

class HighlightRequest(BaseModel):
    """Request model for CSS-based element highlighting."""
    selector: str
    duration: Optional[int] = Field(default=3, description="Duration in seconds to highlight the element")
    style: Optional[str] = Field(default="border", description="Highlight style: 'border', 'background', or 'shadow'")
