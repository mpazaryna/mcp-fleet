"""
Yoga teaching tools for generating setlists and dharma talks
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.types import MCPTool
from pydantic import BaseModel, Field
import aiofiles
from templates import TemplateEngine, TemplateContext

logger = logging.getLogger(__name__)

# Initialize template engine and storage path
storage_path = os.getenv("YOGA_STORAGE_PATH", "./yoga_data")
template_engine = TemplateEngine()

# Ensure storage directory exists
os.makedirs(storage_path, exist_ok=True)


class SimpleFileStorage:
    """Simple file storage for yoga content."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def write_file(self, file_path: str, content: str) -> None:
        """Write content to a file."""
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(content)

# Initialize simple storage
simple_storage = SimpleFileStorage(storage_path)


# Schema definitions
class CreateSetlistInputSchema(BaseModel):
    """Schema for creating a yoga setlist"""

    name: str = Field(description="Name of the yoga setlist")
    duration: int = Field(description="Duration in minutes")
    level: str = Field(description="Difficulty level (beginner, intermediate, advanced)")
    focus: str = Field(description="Focus area (strength, flexibility, relaxation, etc.)")
    considerations: str = Field(description="Special considerations or modifications")
    theme: Optional[str] = Field(default=None, description="Optional theme for the class")


class CreateTalkInputSchema(BaseModel):
    """Schema for creating a dharma talk"""

    name: str = Field(description="Name of the dharma talk")
    duration: int = Field(description="Duration in minutes")
    topic: str = Field(description="Main topic or theme")
    audience: str = Field(description="Target audience description")
    style: str = Field(description="Teaching style (traditional, contemporary, etc.)")
    message: str = Field(description="Key message or teaching point")


class ContentCreationResult(BaseModel):
    """Result of content creation"""

    success: bool
    content_id: str
    name: str
    content_type: str
    file_path: str
    created_at: str


# Tool implementations
async def create_setlist(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a yoga setlist using templates and interactive prompting"""
    logger.info(f"Creating setlist with args: {args}")
    
    # Validate input
    input_data = CreateSetlistInputSchema(**args)
    
    # Load setlist template
    template_path = Path(__file__).parent.parent / "templates" / "setlist.md"
    template = await template_engine.load_template(str(template_path))
    
    # Create context for template rendering
    context = TemplateContext({
        "name": input_data.name,
        "duration": str(input_data.duration),
        "level": input_data.level,
        "focus": input_data.focus,
        "considerations": input_data.considerations,
        "theme": input_data.theme or "General Practice",
        "created_at": datetime.now().isoformat()
    })
    
    # Generate content ID and file path
    content_id = f"setlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    file_path = f"{storage_path}/{content_id}.md"
    
    # Render template and save
    result = await template_engine.render_and_save(
        template.content, context, file_path, simple_storage
    )
    
    logger.info(f"✅ Setlist created successfully: {content_id}")
    
    return ContentCreationResult(
        success=True,
        content_id=content_id,
        name=input_data.name,
        content_type="setlist",
        file_path=file_path,
        created_at=datetime.now().isoformat()
    ).model_dump()


async def create_talk(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create a dharma talk using templates and interactive prompting"""
    logger.info(f"Creating talk with args: {args}")
    
    # Validate input
    input_data = CreateTalkInputSchema(**args)
    
    # Load talk template
    template_path = Path(__file__).parent.parent / "templates" / "talk.md"
    template = await template_engine.load_template(str(template_path))
    
    # Create context for template rendering
    context = TemplateContext({
        "name": input_data.name,
        "duration": str(input_data.duration),
        "topic": input_data.topic,
        "audience": input_data.audience,
        "style": input_data.style,
        "message": input_data.message,
        "created_at": datetime.now().isoformat()
    })
    
    # Generate content ID and file path
    content_id = f"talk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    file_path = f"{storage_path}/{content_id}.md"
    
    # Render template and save
    result = await template_engine.render_and_save(
        template.content, context, file_path, simple_storage
    )
    
    logger.info(f"✅ Talk created successfully: {content_id}")
    
    return ContentCreationResult(
        success=True,
        content_id=content_id,
        name=input_data.name,
        content_type="talk",
        file_path=file_path,
        created_at=datetime.now().isoformat()
    ).model_dump()


# Tool definitions
yoga_tools: List[MCPTool] = [
    MCPTool(
        name="create_setlist",
        description="Create a yoga setlist using templated content generation with interactive prompting",
        input_schema=CreateSetlistInputSchema.model_json_schema(),
        output_schema=ContentCreationResult.model_json_schema(),
    ),
    MCPTool(
        name="create_talk", 
        description="Create a dharma talk using templated content generation with interactive prompting",
        input_schema=CreateTalkInputSchema.model_json_schema(),
        output_schema=ContentCreationResult.model_json_schema(),
    ),
]

# Tool handlers
yoga_handlers = {
    "create_setlist": create_setlist,
    "create_talk": create_talk,
}