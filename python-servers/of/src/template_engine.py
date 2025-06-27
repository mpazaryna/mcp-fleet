"""
Generic Template Engine for Markdown Templates with Frontmatter

Provides a generic mechanism to:
1. Load markdown files with YAML frontmatter
2. Parse and validate template metadata
3. Inject variables into template content
4. Support template inheritance and composition
"""
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import jinja2
import aiofiles


class TemplateVariable(BaseModel):
    """Definition of a template variable"""
    name: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[str] = None
    type: str = "string"


class TemplateSection(BaseModel):
    """Definition of a template section for patterns"""
    title: str
    description: Optional[str] = None
    required: bool = True
    exploration_mappings: List[str] = Field(default_factory=list)


class TemplateMetadata(BaseModel):
    """Template frontmatter metadata"""
    name: str
    description: Optional[str] = None
    domain: Optional[str] = None
    variables: List[TemplateVariable] = Field(default_factory=list)
    sections: List[TemplateSection] = Field(default_factory=list)
    extends: Optional[str] = None  # For template inheritance
    tags: List[str] = Field(default_factory=list)


class ParsedTemplate(BaseModel):
    """A parsed template with metadata and content"""
    metadata: TemplateMetadata
    content: str
    file_path: Path


class TemplateEngine:
    """Generic template engine for markdown files with frontmatter"""
    
    def __init__(self, template_dirs: List[Path]):
        """
        Initialize template engine with template directories
        
        Args:
            template_dirs: List of directories to search for templates
        """
        self.template_dirs = [Path(d) for d in template_dirs]
        self.jinja_env = jinja2.Environment(
            variable_start_string='{{',
            variable_end_string='}}',
            undefined=jinja2.StrictUndefined
        )
        self._template_cache: Dict[str, ParsedTemplate] = {}
    
    async def load_template(self, template_name: str) -> Optional[ParsedTemplate]:
        """
        Load a template by name from template directories
        
        Args:
            template_name: Name of template (with or without .md extension)
            
        Returns:
            ParsedTemplate object or None if not found
        """
        # Normalize template name
        if not template_name.endswith('.md'):
            template_name += '.md'
        
        # Check cache first
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        # Search in template directories
        for template_dir in self.template_dirs:
            template_path = await self._find_template_file(template_dir, template_name)
            if template_path:
                template = await self._parse_template_file(template_path)
                if template:
                    self._template_cache[template_name] = template
                    return template
        
        return None
    
    async def _find_template_file(self, base_dir: Path, template_name: str) -> Optional[Path]:
        """Recursively find template file in directory"""
        if not base_dir.exists():
            return None
            
        # Direct match
        direct_path = base_dir / template_name
        if direct_path.exists() and direct_path.is_file():
            return direct_path
        
        # Search subdirectories
        for path in base_dir.rglob(template_name):
            if path.is_file():
                return path
                
        return None
    
    async def _parse_template_file(self, file_path: Path) -> Optional[ParsedTemplate]:
        """Parse template file with frontmatter"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Parse frontmatter and content
            frontmatter, template_content = self._parse_frontmatter(content)
            
            # Create metadata from frontmatter
            metadata = self._create_metadata(frontmatter, file_path.stem)
            
            return ParsedTemplate(
                metadata=metadata,
                content=template_content,
                file_path=file_path
            )
            
        except Exception as e:
            print(f"Error parsing template {file_path}: {e}")
            return None
    
    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content"""
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            frontmatter_yaml = match.group(1)
            template_content = match.group(2)
            
            try:
                frontmatter = yaml.safe_load(frontmatter_yaml) or {}
            except yaml.YAMLError:
                frontmatter = {}
        else:
            # No frontmatter found
            frontmatter = {}
            template_content = content
        
        return frontmatter, template_content.strip()
    
    def _create_metadata(self, frontmatter: Dict[str, Any], default_name: str) -> TemplateMetadata:
        """Create TemplateMetadata from frontmatter dict"""
        # Parse variables
        variables = []
        for var_data in frontmatter.get('variables', []):
            if isinstance(var_data, dict):
                variables.append(TemplateVariable(**var_data))
            elif isinstance(var_data, str):
                variables.append(TemplateVariable(name=var_data))
        
        # Parse sections
        sections = []
        for section_data in frontmatter.get('sections', []):
            if isinstance(section_data, dict):
                # Handle exploration_mappings field name variation
                if 'explorationMappings' in section_data:
                    section_data['exploration_mappings'] = section_data.pop('explorationMappings')
                sections.append(TemplateSection(**section_data))
        
        return TemplateMetadata(
            name=frontmatter.get('name', default_name),
            description=frontmatter.get('description'),
            domain=frontmatter.get('domain'),
            variables=variables,
            sections=sections,
            extends=frontmatter.get('extends'),
            tags=frontmatter.get('tags', [])
        )
    
    async def render_template(
        self, 
        template_name: str, 
        variables: Dict[str, Any],
        validate_required: bool = True
    ) -> Optional[str]:
        """
        Render template with provided variables
        
        Args:
            template_name: Name of template to render
            variables: Dictionary of variables to inject
            validate_required: Whether to validate required variables
            
        Returns:
            Rendered template content or None if error
        """
        template = await self.load_template(template_name)
        if not template:
            return None
        
        # Validate required variables
        if validate_required:
            missing_vars = self._validate_required_variables(template, variables)
            if missing_vars:
                raise ValueError(f"Missing required variables: {missing_vars}")
        
        # Handle template inheritance
        if template.metadata.extends:
            base_template = await self.load_template(template.metadata.extends)
            if base_template:
                # Merge content (simplified inheritance)
                content = base_template.content + "\n\n" + template.content
            else:
                content = template.content
        else:
            content = template.content
        
        # Render with Jinja2
        try:
            jinja_template = self.jinja_env.from_string(content)
            return jinja_template.render(**variables)
        except jinja2.TemplateError as e:
            print(f"Template rendering error: {e}")
            return None
    
    def _validate_required_variables(
        self, 
        template: ParsedTemplate, 
        variables: Dict[str, Any]
    ) -> List[str]:
        """Check for missing required variables"""
        missing = []
        for var in template.metadata.variables:
            if var.required and var.name not in variables:
                # Check if variable has a default value
                if var.default is None:
                    missing.append(var.name)
        return missing
    
    async def list_templates(self, domain: Optional[str] = None) -> List[ParsedTemplate]:
        """
        List all available templates, optionally filtered by domain
        
        Args:
            domain: Optional domain filter
            
        Returns:
            List of ParsedTemplate objects
        """
        templates = []
        
        for template_dir in self.template_dirs:
            if not template_dir.exists():
                continue
                
            for md_file in template_dir.rglob("*.md"):
                template = await self._parse_template_file(md_file)
                if template:
                    if domain is None or template.metadata.domain == domain:
                        templates.append(template)
        
        return templates
    
    async def get_template_info(self, template_name: str) -> Optional[TemplateMetadata]:
        """Get metadata for a template without loading full content"""
        template = await self.load_template(template_name)
        return template.metadata if template else None


# Convenience functions for common use cases
async def create_template_engine(base_path: Union[str, Path]) -> TemplateEngine:
    """Create template engine with standard directory structure"""
    base_path = Path(base_path)
    template_dirs = [
        base_path / "templates" / "patterns",
        base_path / "templates" / "prompts",
        base_path / "templates"  # Fallback
    ]
    return TemplateEngine(template_dirs)


async def render_prompt_template(
    template_engine: TemplateEngine,
    prompt_name: str,
    context: Dict[str, Any]
) -> Optional[str]:
    """Convenience function to render a prompt template"""
    return await template_engine.render_template(
        f"prompts/{prompt_name}",
        context,
        validate_required=False  # Prompts often have optional variables
    )


async def render_pattern_template(
    template_engine: TemplateEngine,
    pattern_name: str,
    variables: Dict[str, Any]
) -> Optional[str]:
    """Convenience function to render a pattern template"""
    return await template_engine.render_template(
        f"patterns/{pattern_name}",
        variables,
        validate_required=True  # Patterns should validate required variables
    )