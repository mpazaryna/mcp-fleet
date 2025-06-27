"""
Prompt Manager for AI Conversation Templates

Manages AI system prompts stored as markdown templates with context injection.
Enables systematic AI guidance through different phases of the orchestration methodology.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel
from enum import Enum
import logging

try:
    from .template_engine import TemplateEngine, create_template_engine
except ImportError:
    from template_engine import TemplateEngine, create_template_engine


logger = logging.getLogger(__name__)


class MethodologyPhase(str, Enum):
    """Phases of the orchestration methodology"""
    EXPLORATION = "exploration"
    SPECIFICATION = "specification"
    EXECUTION = "execution"
    FEEDBACK = "feedback"
    FLYWHEEL = "flywheel"


class ConversationContext(BaseModel):
    """Context for AI conversation prompts"""
    project_name: str
    current_phase: MethodologyPhase
    session_count: int = 1
    previous_sessions: List[str] = []
    project_description: Optional[str] = None
    exploration_progress: Optional[str] = None
    specification_status: Optional[str] = None
    execution_progress: Optional[str] = None
    current_tasks: List[str] = []
    recent_insights: List[str] = []
    identified_gaps: List[str] = []
    custom_context: Dict[str, Any] = {}
    
    def to_prompt_variables(self) -> Dict[str, Any]:
        """Convert context to variables for prompt template rendering"""
        return {
            'PROJECT_NAME': self.project_name,
            'CURRENT_PHASE': self.current_phase.value,
            'SESSION_COUNT': self.session_count,
            'PROJECT_DESCRIPTION': self.project_description or "Not yet defined",
            'EXPLORATION_PROGRESS': self.exploration_progress or "Just starting",
            'SPECIFICATION_STATUS': self.specification_status or "Not started",
            'EXECUTION_PROGRESS': self.execution_progress or "Not started",
            'CURRENT_TASKS': '\n'.join(f"- {task}" for task in self.current_tasks) if self.current_tasks else "No specific tasks yet",
            'RECENT_INSIGHTS': '\n'.join(f"- {insight}" for insight in self.recent_insights) if self.recent_insights else "No recent insights",
            'IDENTIFIED_GAPS': '\n'.join(f"- {gap}" for gap in self.identified_gaps) if self.identified_gaps else "No gaps identified",
            'PREVIOUS_SESSIONS_COUNT': len(self.previous_sessions),
            'HAS_PREVIOUS_SESSIONS': len(self.previous_sessions) > 0,
            **self.custom_context
        }


class PromptManager:
    """Manages AI conversation prompts with context injection"""
    
    def __init__(self, template_engine: TemplateEngine):
        """
        Initialize prompt manager
        
        Args:
            template_engine: Template engine instance
        """
        self.template_engine = template_engine
        self._prompt_cache: Dict[str, str] = {}
    
    async def get_phase_prompt(
        self, 
        phase: MethodologyPhase, 
        context: ConversationContext
    ) -> Optional[str]:
        """
        Get the system prompt for a specific methodology phase
        
        Args:
            phase: Methodology phase
            context: Conversation context
            
        Returns:
            Rendered system prompt or None if error
        """
        logger.debug(f"Getting prompt for phase: {phase}")
        
        try:
            prompt_name = f"prompts/{phase.value}.md"
            variables = context.to_prompt_variables()
            
            rendered_prompt = await self.template_engine.render_template(
                prompt_name,
                variables,
                validate_required=False  # Prompts often have optional variables
            )
            
            if rendered_prompt:
                logger.debug(f"Successfully rendered {phase} prompt with {len(variables)} variables")
            else:
                logger.warning(f"Failed to render prompt for phase {phase}")
            
            return rendered_prompt
            
        except Exception as e:
            logger.error(f"Error getting prompt for phase {phase}: {e}")
            return None
    
    async def get_exploration_prompt(self, context: ConversationContext) -> Optional[str]:
        """Get exploration phase prompt with focus on problem space"""
        context.current_phase = MethodologyPhase.EXPLORATION
        return await self.get_phase_prompt(MethodologyPhase.EXPLORATION, context)
    
    async def get_specification_prompt(self, context: ConversationContext) -> Optional[str]:
        """Get specification phase prompt with exploration insights"""
        context.current_phase = MethodologyPhase.SPECIFICATION
        return await self.get_phase_prompt(MethodologyPhase.SPECIFICATION, context)
    
    async def get_execution_prompt(self, context: ConversationContext) -> Optional[str]:
        """Get execution phase prompt with specification details"""
        context.current_phase = MethodologyPhase.EXECUTION
        return await self.get_phase_prompt(MethodologyPhase.EXECUTION, context)
    
    async def get_flywheel_prompt(self, context: ConversationContext) -> Optional[str]:
        """Get flywheel prompt for iterative improvement"""
        context.current_phase = MethodologyPhase.FLYWHEEL
        return await self.get_phase_prompt(MethodologyPhase.FLYWHEEL, context)
    
    async def get_custom_prompt(
        self, 
        prompt_name: str, 
        context: ConversationContext,
        additional_variables: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Get a custom prompt with context injection
        
        Args:
            prompt_name: Name of the prompt template
            context: Conversation context
            additional_variables: Additional variables to include
            
        Returns:
            Rendered prompt or None if error
        """
        logger.debug(f"Getting custom prompt: {prompt_name}")
        
        try:
            variables = context.to_prompt_variables()
            
            if additional_variables:
                variables.update(additional_variables)
            
            rendered_prompt = await self.template_engine.render_template(
                prompt_name,
                variables,
                validate_required=False
            )
            
            return rendered_prompt
            
        except Exception as e:
            logger.error(f"Error getting custom prompt {prompt_name}: {e}")
            return None
    
    async def create_session_continuation_prompt(
        self,
        context: ConversationContext,
        last_session_summary: str
    ) -> Optional[str]:
        """
        Create a prompt for continuing a previous session
        
        Args:
            context: Current conversation context
            last_session_summary: Summary of the last session
            
        Returns:
            Session continuation prompt
        """
        try:
            continuation_variables = {
                'LAST_SESSION_SUMMARY': last_session_summary,
                'IS_CONTINUATION': True,
                'SESSIONS_SO_FAR': context.session_count - 1
            }
            
            base_prompt = await self.get_phase_prompt(context.current_phase, context)
            if not base_prompt:
                return None
            
            # Add continuation context
            continuation_prompt = await self.get_custom_prompt(
                "prompts/session_continuation.md",
                context,
                continuation_variables
            )
            
            if continuation_prompt:
                return f"{base_prompt}\n\n{continuation_prompt}"
            else:
                # Fallback to base prompt with simple continuation note
                return f"{base_prompt}\n\n## Session Continuation\n\nThis is session {context.session_count} for this project. Previous session summary:\n{last_session_summary}"
            
        except Exception as e:
            logger.error(f"Error creating session continuation prompt: {e}")
            return None
    
    async def create_gap_analysis_prompt(
        self,
        context: ConversationContext,
        identified_gaps: List[str]
    ) -> Optional[str]:
        """
        Create a prompt for gap analysis and flywheel iteration
        
        Args:
            context: Current conversation context
            identified_gaps: List of identified gaps
            
        Returns:
            Gap analysis prompt
        """
        try:
            gap_variables = {
                'IDENTIFIED_GAPS': '\n'.join(f"- {gap}" for gap in identified_gaps),
                'GAP_COUNT': len(identified_gaps),
                'NEEDS_FLYWHEEL': True
            }
            
            return await self.get_custom_prompt(
                "prompts/gap_analysis.md",
                context,
                gap_variables
            )
            
        except Exception as e:
            logger.error(f"Error creating gap analysis prompt: {e}")
            return None
    
    async def list_available_prompts(self) -> List[str]:
        """List all available prompt templates"""
        try:
            templates = await self.template_engine.list_templates()
            prompts = [
                t.metadata.name for t in templates 
                if 'prompt' in str(t.file_path).lower() or t.file_path.parent.name == 'prompts'
            ]
            return sorted(prompts)
            
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []
    
    async def validate_prompt_template(self, prompt_name: str) -> Dict[str, Any]:
        """
        Validate a prompt template
        
        Args:
            prompt_name: Name of prompt to validate
            
        Returns:
            Validation results
        """
        try:
            template = await self.template_engine.load_template(prompt_name)
            if not template:
                return {'valid': False, 'error': 'Prompt template not found'}
            
            # Test render with minimal context
            test_context = ConversationContext(
                project_name="Test Project",
                current_phase=MethodologyPhase.EXPLORATION
            )
            
            test_render = await self.template_engine.render_template(
                prompt_name,
                test_context.to_prompt_variables(),
                validate_required=False
            )
            
            return {
                'valid': True,
                'name': template.metadata.name,
                'variables': len(template.metadata.variables),
                'can_render': test_render is not None,
                'content_length': len(template.content),
                'file_path': str(template.file_path)
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}


# Factory function
async def create_prompt_manager(base_path: Union[str, Path]) -> PromptManager:
    """Create prompt manager with template engine"""
    template_engine = await create_template_engine(base_path)
    return PromptManager(template_engine)


# Utility functions for common prompt scenarios
async def create_exploration_context(
    project_name: str,
    project_description: Optional[str] = None,
    session_count: int = 1
) -> ConversationContext:
    """Create context for exploration phase"""
    return ConversationContext(
        project_name=project_name,
        current_phase=MethodologyPhase.EXPLORATION,
        project_description=project_description,
        session_count=session_count
    )


async def create_specification_context(
    project_name: str,
    exploration_progress: str,
    session_count: int = 1
) -> ConversationContext:
    """Create context for specification phase"""
    return ConversationContext(
        project_name=project_name,
        current_phase=MethodologyPhase.SPECIFICATION,
        exploration_progress=exploration_progress,
        session_count=session_count
    )


async def create_flywheel_context(
    project_name: str,
    identified_gaps: List[str],
    session_count: int = 1
) -> ConversationContext:
    """Create context for flywheel iteration"""
    return ConversationContext(
        project_name=project_name,
        current_phase=MethodologyPhase.FLYWHEEL,
        identified_gaps=identified_gaps,
        session_count=session_count
    )