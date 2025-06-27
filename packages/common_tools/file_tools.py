"""
File operation tools for MCP servers
"""
import aiofiles
import os
from pathlib import Path
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

from mcp_core.types import MCPTool


# Schema definitions
class ReadFileInputSchema(BaseModel):
    """Schema for read file input"""
    path: str = Field(description="Path to the file to read")


class ReadFileOutputSchema(BaseModel):
    """Schema for read file output"""
    content: str
    size: int
    exists: bool


class WriteFileInputSchema(BaseModel):
    """Schema for write file input"""
    path: str = Field(description="Path to the file to write")
    content: str = Field(description="Content to write to the file")
    create_dirs: Optional[bool] = Field(default=False, description="Create directories if they don't exist")


class WriteFileOutputSchema(BaseModel):
    """Schema for write file output"""
    success: bool
    path: str
    size: int


class DirectoryEntry(BaseModel):
    """Directory entry information"""
    name: str
    type: Literal["file", "directory"]
    size: Optional[int] = None


class ListDirectoryInputSchema(BaseModel):
    """Schema for list directory input"""
    path: str = Field(description="Path to the directory to list")
    include_hidden: Optional[bool] = Field(default=False, description="Include hidden files/directories")


class ListDirectoryOutputSchema(BaseModel):
    """Schema for list directory output"""
    entries: List[DirectoryEntry]
    total: int


class FileExistsInputSchema(BaseModel):
    """Schema for file exists input"""
    path: str = Field(description="Path to check")


class FileExistsOutputSchema(BaseModel):
    """Schema for file exists output"""
    exists: bool
    type: Optional[Literal["file", "directory", "unknown"]] = None


# Tool definitions
file_tools: List[MCPTool] = [
    MCPTool(
        name="read_file",
        description="Read the contents of a file",
        input_schema=ReadFileInputSchema.model_json_schema(),
        output_schema=ReadFileOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="write_file",
        description="Write content to a file",
        input_schema=WriteFileInputSchema.model_json_schema(),
        output_schema=WriteFileOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="list_directory",
        description="List contents of a directory",
        input_schema=ListDirectoryInputSchema.model_json_schema(),
        output_schema=ListDirectoryOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="file_exists",
        description="Check if a file or directory exists",
        input_schema=FileExistsInputSchema.model_json_schema(),
        output_schema=FileExistsOutputSchema.model_json_schema(),
    ),
]


# Tool handlers
async def read_file_handler(args: dict) -> dict:
    """Read file handler"""
    validated_args = ReadFileInputSchema(**args)
    path = Path(validated_args.path)
    
    try:
        if not path.exists():
            return ReadFileOutputSchema(
                content="",
                size=0,
                exists=False
            ).model_dump()
        
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        stat = path.stat()
        
        return ReadFileOutputSchema(
            content=content,
            size=stat.st_size,
            exists=True
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to read file {path}: {str(error)}")


async def write_file_handler(args: dict) -> dict:
    """Write file handler"""
    validated_args = WriteFileInputSchema(**args)
    path = Path(validated_args.path)
    
    try:
        if validated_args.create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(validated_args.content)
        
        stat = path.stat()
        
        return WriteFileOutputSchema(
            success=True,
            path=str(path),
            size=stat.st_size
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to write file {path}: {str(error)}")


async def list_directory_handler(args: dict) -> dict:
    """List directory handler"""
    validated_args = ListDirectoryInputSchema(**args)
    path = Path(validated_args.path)
    
    try:
        if not path.exists():
            raise Exception(f"Directory {path} does not exist")
        
        if not path.is_dir():
            raise Exception(f"{path} is not a directory")
        
        entries = []
        
        for entry in path.iterdir():
            if not validated_args.include_hidden and entry.name.startswith('.'):
                continue
            
            size = None
            if entry.is_file():
                try:
                    size = entry.stat().st_size
                except:
                    # Ignore stat errors
                    pass
            
            entries.append(DirectoryEntry(
                name=entry.name,
                type="file" if entry.is_file() else "directory",
                size=size
            ))
        
        return ListDirectoryOutputSchema(
            entries=entries,
            total=len(entries)
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to list directory {path}: {str(error)}")


async def file_exists_handler(args: dict) -> dict:
    """File exists handler"""
    validated_args = FileExistsInputSchema(**args)
    path = Path(validated_args.path)
    
    try:
        if not path.exists():
            return FileExistsOutputSchema(exists=False).model_dump()
        
        if path.is_file():
            file_type = "file"
        elif path.is_dir():
            file_type = "directory"
        else:
            file_type = "unknown"
        
        return FileExistsOutputSchema(
            exists=True,
            type=file_type
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to check existence of {path}: {str(error)}")


# Handler mapping
file_handlers = {
    "read_file": read_file_handler,
    "write_file": write_file_handler,
    "list_directory": list_directory_handler,
    "file_exists": file_exists_handler,
}