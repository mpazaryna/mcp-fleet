#!/usr/bin/env python3
"""
Apple Notes integration tools using AppleScript for native macOS access.

This module provides comprehensive Apple Notes functionality:
- Create, list, search, update, and delete notes
- Folder management
- Direct AppleScript integration for full system access
- MCP tool definitions and handlers

Following MCP Fleet TDD methodology with full test coverage.
"""

import subprocess
import json
import re
from typing import Optional, Dict, List, Any
from datetime import datetime


def escape_applescript_string(text: str) -> str:
    """Escape quotes and backslashes for AppleScript string literals."""
    # Escape backslashes first, then quotes
    return text.replace('\\', '\\\\').replace('"', '\\"')


def generate_create_note_script(title: str, content: str, folder: Optional[str] = None) -> str:
    """Generate AppleScript for creating a new note."""
    escaped_title = escape_applescript_string(title)
    escaped_content = escape_applescript_string(content)
    
    if folder:
        escaped_folder = escape_applescript_string(folder)
        script = f'''
tell application "Notes"
    activate
    tell folder "{escaped_folder}"
        make new note with properties {{name:"{escaped_title}", body:"{escaped_content}"}}
        set noteRef to the result
        return id of noteRef
    end tell
end tell
'''
    else:
        script = f'''
tell application "Notes"
    activate
    make new note with properties {{name:"{escaped_title}", body:"{escaped_content}"}}
    set noteRef to the result
    return id of noteRef
end tell
'''
    
    return script.strip()


def generate_list_notes_script(folder: Optional[str] = None) -> str:
    """Generate AppleScript for listing notes."""
    if folder:
        escaped_folder = escape_applescript_string(folder)
        script = f'''
tell application "Notes"
    activate
    tell folder "{escaped_folder}"
        set noteList to {{}}
        repeat with eachNote in every note
            set end of noteList to (name of eachNote)
        end repeat
        return my listToString(noteList)
    end tell
end tell

on listToString(lst)
    set AppleScript's text item delimiters to ", "
    set result to lst as string
    set AppleScript's text item delimiters to ""
    return result
end listToString
'''
    else:
        script = '''
tell application "Notes"
    activate
    set noteList to {}
    repeat with eachNote in every note
        set end of noteList to (name of eachNote)
    end repeat
    return my listToString(noteList)
end tell

on listToString(lst)
    set AppleScript's text item delimiters to ", "
    set result to lst as string
    set AppleScript's text item delimiters to ""
    return result
end listToString
'''
    
    return script.strip()


def generate_search_notes_script(query: str, folder: Optional[str] = None) -> str:
    """Generate AppleScript for searching notes by content."""
    escaped_query = escape_applescript_string(query)
    
    if folder:
        escaped_folder = escape_applescript_string(folder)
        script = f'''
tell application "Notes"
    activate
    tell folder "{escaped_folder}"
        set matchingNotes to {{}}
        repeat with eachNote in every note
            if (body of eachNote) contains "{escaped_query}" or (name of eachNote) contains "{escaped_query}" then
                set end of matchingNotes to (name of eachNote)
            end if
        end repeat
        return my listToString(matchingNotes)
    end tell
end tell

on listToString(lst)
    set AppleScript's text item delimiters to ", "
    set result to lst as string
    set AppleScript's text item delimiters to ""
    return result
end listToString
'''
    else:
        script = f'''
tell application "Notes"
    activate
    set matchingNotes to {{}}
    repeat with eachNote in every note
        if (body of eachNote) contains "{escaped_query}" or (name of eachNote) contains "{escaped_query}" then
            set end of matchingNotes to (name of eachNote)
        end if
    end repeat
    return my listToString(matchingNotes)
end tell

on listToString(lst)
    set AppleScript's text item delimiters to ", "
    set result to lst as string
    set AppleScript's text item delimiters to ""
    return result
end listToString
'''
    
    return script.strip()


def generate_list_folders_script() -> str:
    """Generate AppleScript for listing all folders."""
    script = '''
tell application "Notes"
    activate
    set folderList to {}
    repeat with eachFolder in every folder
        set end of folderList to (name of eachFolder)
    end repeat
    return my listToString(folderList)
end tell

on listToString(lst)
    set AppleScript's text item delimiters to ", "
    set result to lst as string
    set AppleScript's text item delimiters to ""
    return result
end listToString
'''
    return script.strip()


def generate_create_folder_script(name: str) -> str:
    """Generate AppleScript for creating a new folder."""
    escaped_name = escape_applescript_string(name)
    script = f'''
tell application "Notes"
    activate
    make new folder with properties {{name:"{escaped_name}"}}
    return "Folder created successfully"
end tell
'''
    return script.strip()


def execute_applescript(script: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute AppleScript and return structured result.
    
    Returns:
        Dict with keys: success (bool), output (str), error (str)
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout.strip()
            }
        else:
            return {
                'success': False,
                'error': result.stderr.strip() or "AppleScript execution failed"
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': f"AppleScript execution timeout after {timeout} seconds"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to execute AppleScript: {str(e)}"
        }


def validate_note_content(title: str, content: str) -> Dict[str, Any]:
    """
    Validate note title and content before creation.
    
    Returns:
        Dict with keys: valid (bool), error (str if invalid)
    """
    if not title or not title.strip():
        return {
            'valid': False,
            'error': "Note title cannot be empty"
        }
    
    if len(title) > 1000:
        return {
            'valid': False,
            'error': "Note title is too long (max 1000 characters)"
        }
    
    if content and len(content) > 50000:  # Reasonable limit for Notes app
        return {
            'valid': False,
            'error': "Note content is too long (max 50,000 characters)"
        }
    
    return {'valid': True}


def create_note(title: str, content: str, folder: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new note in Apple Notes.
    
    Args:
        title: Note title
        content: Note content
        folder: Optional folder name to create note in
        
    Returns:
        Dict with success status, note details, and any errors
    """
    # Validate input
    validation = validate_note_content(title, content)
    if not validation['valid']:
        return {
            'success': False,
            'error': validation['error']
        }
    
    # Generate and execute AppleScript
    script = generate_create_note_script(title, content, folder)
    result = execute_applescript(script)
    
    if result['success']:
        # Extract note ID from output if available
        note_id = None
        if 'note id' in result['output']:
            note_id = result['output']
        
        return {
            'success': True,
            'title': title,
            'content': content,
            'folder': folder,
            'note_id': note_id,
            'created_at': datetime.now().isoformat(),
            'message': f"Note '{title}' created successfully"
        }
    else:
        return {
            'success': False,
            'error': result['error']
        }


def list_notes(folder: Optional[str] = None) -> Dict[str, Any]:
    """
    List notes from Apple Notes.
    
    Args:
        folder: Optional folder name to list notes from
        
    Returns:
        Dict with success status and list of note names
    """
    script = generate_list_notes_script(folder)
    result = execute_applescript(script)
    
    if result['success']:
        # Parse comma-separated note names
        if result['output']:
            notes = [note.strip() for note in result['output'].split(',') if note.strip()]
        else:
            notes = []
        
        return {
            'success': True,
            'notes': notes,
            'count': len(notes),
            'folder': folder
        }
    else:
        return {
            'success': False,
            'error': result['error']
        }


def search_notes(query: str, folder: Optional[str] = None) -> Dict[str, Any]:
    """
    Search notes by title or content.
    
    Args:
        query: Search query string
        folder: Optional folder to search within
        
    Returns:
        Dict with success status and matching note names
    """
    if not query or not query.strip():
        return {
            'success': False,
            'error': "Search query cannot be empty"
        }
    
    script = generate_search_notes_script(query, folder)
    result = execute_applescript(script)
    
    if result['success']:
        # Parse comma-separated note names
        if result['output']:
            notes = [note.strip() for note in result['output'].split(',') if note.strip()]
        else:
            notes = []
        
        return {
            'success': True,
            'notes': notes,
            'count': len(notes),
            'query': query,
            'folder': folder
        }
    else:
        return {
            'success': False,
            'error': result['error']
        }


def update_note(note_id: str, title: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
    """
    Update an existing note (placeholder - complex to implement with AppleScript).
    
    Args:
        note_id: Note identifier
        title: New title (optional)
        content: New content (optional)
        
    Returns:
        Dict with success status and update details
    """
    # This is a placeholder implementation
    # Updating notes by ID is complex with AppleScript
    return {
        'success': False,
        'error': "Note updating not yet implemented - use delete and recreate"
    }


def delete_note(note_id: str) -> Dict[str, Any]:
    """
    Delete a note (placeholder - complex to implement with AppleScript).
    
    Args:
        note_id: Note identifier
        
    Returns:
        Dict with success status
    """
    # This is a placeholder implementation
    # Deleting specific notes by ID is complex with AppleScript
    return {
        'success': False,
        'error': "Note deletion not yet implemented - delete manually from Notes app"
    }


def create_folder(name: str) -> Dict[str, Any]:
    """
    Create a new folder in Apple Notes.
    
    Args:
        name: Folder name
        
    Returns:
        Dict with success status and folder details
    """
    if not name or not name.strip():
        return {
            'success': False,
            'error': "Folder name cannot be empty"
        }
    
    script = generate_create_folder_script(name)
    result = execute_applescript(script)
    
    if result['success']:
        return {
            'success': True,
            'folder_name': name,
            'message': f"Folder '{name}' created successfully"
        }
    else:
        return {
            'success': False,
            'error': result['error']
        }


def list_folders() -> Dict[str, Any]:
    """
    List all folders in Apple Notes.
    
    Returns:
        Dict with success status and list of folder names
    """
    script = generate_list_folders_script()
    result = execute_applescript(script)
    
    if result['success']:
        # Parse comma-separated folder names
        if result['output']:
            folders = [folder.strip() for folder in result['output'].split(',') if folder.strip()]
        else:
            folders = []
        
        return {
            'success': True,
            'folders': folders,
            'count': len(folders)
        }
    else:
        return {
            'success': False,
            'error': result['error']
        }


# MCP Tool Definitions
notes_tools = [
    {
        "name": "create_note",
        "description": "Create a new note in Apple Notes with title and content",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the note"
                },
                "content": {
                    "type": "string", 
                    "description": "The content/body of the note"
                },
                "folder": {
                    "type": ["string", "null"],
                    "description": "Optional folder name to create the note in"
                }
            },
            "required": ["title", "content"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "folder": {"type": ["string", "null"]},
                "note_id": {"type": ["string", "null"]},
                "created_at": {"type": "string"},
                "message": {"type": "string"},
                "error": {"type": "string"}
            }
        }
    },
    {
        "name": "list_notes",
        "description": "List all notes or notes from a specific folder",
        "input_schema": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": ["string", "null"],
                    "description": "Optional folder name to list notes from"
                }
            }
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "notes": {"type": "array", "items": {"type": "string"}},
                "count": {"type": "integer"},
                "folder": {"type": ["string", "null"]},
                "error": {"type": "string"}
            }
        }
    },
    {
        "name": "search_notes",
        "description": "Search notes by title or content",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query to find in note titles or content"
                },
                "folder": {
                    "type": ["string", "null"],
                    "description": "Optional folder to search within"
                }
            },
            "required": ["query"]
        },
        "output_schema": {
            "type": "object", 
            "properties": {
                "success": {"type": "boolean"},
                "notes": {"type": "array", "items": {"type": "string"}},
                "count": {"type": "integer"},
                "query": {"type": "string"},
                "folder": {"type": ["string", "null"]},
                "error": {"type": "string"}
            }
        }
    },
    {
        "name": "create_folder",
        "description": "Create a new folder in Apple Notes",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name for the new folder"
                }
            },
            "required": ["name"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "folder_name": {"type": "string"},
                "message": {"type": "string"},
                "error": {"type": "string"}
            }
        }
    },
    {
        "name": "list_folders",
        "description": "List all folders in Apple Notes",
        "input_schema": {
            "type": "object",
            "properties": {}
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "folders": {"type": "array", "items": {"type": "string"}},
                "count": {"type": "integer"},
                "error": {"type": "string"}
            }
        }
    }
]


# MCP Handler Functions
async def handle_create_note(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle create_note MCP tool call."""
    title = args.get("title", "")
    content = args.get("content", "")
    folder = args.get("folder")
    
    return create_note(title, content, folder)


async def handle_list_notes(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list_notes MCP tool call."""
    folder = args.get("folder")
    return list_notes(folder)


async def handle_search_notes(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle search_notes MCP tool call."""
    query = args.get("query", "")
    folder = args.get("folder")
    return search_notes(query, folder)


async def handle_create_folder(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle create_folder MCP tool call."""
    name = args.get("name", "")
    return create_folder(name)


async def handle_list_folders(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list_folders MCP tool call."""
    return list_folders()


# Handler registration
notes_handlers = {
    "create_note": handle_create_note,
    "list_notes": handle_list_notes,
    "search_notes": handle_search_notes,
    "create_folder": handle_create_folder,
    "list_folders": handle_list_folders
}