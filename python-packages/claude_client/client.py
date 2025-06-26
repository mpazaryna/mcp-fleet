"""
Enhanced Anthropic Claude API client
"""
import asyncio
import json
import os
from typing import List, Optional

import httpx
from .types import ClaudeConfig, ClaudeMessage, ClaudeResponse, ClaudeError, ClaudeModel


class ClaudeClient:
    """Enhanced Claude API client with retry logic"""
    
    def __init__(self, config: Optional[ClaudeConfig] = None):
        self.config = config or ClaudeConfig()
        
        # Set defaults
        self.api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable or api_key config required")
        
        self.base_url = self.config.base_url or "https://api.anthropic.com/v1/messages"
        self.model = self.config.model or "claude-3-5-sonnet-20241022"
        self.max_retries = self.config.max_retries or 3
        self.retry_delay = self.config.retry_delay or 1000
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
        )
    
    async def chat(
        self,
        messages: List[ClaudeMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> str:
        """Send a chat request and return just the text response"""
        response = await self.send_request(messages, system_prompt, max_tokens)
        return response.content[0].text
    
    async def chat_with_response(
        self,
        messages: List[ClaudeMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> ClaudeResponse:
        """Send a chat request and return the full response"""
        return await self.send_request(messages, system_prompt, max_tokens)
    
    async def send_request(
        self,
        messages: List[ClaudeMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> ClaudeResponse:
        """Send request to Claude API with retry logic"""
        last_error: Optional[Exception] = None
        
        for attempt in range(self.max_retries):
            try:
                # Prepare request data
                request_data = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "messages": [msg.model_dump() for msg in messages]
                }
                
                if system_prompt:
                    request_data["system"] = system_prompt
                
                # Send request
                response = await self.client.post(
                    self.base_url,
                    json=request_data
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    return ClaudeResponse(**response_data)
                
                # Handle errors
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", response.text)
                
                # Check if rate limited
                if response.status_code == 429:
                    retry_after = response.headers.get("retry-after")
                    delay = int(retry_after) * 1000 if retry_after else self.retry_delay * (attempt + 1)
                    
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(delay / 1000)
                        continue
                
                raise Exception(f"Claude API error ({response.status_code}): {error_message}")
                
            except Exception as error:
                last_error = error
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1) / 1000)
                    continue
        
        raise last_error or Exception("Failed to communicate with Claude API")
    
    def update_model(self, model: ClaudeModel) -> None:
        """Update the model being used"""
        self.model = model
    
    def get_model(self) -> str:
        """Get the current model"""
        return self.model
    
    async def close(self) -> None:
        """Close the HTTP client"""
        await self.client.aclose()