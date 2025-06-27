"""
Streaming support for Claude API
"""
import asyncio
import json
import os
from typing import List, Optional

import httpx
from .types import ClaudeMessage, StreamHandler


class StreamingClient:
    """Claude API streaming client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required for streaming")
        
        self.base_url = "https://api.anthropic.com/v1/messages"
        
        # Create HTTP client
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "anthropic-beta": "messages-2023-12-15"
            }
        )
    
    async def stream_chat(
        self,
        messages: List[ClaudeMessage],
        system_prompt: Optional[str],
        on_chunk: StreamHandler,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096
    ) -> str:
        """Stream a chat conversation and call handler for each chunk"""
        # Prepare request data
        request_data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [msg.model_dump() for msg in messages],
            "stream": True
        }
        
        if system_prompt:
            request_data["system"] = system_prompt
        
        # Send streaming request
        async with self.client.stream("POST", self.base_url, json=request_data) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                raise Exception(f"Streaming error ({response.status_code}): {error_text.decode()}")
            
            full_text = ""
            
            async for chunk in response.aiter_lines():
                if chunk.startswith("data: "):
                    data = chunk[6:]  # Remove "data: " prefix
                    if data == "[DONE]":
                        continue
                    
                    try:
                        parsed = json.loads(data)
                        
                        if parsed.get("type") == "content_block_delta" and parsed.get("delta", {}).get("text"):
                            text = parsed["delta"]["text"]
                            full_text += text
                            await on_chunk(text)
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
            
            return full_text
    
    async def close(self) -> None:
        """Close the HTTP client"""
        await self.client.aclose()