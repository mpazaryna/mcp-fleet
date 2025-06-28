# Fix GitHub Issue

Please analyze and fix the GitHub issue: $ARGUMENTS.

Follow these steps:

1. Use `gh issue view` to get the issue details
2. Understand the problem described in the issue
3. Search the codebase for relevant files
4. Implement the necessary changes to fix the issue
5. Write and run tests to verify the fix
6. Ensure code passes linting and type checking
7. Create a descriptive commit message
8. Push and create a PR

Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks.

## Usage

Use this command with an issue number:
```
/project:fix-github-issue 1234
```

This will systematically work through fixing GitHub issue #1234 following MCP Fleet's development best practices.

## Requirements

- GitHub CLI (`gh`) must be installed and authenticated
- Issue must exist in the repository
- Proper permissions to create branches and PRs