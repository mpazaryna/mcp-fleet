"""
Git operation tools
"""
import asyncio
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

from mcp_core.types import MCPTool


# Schema definitions
class GitCommit(BaseModel):
    """Git commit information"""
    hash: str
    message: str
    author: str
    date: str


class GitStatusInputSchema(BaseModel):
    """Schema for git status input"""
    path: Optional[str] = Field(default=".", description="Path to git repository")


class GitStatusOutputSchema(BaseModel):
    """Schema for git status output"""
    branch: str
    ahead: int
    behind: int
    staged: List[str]
    modified: List[str]
    untracked: List[str]
    clean: bool


class GitLogInputSchema(BaseModel):
    """Schema for git log input"""
    path: Optional[str] = Field(default=".", description="Path to git repository")
    limit: Optional[int] = Field(default=10, description="Number of commits to show")
    oneline: Optional[bool] = Field(default=False, description="Show one line per commit")


class GitLogOutputSchema(BaseModel):
    """Schema for git log output"""
    commits: List[GitCommit]
    total: int


class GitCommitInputSchema(BaseModel):
    """Schema for git commit input"""
    path: Optional[str] = Field(default=".", description="Path to git repository")
    message: str = Field(description="Commit message")
    files: Optional[List[str]] = Field(default=None, description="Specific files to commit")


class GitCommitOutputSchema(BaseModel):
    """Schema for git commit output"""
    success: bool
    hash: Optional[str] = None
    message: str
    files_committed: int


class GitBranchInputSchema(BaseModel):
    """Schema for git branch input"""
    path: Optional[str] = Field(default=".", description="Path to git repository")
    list_all: Optional[bool] = Field(default=False, description="List all branches")


class GitBranchOutputSchema(BaseModel):
    """Schema for git branch output"""
    branches: List[str]
    current: str
    total: int


# Tool definitions
git_tools: List[MCPTool] = [
    MCPTool(
        name="git_status",
        description="Get git repository status",
        input_schema=GitStatusInputSchema.model_json_schema(),
        output_schema=GitStatusOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="git_log",
        description="Get git commit history",
        input_schema=GitLogInputSchema.model_json_schema(),
        output_schema=GitLogOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="git_commit",
        description="Create a git commit",
        input_schema=GitCommitInputSchema.model_json_schema(),
        output_schema=GitCommitOutputSchema.model_json_schema(),
    ),
    MCPTool(
        name="git_branch",
        description="List git branches",
        input_schema=GitBranchInputSchema.model_json_schema(),
        output_schema=GitBranchOutputSchema.model_json_schema(),
    ),
]


# Helper function to run git commands
async def run_git_command(args: List[str], cwd: str = ".") -> tuple[str, str]:
    """Run a git command and return stdout, stderr"""
    try:
        process = await asyncio.create_subprocess_exec(
            "git", *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Git command failed: {stderr.decode()}")
        
        return stdout.decode().strip(), stderr.decode().strip()
        
    except FileNotFoundError:
        raise Exception("Git is not installed or not found in PATH")


# Tool handlers
async def git_status_handler(args: dict) -> dict:
    """Git status handler"""
    validated_args = GitStatusInputSchema(**args)
    repo_path = Path(validated_args.path)
    
    try:
        # Get current branch
        stdout, _ = await run_git_command(["branch", "--show-current"], str(repo_path))
        current_branch = stdout or "HEAD"
        
        # Get status --porcelain for parsing
        stdout, _ = await run_git_command(["status", "--porcelain"], str(repo_path))
        
        staged = []
        modified = []
        untracked = []
        
        for line in stdout.splitlines():
            if line:
                status = line[:2]
                filename = line[3:]
                
                if status[0] in ['A', 'M', 'D', 'R', 'C']:
                    staged.append(filename)
                if status[1] in ['M', 'D']:
                    modified.append(filename)
                if status[0] == '?' and status[1] == '?':
                    untracked.append(filename)
        
        # Check if ahead/behind remote
        ahead = 0
        behind = 0
        try:
            stdout, _ = await run_git_command(
                ["rev-list", "--left-right", "--count", f"origin/{current_branch}...HEAD"],
                str(repo_path)
            )
            if stdout:
                parts = stdout.split('\t')
                if len(parts) == 2:
                    behind = int(parts[0])
                    ahead = int(parts[1])
        except:
            # Ignore errors for ahead/behind (remote might not exist)
            pass
        
        clean = len(staged) == 0 and len(modified) == 0 and len(untracked) == 0
        
        return GitStatusOutputSchema(
            branch=current_branch,
            ahead=ahead,
            behind=behind,
            staged=staged,
            modified=modified,
            untracked=untracked,
            clean=clean
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to get git status: {str(error)}")


async def git_log_handler(args: dict) -> dict:
    """Git log handler"""
    validated_args = GitLogInputSchema(**args)
    repo_path = Path(validated_args.path)
    
    try:
        git_args = ["log", f"--max-count={validated_args.limit}"]
        
        if validated_args.oneline:
            git_args.append("--oneline")
            format_str = "--pretty=format:%H|%s|%an|%ad"
        else:
            format_str = "--pretty=format:%H|%s|%an|%ad"
        
        git_args.extend([format_str, "--date=iso"])
        
        stdout, _ = await run_git_command(git_args, str(repo_path))
        
        commits = []
        for line in stdout.splitlines():
            if line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append(GitCommit(
                        hash=parts[0],
                        message=parts[1],
                        author=parts[2],
                        date=parts[3]
                    ))
        
        return GitLogOutputSchema(
            commits=commits,
            total=len(commits)
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to get git log: {str(error)}")


async def git_commit_handler(args: dict) -> dict:
    """Git commit handler"""
    validated_args = GitCommitInputSchema(**args)
    repo_path = Path(validated_args.path)
    
    try:
        # Add files if specified
        if validated_args.files:
            for file in validated_args.files:
                await run_git_command(["add", file], str(repo_path))
        else:
            # Add all staged files
            await run_git_command(["add", "-A"], str(repo_path))
        
        # Create commit
        await run_git_command(["commit", "-m", validated_args.message], str(repo_path))
        
        # Get commit hash
        stdout, _ = await run_git_command(["rev-parse", "HEAD"], str(repo_path))
        commit_hash = stdout
        
        # Count committed files (approximate)
        stdout, _ = await run_git_command(["show", "--name-only", "HEAD"], str(repo_path))
        files_committed = len(stdout.splitlines()) - 1  # Subtract commit message line
        
        return GitCommitOutputSchema(
            success=True,
            hash=commit_hash,
            message=validated_args.message,
            files_committed=files_committed
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to create git commit: {str(error)}")


async def git_branch_handler(args: dict) -> dict:
    """Git branch handler"""
    validated_args = GitBranchInputSchema(**args)
    repo_path = Path(validated_args.path)
    
    try:
        git_args = ["branch"]
        if validated_args.list_all:
            git_args.append("-a")
        
        stdout, _ = await run_git_command(git_args, str(repo_path))
        
        branches = []
        current = ""
        
        for line in stdout.splitlines():
            line = line.strip()
            if line:
                if line.startswith("* "):
                    current = line[2:]
                    branches.append(current)
                else:
                    branches.append(line)
        
        return GitBranchOutputSchema(
            branches=branches,
            current=current,
            total=len(branches)
        ).model_dump()
        
    except Exception as error:
        raise Exception(f"Failed to list git branches: {str(error)}")


# Handler mapping
git_handlers = {
    "git_status": git_status_handler,
    "git_log": git_log_handler,
    "git_commit": git_commit_handler,
    "git_branch": git_branch_handler,
}