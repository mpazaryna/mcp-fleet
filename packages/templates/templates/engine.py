"""Template engine implementation for variable substitution in plain markdown files."""

import re
from pathlib import Path
from typing import Set, Optional, Any

from .types import TemplateContext, TemplateResult, Template


class TemplateEngine:
    """Template engine for processing plain markdown files with variable substitution."""
    
    def __init__(self):
        """Initialize the template engine."""
        # Pattern to match ${variable_name} syntax
        self.variable_pattern = re.compile(r'\$\{([^}]+)\}')
    
    def extract_variables(self, content: str) -> Set[str]:
        """Extract all variable names from template content.
        
        Args:
            content: Template content to scan for variables
            
        Returns:
            Set of variable names found in the template
        """
        matches = self.variable_pattern.findall(content)
        return set(matches)
    
    async def load_template(self, template_path: str) -> Template:
        """Load a template from a file path.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            Template object with loaded content and extracted variables
        """
        path = Path(template_path)
        content = path.read_text(encoding='utf-8')
        variables = self.extract_variables(content)
        
        return Template(content=content, path=template_path, variables=variables)
    
    async def load_template_from_string(self, content: str) -> Template:
        """Load a template from a string.
        
        Args:
            content: Template content as string
            
        Returns:
            Template object with content and extracted variables
        """
        variables = self.extract_variables(content)
        return Template(content=content, path=None, variables=variables)
    
    def render(self, template_content: str, context: TemplateContext) -> TemplateResult:
        """Render a template with the given context.
        
        Args:
            template_content: The template content to render
            context: Context containing variables for substitution
            
        Returns:
            TemplateResult with rendered content and metadata
        """
        # Extract all variables from template
        all_variables = self.extract_variables(template_content)
        
        # Track which variables we actually use
        variables_used = set()
        rendered_content = template_content
        
        # Substitute each variable that we have in the context
        for variable in all_variables:
            if variable in context.variables:
                pattern = f"${{{variable}}}"
                rendered_content = rendered_content.replace(pattern, context.variables[variable])
                variables_used.add(variable)
        
        # Calculate missing variables
        missing_variables = all_variables - variables_used
        
        return TemplateResult(
            content=rendered_content,
            variables_used=variables_used,
            missing_variables=missing_variables,
            original_template=template_content
        )
    
    async def render_and_save(
        self, 
        template_content: str, 
        context: TemplateContext, 
        output_path: str,
        storage_backend: Any
    ) -> TemplateResult:
        """Render a template and save it using the storage backend.
        
        Args:
            template_content: The template content to render
            context: Context containing variables for substitution
            output_path: Path where to save the rendered content
            storage_backend: Storage backend to use for saving
            
        Returns:
            TemplateResult with rendered content and metadata
        """
        result = self.render(template_content, context)
        await storage_backend.write_file(output_path, result.content)
        return result