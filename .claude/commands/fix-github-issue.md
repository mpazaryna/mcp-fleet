# Fix GitHub Issue

Please analyze and fix the GitHub issue: $ARGUMENTS.

Follow these steps:

1. Use `gh issue view` to get the issue details
2. Create a new branch from main using the issue number as the branch name
3. Understand the problem described in the issue
4. Search the codebase for relevant files
5. Implement the necessary changes to fix the issue
6. Write and run tests to verify the fix
7. Ensure code passes linting and type checking
8. Create descriptive commit messages referencing the issue
9. Push the branch and create a PR linking to the issue

## Gitflow Process

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create branch named after issue number
git checkout -b <issue-number>

# Work on the issue...

# Commit with issue reference
git commit -m "Fix: <description> (#<issue-number>)"

# Push branch
git push origin <issue-number>

# Create PR
gh pr create --title "Fix: <description>" --body "Fixes #<issue-number>" --base main
```

Remember to use the GitHub CLI (`gh`) for all GitHub-related tasks.

## Usage

Use this command with an issue number:
```
/project:fix-github-issue 1234
```

This will:
1. Create branch `1234` from main
2. Implement the fix for issue #1234
3. Create commits like `Fix: Update server architecture (#1234)`
4. Push branch and create PR that auto-closes the issue

## Branch Naming Convention

- Issue #42 → Branch name: `42`
- Issue #1234 → Branch name: `1234`
- No prefixes needed (no feature/, fix/, etc.)
- Simple, clean, directly tied to issue tracking

## Requirements

- GitHub CLI (`gh`) must be installed and authenticated
- Issue must exist in the repository
- Proper permissions to create branches and PRs