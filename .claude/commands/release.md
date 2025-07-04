# Release

Create a new release following gitflow methodology with semantic versioning.

## Usage

```
/project:release <version-type>
```

Where `<version-type>` is one of:
- `patch` - Bug fixes, minor changes (1.0.0 → 1.0.1)
- `minor` - New features, backwards compatible (1.0.0 → 1.1.0)
- `major` - Breaking changes (1.0.0 → 2.0.0)

Example:
```
/project:release minor
```

## What This Command Does

1. **Validates Current State**
   - Ensures you're on a feature branch (not main)
   - Checks for clean working directory
   - Confirms all changes are committed

2. **Merges to Main**
   - Switches to main branch
   - Pulls latest changes
   - Merges feature branch using --no-ff for clear history

3. **Creates Version Tag**
   - Determines next version based on type
   - Creates annotated tag with release message
   - Updates pyproject.toml files with new version
   - Updates CHANGELOG.md with release notes and date

4. **Pushes Everything**
   - Pushes main branch
   - Pushes new tag
   - Deletes merged feature branch locally and remotely

5. **Provides Summary**
   - Shows new version number
   - Lists changes included in release
   - Provides GitHub release URL

## Success Criteria

- ✅ Feature branch successfully merged to main
- ✅ Semantic version tag created and pushed
- ✅ pyproject.toml files updated with new version
- ✅ CHANGELOG.md updated with release notes
- ✅ All changes pushed to GitHub
- ✅ Feature branch cleaned up
- ✅ Clear release notes provided

## Implementation

```bash
#!/bin/bash

# Parse arguments
VERSION_TYPE="${1:-patch}"

if [[ ! "$VERSION_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo "Error: Version type must be 'patch', 'minor', or 'major'"
    echo "Usage: /project:release <patch|minor|major>"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Validate we're not on main
if [[ "$CURRENT_BRANCH" == "main" ]]; then
    echo "Error: Cannot release from main branch. Please work on a feature branch."
    exit 1
fi

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
    echo "Error: You have uncommitted changes. Please commit or stash them first."
    git status --short
    exit 1
fi

# Get latest tag
LATEST_TAG=$(git tag -l | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)
if [[ -z "$LATEST_TAG" ]]; then
    LATEST_TAG="v0.0.0"
fi

# Parse current version
CURRENT_VERSION=${LATEST_TAG#v}
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Calculate new version
case $VERSION_TYPE in
    patch)
        PATCH=$((PATCH + 1))
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
esac

NEW_VERSION="v${MAJOR}.${MINOR}.${PATCH}"

echo "🚀 Starting release process..."
echo "Current version: $LATEST_TAG"
echo "New version: $NEW_VERSION"
echo "Feature branch: $CURRENT_BRANCH"
echo

# Switch to main and update
echo "📥 Updating main branch..."
git checkout main
git pull origin main

# Merge feature branch
echo "🔀 Merging feature branch..."
git merge --no-ff "$CURRENT_BRANCH" -m "Merge branch '$CURRENT_BRANCH' for $NEW_VERSION release"

# Update pyproject.toml files with new version
echo "📝 Updating pyproject.toml versions..."
PYPROJECT_FILES=$(find . -name "pyproject.toml" -path "*/servers/*" -o -name "pyproject.toml" -path "*/packages/*")
VERSION_ONLY=${NEW_VERSION#v}

for file in $PYPROJECT_FILES; do
    if grep -q '^version = ' "$file"; then
        echo "  Updating $file"
        sed -i '' "s/^version = .*/version = \"$VERSION_ONLY\"/" "$file"
        git add "$file"
    fi
done

# Commit version updates if any files were changed
if ! git diff --cached --quiet; then
    git commit -m "chore: Update version to $NEW_VERSION"
fi

# Get commit messages for release notes
echo "📋 Generating release notes..."
RELEASE_NOTES=$(git log $LATEST_TAG..HEAD --pretty=format:"- %s" --no-merges)

# Update CHANGELOG.md
echo "📝 Updating CHANGELOG.md..."
CURRENT_DATE=$(date "+%Y-%m-%d")
CHANGELOG_ENTRY="## [$VERSION_ONLY] - $CURRENT_DATE

### Changes
$RELEASE_NOTES

"

# Create new CHANGELOG content by inserting the new entry after the header
if [ -f "CHANGELOG.md" ]; then
    # Find the first occurrence of "## [" (first version entry)
    FIRST_VERSION_LINE=$(grep -n "^## \[" CHANGELOG.md | head -1 | cut -d: -f1)
    if [ -n "$FIRST_VERSION_LINE" ]; then
        # Insert new entry before the first version entry
        INSERT_LINE=$((FIRST_VERSION_LINE - 1))
        
        # Create temporary file with new content
        head -n $INSERT_LINE CHANGELOG.md > CHANGELOG.tmp
        echo "$CHANGELOG_ENTRY" >> CHANGELOG.tmp
        tail -n +$((INSERT_LINE + 1)) CHANGELOG.md >> CHANGELOG.tmp
        
        # Replace original file
        mv CHANGELOG.tmp CHANGELOG.md
        
        # Stage the changelog
        git add CHANGELOG.md
        git commit -m "docs: Update CHANGELOG.md for $NEW_VERSION"
        
        echo "  ✅ CHANGELOG.md updated with release $NEW_VERSION"
    else
        echo "  ⚠️  Could not find version entries in CHANGELOG.md, skipping update"
    fi
else
    echo "  ⚠️  CHANGELOG.md not found, skipping update"
fi

# Create annotated tag
echo "🏷️  Creating version tag..."
git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION

Changes:
$RELEASE_NOTES"

# Push everything
echo "⬆️  Pushing to GitHub..."
git push origin main
git push origin "$NEW_VERSION"

# Clean up feature branch
echo "🧹 Cleaning up feature branch..."
git branch -d "$CURRENT_BRANCH"
git push origin --delete "$CURRENT_BRANCH" 2>/dev/null || true

# Success message
echo
echo "✅ Release $NEW_VERSION completed successfully!"
echo
echo "📝 Release Notes:"
echo "$RELEASE_NOTES"
echo
echo "🔗 Create GitHub release: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:\/]\(.*\)\.git/\1/')/releases/new?tag=$NEW_VERSION"
echo
echo "Next steps:"
echo "1. Click the link above to create a GitHub release"
echo "2. Review and publish the release notes"
echo "3. Announce the release to your team"
```

## Error Handling

The command will fail gracefully if:
- You're on the main branch (must be on feature branch)
- There are uncommitted changes
- Version type is invalid
- Git operations fail (merge conflicts, push issues)

## Best Practices

1. **Always test thoroughly** before releasing
2. **Write clear commit messages** - they become release notes
3. **Use semantic versioning** correctly:
   - PATCH: Bug fixes, typos, small improvements
   - MINOR: New features, significant improvements
   - MAJOR: Breaking changes, major refactors
4. **Create GitHub release** after tagging for better visibility
5. **Document breaking changes** clearly in commit messages

## Requirements

- Git must be installed and configured
- GitHub remote must be properly set up
- Must have push permissions to main branch
- Must be on a feature branch (not main)
- pyproject.toml files must exist for version updates
- CHANGELOG.md should exist following Keep a Changelog format