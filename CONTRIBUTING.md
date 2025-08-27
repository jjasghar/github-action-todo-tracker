# Contributing to TODO Tracker

Thank you for your interest in contributing to TODO Tracker! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Docker (for testing the GitHub Action)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/github-action-todo-tracker.git
   cd github-action-todo-tracker
   ```

2. **Set up the development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -e ".[dev]"
   ```

3. **Run the tests**
   ```bash
   pytest
   ```

## 📝 Development Guidelines

### Code Style

We use `black` for code formatting:

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting a PR
- Aim for high test coverage (we currently have 44 tests)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/todo_tracker --cov-report=html

# Run specific test file
pytest tests/test_scanner.py -v
```

### Documentation

- Update the README if you add new features
- Add docstrings to new functions and classes
- Update the CHANGELOG.md for user-facing changes

## 🐛 Bug Reports

When filing a bug report, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Minimal steps to reproduce the bug
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Python version, OS, etc.
6. **Logs**: Any relevant error messages or logs

## ✨ Feature Requests

For feature requests, please:

1. Check if the feature already exists or is planned
2. Describe the use case and why it would be valuable
3. Provide examples of how it would work
4. Consider if it fits the project's scope and goals

## 🔧 Pull Requests

### Before Submitting

1. **Fork the repository** and create a feature branch
2. **Write tests** for your changes
3. **Ensure all tests pass** (`pytest`)
4. **Format your code** (`black src/ tests/`)
5. **Update documentation** if needed
6. **Update CHANGELOG.md** for user-facing changes

### PR Guidelines

1. **Clear title**: Summarize the change in the title
2. **Detailed description**: Explain what changed and why
3. **Link issues**: Reference any related issues
4. **Small scope**: Keep PRs focused on a single change
5. **Tests included**: Add or update tests as needed

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 📋 Project Structure

```
github-action-todo-tracker/
├── src/todo_tracker/          # Source code
│   ├── scanner.py            # TODO scanning logic
│   ├── github_client.py      # GitHub API integration
│   ├── cli.py               # Command-line interface
│   └── main.py              # Entry point
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── .github/workflows/       # CI/CD workflows
├── action.yml              # GitHub Action definition
├── Dockerfile              # Container for GitHub Action
└── entrypoint.sh           # GitHub Action entrypoint
```

## 🏷️ Release Process

Releases are automated via GitHub Actions when tags are pushed:

1. **Create a tag**: `git tag v1.1.0`
2. **Push the tag**: `git push origin v1.1.0`
3. **GitHub Actions**: Will automatically create a release and update major version tags

## 🤝 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold this code.

## 📞 Getting Help

- **Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Documentation**: Check the README and docs/ directory

## 🙏 Recognition

Contributors will be recognized in:
- The project's README
- Release notes for significant contributions
- GitHub's contributors page

Thank you for contributing to TODO Tracker! 🎉
