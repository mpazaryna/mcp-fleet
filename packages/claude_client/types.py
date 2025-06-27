"""
Type definitions for Claude client
"""
from typing import Any, Dict, List, Literal, Optional, Protocol, Union
from pydantic import BaseModel


class ClaudeMessage(BaseModel):
    """Claude message structure"""
    role: Literal["user", "assistant"]
    content: str


class ClaudeConfig(BaseModel):
    """Configuration for Claude client"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[int] = None


# Type alias for Claude model names
ClaudeModel = Literal[
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229", 
    "claude-3-haiku-20240307",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022"
]


class ClaudeContentBlock(BaseModel):
    """Content block in Claude response"""
    type: str
    text: str


class ClaudeUsage(BaseModel):
    """Usage statistics in Claude response"""
    input_tokens: int
    output_tokens: int


class ClaudeResponse(BaseModel):
    """Claude API response"""
    id: str
    type: str
    role: str
    content: List[ClaudeContentBlock]
    model: str
    stop_reason: Optional[str]
    stop_sequence: Optional[str]
    usage: ClaudeUsage


class ClaudeErrorDetail(BaseModel):
    """Error detail in Claude error response"""
    type: str
    message: str


class ClaudeError(BaseModel):
    """Claude API error response"""
    type: str
    error: ClaudeErrorDetail


class StreamHandler(Protocol):
    """Protocol for stream handlers"""
    
    async def __call__(self, chunk: str) -> None:
        """Handle a streaming chunk"""
        ...