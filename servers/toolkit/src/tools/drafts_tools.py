"""
Drafts app integration tools for MCP Toolkit server.

Provides functionality to create drafts in the Drafts app via URL schemes
and integrate with external note-taking workflows.
"""
import urllib.parse
import webbrowser
from typing import List, Optional, Dict, Any


def validate_draft_content(content: str) -> None:
    """Validate draft content."""
    if not content or not content.strip():
        raise ValueError("Content cannot be empty")


def encode_draft_params(content: str, tags: Optional[List[str]] = None, action: Optional[str] = None) -> str:
    """
    Encode parameters for Drafts URL scheme.
    
    Args:
        content: The text content for the draft
        tags: Optional list of tags to add to the draft
        action: Optional action to run after creating the draft
    
    Returns:
        URL scheme string for Drafts app
    
    Raises:
        ValueError: If content is empty
        TypeError: If tags is not a list
    """
    validate_draft_content(content)
    
    if tags is not None and not isinstance(tags, list):
        raise TypeError("Tags must be a list")
    
    # Build URL parameters
    params = {"text": content}
    
    if tags:
        # Add each tag as a separate parameter
        for tag in tags:
            if "tag" not in params:
                params["tag"] = []
            if not isinstance(params["tag"], list):
                params["tag"] = [params["tag"]]
            params["tag"].append(tag)
    
    if action:
        params["action"] = action
    
    # Build URL
    url = "drafts://create?"
    param_parts = []
    
    for key, value in params.items():
        if key == "tag" and isinstance(value, list):
            # Handle multiple tag parameters
            for tag in value:
                param_parts.append(f"tag={urllib.parse.quote(tag)}")
        else:
            param_parts.append(f"{key}={urllib.parse.quote(str(value))}")
    
    return url + "&".join(param_parts)


def send_to_url_scheme(scheme: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a URL scheme to the system to open an external app.
    
    Args:
        scheme: The URL scheme (e.g., "things", "obsidian")
        params: Parameters to include in the URL
    
    Returns:
        Dict with success status and URL
    """
    # Build URL
    url = f"{scheme}://"
    if params:
        param_parts = []
        for key, value in params.items():
            param_parts.append(f"{key}={urllib.parse.quote(str(value))}")
        url += "?" + "&".join(param_parts)
    
    try:
        webbrowser.open(url)
        return {
            "success": True,
            "url": url,
            "message": f"Opened {scheme} app"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


def create_draft(content: str, tags: Optional[List[str]] = None, action: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new draft in the Drafts app.
    
    Args:
        content: The text content for the draft
        tags: Optional list of tags to add to the draft
        action: Optional action to run after creating the draft
    
    Returns:
        Dict with success status and details
    """
    try:
        url = encode_draft_params(content, tags, action)
        webbrowser.open(url)
        
        return {
            "success": True,
            "url": url,
            "message": "Draft created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def create_draft_with_template(template_name: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a draft using a template with variable substitution.
    
    Args:
        template_name: Name of the template to use
        variables: Variables to substitute in the template
    
    Returns:
        Dict with success status and details
    """
    # Simple template processing
    templates = {
        "daily_note": """# Daily Note - {date}

## Mood
{mood}

## Goals
{goals}

## Notes
""",
        "meeting": """# {title}

Date: {date}
Attendees: {attendees}

## Agenda

## Notes

## Action Items
"""
    }
    
    if template_name not in templates:
        return {
            "success": False,
            "error": f"Template '{template_name}' not found"
        }
    
    template = templates[template_name]
    variables = variables or {}
    
    try:
        # Simple variable substitution
        content = template
        for key, value in variables.items():
            if isinstance(value, list):
                value = "\n".join(f"- {item}" for item in value)
            content = content.replace(f"{{{key}}}", str(value))
        
        return create_draft(content, tags=[template_name])
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# MCP Tool definitions
draft_tools = [
    {
        "name": "create_draft",
        "description": "Create a new draft in the Drafts app with optional tags and actions",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The text content for the draft"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of tags to add to the draft"
                },
                "action": {
                    "type": "string",
                    "description": "Optional action to run after creating the draft"
                }
            },
            "required": ["content"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "url": {"type": "string"},
                "message": {"type": "string"},
                "error": {"type": "string"}
            }
        }
    },
    {
        "name": "create_draft_with_template",
        "description": "Create a draft using a predefined template with variable substitution",
        "input_schema": {
            "type": "object",
            "properties": {
                "template_name": {
                    "type": "string",
                    "description": "Name of the template to use (daily_note, meeting)"
                },
                "variables": {
                    "type": "object",
                    "description": "Variables to substitute in the template"
                }
            },
            "required": ["template_name"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "url": {"type": "string"},
                "message": {"type": "string"},
                "error": {"type": "string"}
            }
        }
    }
]

# MCP Tool handlers
draft_handlers = {
    "create_draft": lambda args: create_draft(
        args["content"], 
        args.get("tags"), 
        args.get("action")
    ),
    "create_draft_with_template": lambda args: create_draft_with_template(
        args["template_name"], 
        args.get("variables")
    )
}