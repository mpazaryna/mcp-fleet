"""
common_tools - Shared MCP tools

Provides reusable MCP tools for file operations, project discovery,
and git operations that can be used across multiple MCP servers.
"""

from .file_tools import (
    file_tools,
    file_handlers,
    ReadFileInputSchema,
    ReadFileOutputSchema,
    WriteFileInputSchema,
    WriteFileOutputSchema,
    ListDirectoryInputSchema,
    ListDirectoryOutputSchema,
    FileExistsInputSchema,
    FileExistsOutputSchema,
)

from .project_tools import (
    project_tools,
    project_handlers,
    FindProjectsInputSchema,
    FindProjectsOutputSchema,
    GetProjectInfoInputSchema,
    GetProjectInfoOutputSchema,
    CreateProjectInputSchema,
    CreateProjectOutputSchema,
)

from .git_tools import (
    git_tools,
    git_handlers,
    GitStatusInputSchema,
    GitStatusOutputSchema,
    GitLogInputSchema,
    GitLogOutputSchema,
    GitCommitInputSchema,
    GitCommitOutputSchema,
    GitBranchInputSchema,
    GitBranchOutputSchema,
)

# Combined exports for convenience
all_tools = [
    *file_tools,
    *project_tools,
    *git_tools,
]

all_handlers = {
    **file_handlers,
    **project_handlers,
    **git_handlers,
}

__all__ = [
    # File tools
    "file_tools",
    "file_handlers",
    "ReadFileInputSchema",
    "ReadFileOutputSchema", 
    "WriteFileInputSchema",
    "WriteFileOutputSchema",
    "ListDirectoryInputSchema",
    "ListDirectoryOutputSchema",
    "FileExistsInputSchema",
    "FileExistsOutputSchema",
    # Project tools
    "project_tools",
    "project_handlers",
    "FindProjectsInputSchema",
    "FindProjectsOutputSchema",
    "GetProjectInfoInputSchema",
    "GetProjectInfoOutputSchema",
    "CreateProjectInputSchema",
    "CreateProjectOutputSchema",
    # Git tools
    "git_tools",
    "git_handlers",
    "GitStatusInputSchema",
    "GitStatusOutputSchema",
    "GitLogInputSchema",
    "GitLogOutputSchema",
    "GitCommitInputSchema",
    "GitCommitOutputSchema",
    "GitBranchInputSchema",
    "GitBranchOutputSchema",
    # Combined
    "all_tools",
    "all_handlers",
]