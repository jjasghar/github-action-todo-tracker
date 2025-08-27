# GitHub Action TODO Tracker

**Never lose track of your TODOs again!** 

This powerful automation tool scans your codebase for TODO comments and automatically creates GitHub issues to track them. It's designed to help development teams maintain visibility of technical debt, pending features, and code improvements by converting scattered TODO comments into organized, trackable GitHub issues.

🎯 **Perfect for**: Open source projects, team development, technical debt management, and ensuring nothing falls through the cracks.

[![Tests](https://github.com/jjasghar/github-action-todo-tracker/actions/workflows/test.yml/badge.svg)](https://github.com/jjasghar/github-action-todo-tracker/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Live Example

**See it in action!** This tool is already helping real projects track their TODOs:

📋 **[Live Example: AI IRC Slack Discord Bot](https://github.com/jjasghar/ai-irc-slack-discord-ollama-bot/issues/2)**

This issue was automatically created by the TODO Tracker when it found a TODO comment in the `main.py` file. Notice how it:
- Creates a clear, descriptive title with file and line number
- Links directly to the exact line of code in the repository
- Includes the full TODO content and context
- Uses the `todo-tracker` label for easy filtering

## ✨ Key Features

- 🔍 **Smart Scanning**: Automatically finds TODO, todo, and ToDo comments in your codebase
- 🚫 **Intelligent Filtering**: Skips irrelevant directories (`.git`, `__pycache__`, etc.) and file types
- 📝 **Issue Creation**: Creates standardized GitHub issues with links back to the source code
- 🔒 **Duplicate Prevention**: Uses content-based hashing to prevent duplicate issues
- 🧹 **Cleanup**: Optionally closes issues for TODOs that have been resolved
- 🛠️ **Dual Mode**: Works as both a standalone CLI tool and GitHub Action
- ⚙️ **Customizable**: Configure ignored directories, file patterns, and more
- 🎯 **Production Ready**: Used by real open source projects in production

## 🚀 Quick Start

Ready to never lose a TODO again? Get started in minutes!

### 🔧 As a CLI Tool (Easiest)

```bash
# 1. Clone this repository
git clone https://github.com/jjasghar/github-action-todo-tracker.git
cd github-action-todo-tracker

# 2. Set up the environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
pip install -e .

# 3. Set your GitHub token
export GITHUB_TOKEN="your_github_personal_access_token"

# 4. Run on any repository (try the example!)
todo-tracker track \
  --repo-name jjasghar/ai-irc-slack-discord-ollama-bot \
  --repo-path /path/to/local/clone \
  --verbose

# Or just scan without creating issues
todo-tracker scan --repo-path /path/to/repo
```

### ⚡ As a GitHub Action

Add this workflow to your repository at `.github/workflows/todo-tracker.yml`:

```yaml
name: TODO Tracker

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  track-todos:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: jjasghar/github-action-todo-tracker@v1
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        close-resolved: true
```

💡 **Want to see it in action first?** Check out the [live example issue](https://github.com/jjasghar/ai-irc-slack-discord-ollama-bot/issues/2) created by this tool!

## Usage

### GitHub Action Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github-token` | GitHub token for API access | Yes | - |
| `repo-path` | Path to scan for TODOs | No | `.` |
| `close-resolved` | Close issues for resolved TODOs | No | `false` |
| `ignore-dirs` | Comma-separated directories to ignore | No | - |
| `ignore-patterns` | Comma-separated file patterns to ignore | No | - |
| `dry-run` | Preview changes without creating issues | No | `false` |

### GitHub Action Outputs

| Output | Description |
|--------|-------------|
| `todos-found` | Number of TODOs found |
| `issues-created` | Number of new issues created |
| `issues-skipped` | Number of existing TODOs skipped |
| `issues-closed` | Number of resolved issues closed |

### CLI Commands

#### Track TODOs (`todo-tracker track`)

Scan repository and create GitHub issues:

```bash
todo-tracker track \
  --github-token $GITHUB_TOKEN \
  --repo-name owner/repo \
  --repo-path /path/to/repo \
  --close-resolved \
  --ignore-dirs build dist \
  --ignore-patterns "*.pyc" "*.log" \
  --verbose
```

#### Scan Only (`todo-tracker scan`)

Scan repository without creating issues (useful for testing):

```bash
todo-tracker scan --repo-path /path/to/repo
```

### Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token
- `GITHUB_REPOSITORY`: Repository name in format `owner/repo`

## TODO Comment Formats

The tool recognizes these TODO formats:

```python
# TODO: Fix this bug
# todo: implement feature
# ToDo: Add error handling

// TODO: Refactor this function
/* TODO: Update documentation */

-- TODO: Optimize query
<!-- TODO: Update styling -->
```

## Example Output

### CLI Output

```
Starting TODO scan of: /path/to/repo
Repository: owner/repo

Scan Summary:
  Total TODOs found: 5
  Files with TODOs: 3
  TODO types: {'TODO': 3, 'todo': 1, 'ToDo': 1}

Connecting to GitHub repository: owner/repo
Connected to: owner/repo
Default branch: main

Creating GitHub issues...
Created issue #123: TODO: Fix authentication bug (auth.py:45)
Created issue #124: TODO: Add input validation (utils.py:12)
Skipped 2 existing TODOs

Created 2 new issues
Skipped 2 existing TODOs

TODO tracking completed successfully!
```

### Generated Issues

Each TODO creates a standardized GitHub issue. Here's the format using our [real example](https://github.com/jjasghar/ai-irc-slack-discord-ollama-bot/issues/2):

**Title**: `TODO: Let see if the todo github action finds me. (main.py:32)`

**Body**:
```markdown
## TODO Found in Code

**File:** `/tmp/ai-irc-slack-discord-ollama-bot/main.py`
**Line:** 32
**Type:** `TODO`

### Content
```
Let see if the todo github action finds me.
```

### Location
[View in repository](https://github.com/jjasghar/ai-irc-slack-discord-ollama-bot/blob/main/main.py#L32)

---
*This issue was automatically created by the TODO Tracker.*
*TODO Hash: `fd053141`*
```

🔗 **See the actual generated issue**: https://github.com/jjasghar/ai-irc-slack-discord-ollama-bot/issues/2

## 🚀 Why Use TODO Tracker?

**Before**: TODOs scattered throughout your codebase, easy to forget, no visibility
```python
# TODO: Fix this authentication bug
# TODO: Add input validation
# TODO: Optimize this query
```

**After**: Organized GitHub issues with full context and traceability
- ✅ All TODOs tracked in your project's issue system
- ✅ Direct links to source code locations
- ✅ Automatic duplicate prevention
- ✅ Integration with your existing workflow
- ✅ Team visibility and assignment capabilities

**Perfect for**:
- 🏢 **Development Teams**: Keep track of technical debt across team members
- 🌍 **Open Source Projects**: Let contributors easily find areas that need work
- 📈 **Project Management**: Convert code comments into actionable items
- 🔄 **CI/CD Integration**: Automatically track TODOs on every push

## Configuration

### Default Ignored Directories

- `.git`
- `__pycache__`
- `node_modules`
- `.pytest_cache`

### Default Ignored File Patterns

- `*.pyc`
- `*.log`
- `*.tmp`

### Customizing Ignores

```yaml
# GitHub Action
- uses: jjasghar/github-action-todo-tracker@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    ignore-dirs: "build,dist,coverage"
    ignore-patterns: "*.min.js,*.map"
```

```bash
# CLI
todo-tracker track \
  --ignore-dirs build dist coverage \
  --ignore-patterns "*.min.js" "*.map"
```

## Development

### Setup

```bash
git clone https://github.com/jjasghar/github-action-todo-tracker.git
cd github-action-todo-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development/testing
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/todo_tracker --cov-report=html

# Run specific test file
pytest tests/test_scanner.py -v
```

### Code Style

```bash
# Format code
black src/ tests/

# Check style
black --check src/ tests/
```

### Project Structure

```
github-action-todo-tracker/
├── src/todo_tracker/          # Source code
│   ├── __init__.py
│   ├── scanner.py            # TODO scanning logic
│   ├── github_client.py      # GitHub API integration
│   ├── cli.py               # Command-line interface
│   └── main.py              # Entry point
├── tests/                   # Unit tests
│   ├── test_scanner.py
│   ├── test_github_client.py
│   └── test_cli.py
├── docs/                    # Documentation
├── .github/workflows/       # GitHub Actions workflows
├── action.yml              # GitHub Action definition
├── Dockerfile              # Container for GitHub Action
├── entrypoint.sh           # GitHub Action entrypoint
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`pytest`)
6. Format code (`black src/ tests/`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

- Always use GitHub tokens with minimal required permissions
- The tool only needs repository read access and issues write access
- Never commit tokens to your repository
- Use GitHub's built-in `GITHUB_TOKEN` in workflows when possible

## Troubleshooting

### Common Issues

**Issue**: "Repository not found" error
**Solution**: Ensure your GitHub token has access to the repository and the repository name is correct.

**Issue**: No TODOs found in known files with TODOs
**Solution**: Check if the files are being ignored by default patterns or custom ignore settings.

**Issue**: Permission denied when creating issues
**Solution**: Verify your GitHub token has "Issues" write permission.

**Issue**: Encoding errors when scanning files
**Solution**: The tool handles most encoding issues automatically, but you may need to add specific file patterns to ignore list.

### Debug Mode

Run with verbose output to debug issues:

```bash
todo-tracker track --verbose
```

### Dry Run

Test the tool without creating actual issues:

```bash
todo-tracker track --dry-run
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Support

- 📖 [Documentation](https://github.com/jjasghar/github-action-todo-tracker/docs)
- 🐛 [Issue Tracker](https://github.com/jjasghar/github-action-todo-tracker/issues)
- 💬 [Discussions](https://github.com/jjasghar/github-action-todo-tracker/discussions)
