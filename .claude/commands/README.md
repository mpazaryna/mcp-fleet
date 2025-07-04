# Claude Code Commands

This directory contains custom commands for Claude Code to streamline MCP Fleet development workflows.

## Available Commands

### `/project:issue-fix <issue_number>`

Systematically analyzes and fixes GitHub issues following MCP Fleet's development best practices.

**Usage:**
```
/project:issue-fix 1234
```

**Process:**
1. Fetches issue details using GitHub CLI
2. Creates new branch from main using issue number as branch name
3. Analyzes the problem and searches relevant code
4. Implements necessary changes
5. Writes and runs tests to verify the fix
6. Ensures code passes linting and type checking
7. Creates descriptive commit messages with issue references
8. Pushes branch and creates PR linking to the issue

**Gitflow:**
- Branch names match issue numbers (e.g., issue #42 → branch `42`)
- No prefixes needed (no feature/, fix/, etc.)
- Commits reference issues (e.g., `Fix: Description (#42)`)
- PRs automatically close linked issues

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Proper repository permissions for branches and PRs

### `/project:issue write <planning_notes>`

Creates well-structured GitHub issues from planning sessions or requirements discussions.

**Usage:**
```
/project:issue-write "Add new workflow management features to tides server"
```

**Process:**
1. Analyzes planning session notes or requirements
2. Structures information using standardized template
3. Creates comprehensive issue with:
   - Clear issue description
   - Detailed requirements
   - Current state documentation
   - Testable acceptance criteria
   - Source references
   - Priority assessment
4. Applies appropriate labels
5. Creates issue using GitHub CLI

**Template Sections:**
- **Issue Description** - Clear problem statement and purpose
- **Requirements** - Numbered list of specific needs
- **Current State** - What exists now and gaps
- **Acceptance Criteria** - Checklist of measurable outcomes
- **Source** - Reference to planning materials
- **Priority** - High/Medium/Low with justification

## Adding Your Own Commands

You can add additional `.md` files to this directory to create custom commands for your workflow. Each command file should:

1. Start with a clear description of what the command does
2. Include usage examples
3. Document any requirements or prerequisites
4. Follow the established naming convention

## Best Practices

- Commands should follow MCP Fleet's TDD methodology
- Always include test verification steps
- Use GitHub CLI for all GitHub-related operations
- Maintain consistency with the project's coding standards
- Document any new commands in this README