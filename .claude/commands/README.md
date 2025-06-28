# Claude Code Commands

This directory contains custom commands for Claude Code to streamline MCP Fleet development workflows.

## Available Commands

### `/project:fix-github-issue <issue_number>`

Systematically analyzes and fixes GitHub issues following MCP Fleet's development best practices.

**Usage:**
```
/project:fix-github-issue 1234
```

**Process:**
1. Fetches issue details using GitHub CLI
2. Analyzes the problem and searches relevant code
3. Implements necessary changes
4. Writes and runs tests to verify the fix
5. Ensures code passes linting and type checking
6. Creates descriptive commit message
7. Pushes changes and creates PR

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Proper repository permissions for branches and PRs

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