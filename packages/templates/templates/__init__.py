"""Template engine package for variable substitution in plain markdown files."""

from .engine import TemplateEngine
from .types import TemplateContext, TemplateResult

__all__ = ["TemplateEngine", "TemplateContext", "TemplateResult"]