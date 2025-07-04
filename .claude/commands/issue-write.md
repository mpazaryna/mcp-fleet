# Write GitHub Issue

Please create a GitHub issue from the planning session or requirements: $ARGUMENTS.

Follow this standardized format to ensure high-quality issue creation:

## Issue Template Structure

```markdown
## Issue Description
[Clear, concise description of what needs to be done and why]

## Requirements
**[Main requirement statement]**:
1. **[Component/Feature]** - [Specific question or requirement]
2. **[Component/Feature]** - [Specific question or requirement]
[Additional numbered requirements as needed]

[Decision points if applicable]:
- [Option 1]
- [Option 2]
- [Option 3]

## Current State
- [What exists now]
- [Current problems or gaps]
- [User impact or confusion points]
- [Technical debt or redundancies]

## Acceptance Criteria
- [ ] [Specific, measurable outcome]
- [ ] [Specific, measurable outcome]
- [ ] [Documentation requirement]
- [ ] [Testing requirement]
- [ ] [User-facing changes]
- [ ] [Technical implementation detail]
- [ ] [Cleanup or refactoring task]

## Source
[Reference to planning session, user feedback, or documentation]

## Priority
[High/Medium/Low] - [Brief justification]
```

## Process

1. Analyze the planning session or requirements provided
2. Structure the information according to the template
3. Ensure each section is complete and specific
4. Add appropriate labels based on issue type:
   - `enhancement` for new features
   - `bug` for fixes
   - `documentation` for docs
   - `refactor` for code improvements
   - `question` for clarifications needed
5. Use `gh issue create` with the formatted content
6. Assign to appropriate team members if specified
7. Link to related issues or PRs if applicable

## Example Usage

```
/project:write-github-issue "From our planning session: We need to add Apple Calendar integration to the local server, similar to Apple Notes"
```

This would create a properly formatted issue with:
- Clear description of adding Calendar integration
- Requirements broken down by component
- Current state (Apple Notes exists, Calendar doesn't)
- Specific acceptance criteria
- Proper labels and priority

## Best Practices

- Keep descriptions concise but complete
- Make acceptance criteria testable
- Always include current state for context
- Reference source materials (planning docs, user feedback)
- Set realistic priorities with justification
- Use consistent terminology with the project

## GitHub CLI Command

The final command will be:
```bash
gh issue create \
  --title "[Concise title from description]" \
  --body "[Full formatted content]" \
  --label "[appropriate labels]" \
  --project "[if applicable]"
```