"""
Conversation management for Claude API
"""
from typing import List, Literal
from .types import ClaudeMessage


class ConversationManager:
    """Manages Claude API conversations"""
    
    def __init__(self, max_messages: int = 50):
        self.messages: List[ClaudeMessage] = []
        self.max_messages = max_messages
    
    def add_message(self, role: Literal["user", "assistant"], content: str) -> None:
        """Add a message to the conversation"""
        self.messages.append(ClaudeMessage(role=role, content=content))
        
        # Trim old messages if exceeding limit
        if len(self.messages) > self.max_messages:
            # Keep system context by removing from middle
            to_remove = len(self.messages) - self.max_messages
            del self.messages[1:1 + to_remove]
    
    def add_user_message(self, content: str) -> None:
        """Add a user message"""
        self.add_message("user", content)
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message"""
        self.add_message("assistant", content)
    
    def get_messages(self) -> List[ClaudeMessage]:
        """Get a copy of all messages"""
        return self.messages.copy()
    
    def get_message_count(self) -> int:
        """Get the number of messages"""
        return len(self.messages)
    
    def clear(self) -> None:
        """Clear all messages"""
        self.messages = []
    
    def get_conversation_text(self) -> str:
        """Get conversation as formatted text"""
        return "\n\n".join(
            f"{msg.role.upper()}: {msg.content}"
            for msg in self.messages
        )
    
    def summarize(self, max_length: int = 1000) -> str:
        """Summarize conversation to fit within max_length"""
        text = self.get_conversation_text()
        if len(text) <= max_length:
            return text
        
        # Get start and end of conversation
        half_length = max_length // 2
        start = text[:half_length]
        end = text[-half_length:]
        
        return f"{start}\n\n[... conversation truncated ...]\n\n{end}"
    
    def export_to_markdown(self) -> str:
        """Export conversation to markdown format"""
        markdown = "# Conversation History\n\n"
        
        for msg in self.messages:
            if msg.role == "user":
                markdown += f"## User\n\n{msg.content}\n\n"
            else:
                markdown += f"## Assistant\n\n{msg.content}\n\n"
        
        return markdown
    
    def import_from_markdown(self, markdown: str) -> None:
        """Import conversation from markdown format"""
        self.clear()
        
        # Simple markdown parser for conversation format
        import re
        sections = re.split(r'^##\s+(User|Assistant)', markdown, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                role = sections[i].lower()
                content = sections[i + 1].strip()
                
                if content and role in ["user", "assistant"]:
                    self.add_message(role, content)  # type: ignore