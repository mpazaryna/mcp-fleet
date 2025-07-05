"""Type definitions for the template engine."""

from typing import Dict, Set, Optional
from pydantic import BaseModel


class TemplateContext(BaseModel):
    """Context containing variables for template rendering."""
    
    variables: Dict[str, str]
    
    def __init__(self, variables: Dict[str, str]):
        super().__init__(variables=variables)


class TemplateResult(BaseModel):
    """Result of template rendering operation."""
    
    content: str
    variables_used: Set[str]
    missing_variables: Set[str]
    original_template: str
    
    @property
    def is_complete(self) -> bool:
        """Check if all variables were successfully substituted."""
        return len(self.missing_variables) == 0


class Template(BaseModel):
    """Represents a loaded template."""
    
    content: str
    path: Optional[str] = None
    variables: Set[str]
    
    def __init__(self, content: str, path: Optional[str] = None, variables: Optional[Set[str]] = None):
        if variables is None:
            variables = set()
        super().__init__(content=content, path=path, variables=variables)