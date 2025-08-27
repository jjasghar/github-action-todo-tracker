# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-01-XX

### Added
- Initial release of TODO Tracker GitHub Action
- Automatic scanning for TODO, todo, and ToDo comments in codebase
- GitHub issue creation with direct links to source code locations
- Duplicate prevention using content-based hashing
- Support for custom ignore directories and file patterns
- Dry-run mode for testing without creating issues
- Option to close resolved TODO issues automatically
- Comprehensive CLI interface for standalone usage
- Docker containerization for GitHub Actions
- Full test suite with 44 unit tests
- Support for Python 3.9, 3.10, and 3.11

### Features
- 🔍 Smart scanning with configurable ignore patterns
- 📝 Standardized GitHub issue format with metadata
- 🔒 Content-based deduplication prevents spam
- 🧹 Automatic cleanup of resolved TODOs
- 🛠️ Dual mode: GitHub Action + standalone CLI
- ⚙️ Highly configurable via inputs and environment variables
- 🎯 Production-ready with real-world usage examples

### Example Usage
```yaml
- uses: jjasghar/github-action-todo-tracker@v1
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    close-resolved: true
    ignore-dirs: 'node_modules,build'
    ignore-patterns: '*.min.js,*.map'
```

### CLI Usage
```bash
pip install github-action-todo-tracker
export GITHUB_TOKEN="your_token"
todo-tracker track --repo-name owner/repo --repo-path /path/to/repo
```

## [0.1.0] - 2025-01-XX

### Added
- Initial development version
- Basic TODO scanning functionality
- GitHub API integration via PyGithub
- Command-line interface prototype
