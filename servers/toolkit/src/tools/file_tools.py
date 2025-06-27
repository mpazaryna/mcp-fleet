"""
File operation tools for Toolkit server
"""
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any

async def read_file(file_path: str) -> Dict[str, Any]:
    """Read file contents."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write file contents."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"File written to {file_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def list_directory(directory_path: str) -> Dict[str, Any]:
    """List directory contents."""
    try:
        path = Path(directory_path)
        if not path.exists():
            return {"success": False, "error": "Directory does not exist"}
        
        items = []
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None
            })
        
        return {"success": True, "items": items}
    except Exception as e:
        return {"success": False, "error": str(e)}

# MCP Tool definitions
file_tools = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["file_path"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "content": {"type": "string"},
                "error": {"type": "string"}
            }
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string", 
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "error": {"type": "string"}
            }
        }
    },
    {
        "name": "list_directory",
        "description": "List the contents of a directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to the directory to list"
                }
            },
            "required": ["directory_path"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "items": {"type": "array"},
                "error": {"type": "string"}
            }
        }
    }
]

# MCP Tool handlers  
file_handlers = {
    "read_file": lambda args: read_file(args["file_path"]),
    "write_file": lambda args: write_file(args["file_path"], args["content"]),
    "list_directory": lambda args: list_directory(args["directory_path"])
}