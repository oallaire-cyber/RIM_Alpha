# Contributing to Risk Influence Map

Thank you for your interest in contributing to the Risk Influence Map project! This document provides guidelines for contributing to this POC.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Setup](#development-setup)
5. [Coding Standards](#coding-standards)
6. [Submitting Changes](#submitting-changes)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the project
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## Getting Started

### Types of Contributions

We welcome:

- **Bug Reports**: Found a problem? Let us know!
- **Feature Requests**: Have an idea? Share it!
- **Code Contributions**: Ready to code? Great!
- **Documentation**: Help improve docs
- **Testing**: Add or improve tests
- **Design**: UI/UX improvements

### Before You Start

1. Check existing issues to avoid duplicates
2. For major changes, open an issue first to discuss
3. For minor fixes, feel free to submit a PR directly

## How to Contribute

### Reporting Bugs

**Before submitting:**
- Search existing issues
- Verify the bug in the latest version
- Check if it's already fixed in `main` branch

**When reporting, include:**
- Clear, descriptive title
- Steps to reproduce
- Expected vs. actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, Docker version)

**Template:**
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11]
- Python: [e.g., 3.11.0]
- Docker: [e.g., 24.0.0]
- Browser: [e.g., Chrome 120]

## Additional Context
Screenshots, logs, etc.
```

### Suggesting Features

**Before suggesting:**
- Check if already proposed
- Consider if it fits the project scope
- Think about implementation approach

**When suggesting, include:**
- Clear use case
- Proposed solution
- Alternative approaches considered
- Mockups/diagrams if helpful

**Template:**
```markdown
## Feature Description
What feature would you like to see?

## Use Case
Why is this useful?

## Proposed Solution
How should it work?

## Alternatives
Other approaches considered

## Additional Context
Any other relevant information
```

### Improving Documentation

Documentation improvements are always welcome:

- Fix typos or grammatical errors
- Clarify confusing sections
- Add examples
- Update outdated information
- Translate to other languages

Simply submit a PR with your changes!

## Development Setup

### Fork and Clone

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/RIM_Alpha.git
cd RIM_Alpha

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/RIM_Alpha.git
```

### Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if needed)
pip install black flake8 pytest

# Start Neo4j
docker-compose up -d

# Run the application
streamlit run app.py
```

### Development Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Test your changes
streamlit run app.py

# Commit changes
git add .
git commit -m "Add feature: your feature description"

# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Organized and grouped

### Code Formatting

Use `black` for automatic formatting:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Code Quality

Use `flake8` for linting:

```bash
# Check code quality
flake8 app.py --max-line-length=88
```

### Naming Conventions

- **Functions**: `snake_case` (e.g., `get_all_risks`)
- **Classes**: `PascalCase` (e.g., `Neo4jConnection`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `NEO4J_URI`)
- **Private**: Prefix with `_` (e.g., `_internal_method`)

### Documentation

- Add docstrings to all functions and classes
- Use clear, descriptive variable names
- Comment complex logic
- Update relevant documentation files

**Docstring Example:**
```python
def create_risk(conn: Neo4jConnection, name: str, category: str,
                probability: int, impact: int, status: str,
                description: str) -> bool:
    """
    Create a new risk in the database.
    
    Args:
        conn: Neo4j database connection
        name: Unique risk identifier
        category: Risk category (Cyber, Operational, etc.)
        probability: Likelihood score (1-10)
        impact: Severity score (1-10)
        status: Current risk status
        description: Detailed risk description
    
    Returns:
        bool: True if creation successful, False otherwise
    
    Example:
        >>> create_risk(conn, "Data Breach", "Cyber", 7, 9, "Active",
        ...             "Risk of unauthorized data access")
        True
    """
    # Implementation...
```

### Testing

While formal tests are not yet implemented, manually verify:

- New features work as intended
- Existing features still work
- No console errors or warnings
- Works on different browsers/OS

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure README, guides reflect changes
2. **Test Thoroughly**: Verify all functionality works
3. **Clean Commits**: Use clear, descriptive commit messages
4. **Small PRs**: Keep changes focused and manageable

### Commit Message Guidelines

Follow conventional commits:

```
type(scope): brief description

Detailed explanation if needed

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(risks): add bulk import from CSV

fix(visualization): correct node color calculation

docs(setup): add troubleshooting section

refactor(database): optimize query performance
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Works as expected

## Screenshots
If applicable, add screenshots

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. Maintainer reviews your PR
2. Feedback provided via comments
3. Make requested changes
4. Push updates to your branch
5. Maintainer approves and merges

## Development Priorities

Current priorities for contributions:

### High Priority

- [ ] CSV import/export functionality
- [ ] Unit and integration tests
- [ ] Performance optimization for large graphs
- [ ] User authentication system

### Medium Priority

- [ ] Advanced analytics features
- [ ] Risk scenario modeling
- [ ] Export to PDF reports
- [ ] Layout persistence for graphs

### Low Priority

- [ ] API development
- [ ] Mobile responsive improvements
- [ ] Internationalization (i18n)
- [ ] Dark mode theme

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed PRs for examples

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in the repository

Thank you for contributing to Risk Influence Map!

---

**Note**: These guidelines may evolve as the project grows. Check back periodically for updates.
