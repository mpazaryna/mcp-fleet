"""
Pattern Manager for Domain-Specific Specification Templates

Manages loading, validation, and rendering of specification patterns
for different domains (software, business, personal).
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel
import logging

try:
    from .template_engine import TemplateEngine, ParsedTemplate, create_template_engine
except ImportError:
    from template_engine import TemplateEngine, ParsedTemplate, create_template_engine


logger = logging.getLogger(__name__)


class ExplorationInsights(BaseModel):
    """Structured exploration insights from project exploration phase"""
    user_pain_points: Optional[str] = None
    goals: Optional[str] = None
    stakeholders: Optional[str] = None
    constraints: Optional[str] = None
    success_criteria: Optional[str] = None
    technical_considerations: Optional[str] = None
    core_features: Optional[str] = None
    business_value: Optional[str] = None
    user_stories: Optional[str] = None
    risks: Optional[str] = None
    assumptions: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {k.upper(): v for k, v in self.dict().items() if v is not None}


class PatternRenderContext(BaseModel):
    """Context for rendering a specification pattern"""
    project_name: str
    domain: str
    pattern_name: str
    exploration_insights: ExplorationInsights
    custom_variables: Dict[str, Any] = {}
    
    def get_template_variables(self) -> Dict[str, Any]:
        """Get all variables for template rendering"""
        variables = {
            'PROJECT_NAME': self.project_name,
            'DOMAIN': self.domain,
            'PATTERN_NAME': self.pattern_name,
        }
        
        # Add exploration insights with proper mapping
        variables.update(self.exploration_insights.to_dict())
        
        # Add custom variables
        variables.update(self.custom_variables)
        
        return variables


class PatternManager:
    """Manages specification patterns for different domains"""
    
    def __init__(self, template_engine: TemplateEngine):
        """
        Initialize pattern manager
        
        Args:
            template_engine: Template engine instance
        """
        self.template_engine = template_engine
        self._pattern_cache: Dict[str, ParsedTemplate] = {}
    
    async def load_available_patterns(self) -> List[ParsedTemplate]:
        """Load all available patterns from the filesystem"""
        logger.debug("Loading available patterns from filesystem")
        
        try:
            patterns = await self.template_engine.list_templates()
            # Filter to only include patterns (have domain metadata)
            pattern_templates = [
                p for p in patterns 
                if p.metadata.domain is not None
            ]
            
            logger.debug(f"Loaded {len(pattern_templates)} patterns")
            return pattern_templates
            
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
            return []
    
    async def load_pattern(self, pattern_name: str) -> Optional[ParsedTemplate]:
        """
        Load a specific pattern by name
        
        Args:
            pattern_name: Name of the pattern (with or without .md extension)
            
        Returns:
            ParsedTemplate or None if not found
        """
        logger.debug(f"Loading pattern: {pattern_name}")
        
        try:
            # Try direct load first
            pattern = await self.template_engine.load_template(pattern_name)
            if pattern and pattern.metadata.domain:
                return pattern
            
            # Search in patterns subdirectory
            pattern = await self.template_engine.load_template(f"patterns/{pattern_name}")
            if pattern and pattern.metadata.domain:
                return pattern
            
            logger.warning(f"Pattern not found: {pattern_name}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load pattern {pattern_name}: {e}")
            return None
    
    async def get_patterns_by_domain(self, domain: str) -> List[ParsedTemplate]:
        """
        Get all patterns for a specific domain
        
        Args:
            domain: Domain name (e.g., 'software', 'business', 'personal')
            
        Returns:
            List of patterns for the domain
        """
        logger.debug(f"Getting patterns for domain: {domain}")
        
        patterns = await self.load_available_patterns()
        domain_patterns = [
            p for p in patterns 
            if p.metadata.domain == domain
        ]
        
        logger.debug(f"Found {len(domain_patterns)} patterns for domain {domain}")
        return domain_patterns
    
    async def suggest_patterns(
        self, 
        project_type: str, 
        keywords: List[str] = None
    ) -> List[ParsedTemplate]:
        """
        Suggest patterns based on project type and keywords
        
        Args:
            project_type: Type of project (maps to domain)
            keywords: Optional keywords to match against pattern tags/descriptions
            
        Returns:
            List of suggested patterns
        """
        # Map project types to domains
        domain_mapping = {
            'software': 'software',
            'web': 'software', 
            'mobile': 'software',
            'api': 'software',
            'business': 'business',
            'startup': 'business',
            'process': 'business',
            'personal': 'personal',
            'learning': 'personal',
            'skill': 'personal'
        }
        
        domain = domain_mapping.get(project_type.lower(), 'software')
        patterns = await self.get_patterns_by_domain(domain)
        
        # Filter by keywords if provided
        if keywords:
            keyword_set = {kw.lower() for kw in keywords}
            filtered_patterns = []
            
            for pattern in patterns:
                # Check tags
                pattern_tags = {tag.lower() for tag in pattern.metadata.tags}
                # Check description
                description_words = set()
                if pattern.metadata.description:
                    description_words = set(pattern.metadata.description.lower().split())
                
                # Check if any keywords match
                if keyword_set & (pattern_tags | description_words):
                    filtered_patterns.append(pattern)
            
            patterns = filtered_patterns
        
        return patterns
    
    async def render_specification(
        self, 
        context: PatternRenderContext
    ) -> Optional[str]:
        """
        Render a specification using a pattern and exploration insights
        
        Args:
            context: Render context with pattern name, project info, and insights
            
        Returns:
            Rendered specification content or None if error
        """
        logger.debug(f"Rendering specification with pattern: {context.pattern_name}")
        
        try:
            # Load the pattern
            pattern = await self.load_pattern(context.pattern_name)
            if not pattern:
                logger.error(f"Pattern not found: {context.pattern_name}")
                return None
            
            # Get template variables
            variables = context.get_template_variables()
            
            # Add pattern-specific variable mappings
            enhanced_variables = await self._enhance_variables_with_mappings(
                pattern, variables, context.exploration_insights
            )
            
            # Render the specification
            rendered = await self.template_engine.render_template(
                pattern.file_path.name,
                enhanced_variables,
                validate_required=True
            )
            
            if rendered:
                logger.debug(f"Successfully rendered specification with {len(enhanced_variables)} variables")
            else:
                logger.error("Template rendering returned None")
            
            return rendered
            
        except Exception as e:
            logger.error(f"Failed to render specification: {e}")
            return None
    
    async def _enhance_variables_with_mappings(
        self,
        pattern: ParsedTemplate,
        base_variables: Dict[str, Any],
        insights: ExplorationInsights
    ) -> Dict[str, Any]:
        """
        Enhance variables using pattern section mappings
        
        This maps exploration insights to specific pattern sections
        based on the explorationMappings defined in the pattern.
        """
        enhanced = base_variables.copy()
        insights_dict = insights.dict()
        
        # Process each section's exploration mappings
        for section in pattern.metadata.sections:
            if section.exploration_mappings:
                section_content = []
                
                for mapping in section.exploration_mappings:
                    # Convert camelCase to snake_case for matching
                    snake_case_mapping = self._camel_to_snake(mapping)
                    
                    if snake_case_mapping in insights_dict:
                        value = insights_dict[snake_case_mapping]
                        if value:
                            section_content.append(str(value))
                
                # Create a variable for this section
                section_var_name = self._title_to_variable(section.title)
                if section_content:
                    enhanced[section_var_name] = '\n\n'.join(section_content)
                else:
                    enhanced[section_var_name] = f"[{section.title} - To be defined]"
        
        return enhanced
    
    def _camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _title_to_variable(self, title: str) -> str:
        """Convert section title to variable name"""
        return title.upper().replace(' ', '_').replace('&', 'AND')
    
    async def validate_pattern(self, pattern_name: str) -> Dict[str, Any]:
        """
        Validate a pattern and return validation results
        
        Args:
            pattern_name: Name of pattern to validate
            
        Returns:
            Dictionary with validation results
        """
        pattern = await self.load_pattern(pattern_name)
        if not pattern:
            return {'valid': False, 'error': 'Pattern not found'}
        
        validation = {
            'valid': True,
            'name': pattern.metadata.name,
            'domain': pattern.metadata.domain,
            'variables': len(pattern.metadata.variables),
            'required_variables': [
                v.name for v in pattern.metadata.variables if v.required
            ],
            'sections': len(pattern.metadata.sections),
            'has_content': len(pattern.content.strip()) > 0,
            'file_path': str(pattern.file_path)
        }
        
        return validation


# Factory functions
async def create_pattern_manager(base_path: Union[str, Path]) -> PatternManager:
    """Create pattern manager with template engine"""
    template_engine = await create_template_engine(base_path)
    return PatternManager(template_engine)


# Utility function for creating exploration insights from conversation
def create_exploration_insights(conversation_content: str) -> ExplorationInsights:
    """
    Extract structured insights from exploration conversation content
    
    This is a simplified version - in practice, you might use AI to parse
    the conversation and extract key insights.
    """
    insights = ExplorationInsights()
    
    # Simple keyword-based extraction (can be enhanced with AI)
    content_lower = conversation_content.lower()
    
    if 'pain point' in content_lower or 'problem' in content_lower:
        # Extract pain points section
        insights.user_pain_points = "Extracted from exploration conversation"
    
    if 'goal' in content_lower or 'objective' in content_lower:
        insights.goals = "Extracted from exploration conversation"
    
    # Add more extraction logic as needed
    
    return insights