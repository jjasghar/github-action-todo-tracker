"""
Unit tests for the GitHubTodoClient class.
"""

import hashlib
from unittest.mock import Mock, patch, MagicMock
from typing import List

import pytest
from github import Github, Repository, Issue, Label
from github.GithubException import GithubException

from todo_tracker.github_client import GitHubTodoClient
from todo_tracker.scanner import TodoItem


class TestGitHubTodoClient:
    """Test cases for GitHubTodoClient functionality."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_github = Mock(spec=Github)
        self.mock_repo = Mock(spec=Repository)
        self.mock_github.get_repo.return_value = self.mock_repo
        
        # Add required methods to the mock repo
        self.mock_repo.get_label = Mock()
        self.mock_repo.create_label = Mock()
        self.mock_repo.get_issues = Mock()
        self.mock_repo.create_issue = Mock()
        self.mock_repo.html_url = 'https://github.com/owner/repo'
        self.mock_repo.default_branch = 'main'
        
        with patch('todo_tracker.github_client.Github', return_value=self.mock_github):
            self.client = GitHubTodoClient('fake_token', 'owner/repo')
    
    def test_initialization(self) -> None:
        """Test client initialization."""
        assert self.client.repo_name == 'owner/repo'
        assert self.client.todo_label == 'todo-tracker'
        assert self.client.repo == self.mock_repo
    
    @patch('todo_tracker.github_client.Github')
    def test_ensure_label_exists_creates_label(self, mock_github_class: Mock) -> None:
        """Test that label is created if it doesn't exist."""
        mock_github = Mock()
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github
        
        # Simulate label not found
        mock_repo.get_label.side_effect = GithubException(404, "Not Found", None)
        
        client = GitHubTodoClient('fake_token', 'owner/repo')
        
        # Verify label creation was attempted
        mock_repo.create_label.assert_called_once_with(
            name="todo-tracker",
            color="d4c5f9",
            description="Issues created automatically from TODO comments"
        )
    
    @patch('todo_tracker.github_client.Github')
    def test_ensure_label_exists_label_already_exists(self, mock_github_class: Mock) -> None:
        """Test that existing label is not recreated."""
        mock_github = Mock()
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github
        
        # Simulate label exists
        mock_label = Mock(spec=Label)
        mock_repo.get_label.return_value = mock_label
        
        client = GitHubTodoClient('fake_token', 'owner/repo')
        
        # Verify label creation was not attempted
        mock_repo.create_label.assert_not_called()
    
    def test_generate_todo_hash(self) -> None:
        """Test TODO hash generation."""
        todo = TodoItem('file.py', 42, 'Fix this', 'TODO')
        
        hash_value = self.client._generate_todo_hash(todo)
        
        expected_content = "file.py:42:Fix this"
        expected_hash = hashlib.sha256(expected_content.encode()).hexdigest()[:8]
        
        assert hash_value == expected_hash
        assert len(hash_value) == 8
    
    def test_create_issue_title(self) -> None:
        """Test issue title creation."""
        todo = TodoItem('src/utils/helper.py', 42, 'Fix this bug', 'TODO')
        
        title = self.client._create_issue_title(todo)
        
        assert title == 'TODO: Fix this bug (helper.py:42)'
    
    def test_create_issue_title_long_content(self) -> None:
        """Test issue title creation with long content."""
        long_content = 'This is a very long TODO comment that should be truncated'
        todo = TodoItem('file.py', 1, long_content, 'TODO')
        
        title = self.client._create_issue_title(todo)
        
        assert title == 'TODO: This is a very long TODO comment that should be tr... (file.py:1)'
        assert len(title.split('...')[0]) <= 56  # Actual truncation length
    
    def test_create_issue_body(self) -> None:
        """Test issue body creation."""
        todo = TodoItem('src/file.py', 42, 'Fix this bug', 'TODO')
        todo_hash = 'abcd1234'
        
        self.mock_repo.html_url = 'https://github.com/owner/repo'
        self.mock_repo.default_branch = 'main'
        
        body = self.client._create_issue_body(todo, todo_hash)
        
        assert '**File:** `src/file.py`' in body
        assert '**Line:** 42' in body
        assert '**Type:** `TODO`' in body
        assert 'Fix this bug' in body
        assert 'https://github.com/owner/repo/blob/main/src/file.py#L42' in body
        assert '*TODO Hash: `abcd1234`*' in body
    
    def test_create_issue_body_absolute_path(self) -> None:
        """Test issue body creation with absolute path gets converted to relative."""
        import tempfile
        import os
        
        # Create a temporary git repo structure
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = os.path.join(temp_dir, '.git')
            os.makedirs(git_dir)
            
            # Create a file path that would be absolute
            abs_file_path = os.path.join(temp_dir, 'src', 'main.py')
            todo = TodoItem(abs_file_path, 10, 'Test absolute path', 'TODO')
            todo_hash = 'xyz789'
            
            self.mock_repo.html_url = 'https://github.com/owner/repo'
            self.mock_repo.default_branch = 'main'
            
            body = self.client._create_issue_body(todo, todo_hash)
            
            # Should contain the original absolute path in the file display
            assert f'**File:** `{abs_file_path}`' in body
            # But the GitHub link should use the relative path
            assert 'https://github.com/owner/repo/blob/main/src/main.py#L10' in body
            assert '*TODO Hash: `xyz789`*' in body
    
    def test_get_existing_todo_issues(self) -> None:
        """Test fetching existing TODO issues."""
        # Mock issues
        issue1 = Mock(spec=Issue)
        issue1.body = "Some content\n*TODO Hash: `hash1234`*"
        
        issue2 = Mock(spec=Issue)
        issue2.body = "Another issue\n*TODO Hash: `hash5678`*"
        
        issue3 = Mock(spec=Issue)
        issue3.body = "No hash in this one"
        
        self.mock_repo.get_issues.return_value = [issue1, issue2, issue3]
        
        existing_issues = self.client._get_existing_todo_issues()
        
        assert len(existing_issues) == 2
        assert 'hash1234' in existing_issues
        assert 'hash5678' in existing_issues
        assert existing_issues['hash1234'] == issue1
        assert existing_issues['hash5678'] == issue2
    
    def test_get_existing_todo_issues_github_error(self) -> None:
        """Test handling GitHub API errors when fetching issues."""
        self.mock_repo.get_issues.side_effect = GithubException(500, "Server Error", None)
        
        existing_issues = self.client._get_existing_todo_issues()
        
        assert existing_issues == {}
    
    def test_create_issues_for_todos_new_issues(self) -> None:
        """Test creating issues for new TODOs."""
        todos = [
            TodoItem('file1.py', 1, 'Fix bug 1', 'TODO'),
            TodoItem('file2.py', 2, 'Fix bug 2', 'todo'),
        ]
        
        # Mock no existing issues
        self.mock_repo.get_issues.return_value = []
        
        # Mock issue creation
        mock_issue1 = Mock(spec=Issue)
        mock_issue1.number = 1
        mock_issue2 = Mock(spec=Issue)
        mock_issue2.number = 2
        
        self.mock_repo.create_issue.side_effect = [mock_issue1, mock_issue2]
        
        created_issues, skipped_hashes = self.client.create_issues_for_todos(todos)
        
        assert len(created_issues) == 2
        assert len(skipped_hashes) == 0
        assert self.mock_repo.create_issue.call_count == 2
    
    def test_create_issues_for_todos_dry_run(self) -> None:
        """Test dry run mode doesn't create actual issues."""
        todos = [TodoItem('file.py', 1, 'Fix bug', 'TODO')]
        
        self.mock_repo.get_issues.return_value = []
        
        created_issues, skipped_hashes = self.client.create_issues_for_todos(todos, dry_run=True)
        
        assert len(created_issues) == 0
        assert len(skipped_hashes) == 0
        assert self.mock_repo.create_issue.call_count == 0
    
    def test_create_issues_for_todos_skip_existing(self) -> None:
        """Test skipping TODOs that already have issues."""
        todo = TodoItem('file.py', 1, 'Fix bug', 'TODO')
        todo_hash = self.client._generate_todo_hash(todo)
        
        # Mock existing issue
        mock_existing_issue = Mock(spec=Issue)
        mock_existing_issue.body = f"Some content\n*TODO Hash: `{todo_hash}`*"
        self.mock_repo.get_issues.return_value = [mock_existing_issue]
        
        created_issues, skipped_hashes = self.client.create_issues_for_todos([todo])
        
        assert len(created_issues) == 0
        assert len(skipped_hashes) == 1
        assert skipped_hashes[0] == todo_hash
        assert self.mock_repo.create_issue.call_count == 0
    
    def test_create_issues_for_todos_github_error(self) -> None:
        """Test handling GitHub errors during issue creation."""
        todo = TodoItem('file.py', 1, 'Fix bug', 'TODO')
        
        self.mock_repo.get_issues.return_value = []
        self.mock_repo.create_issue.side_effect = GithubException(500, "Server Error", None)
        
        created_issues, skipped_hashes = self.client.create_issues_for_todos([todo])
        
        assert len(created_issues) == 0
        assert len(skipped_hashes) == 0
    
    def test_get_repository_info(self) -> None:
        """Test getting repository information."""
        self.mock_repo.name = 'repo'
        self.mock_repo.full_name = 'owner/repo'
        self.mock_repo.description = 'A test repository'
        self.mock_repo.html_url = 'https://github.com/owner/repo'
        self.mock_repo.default_branch = 'main'
        
        info = self.client.get_repository_info()
        
        expected = {
            'name': 'repo',
            'full_name': 'owner/repo',
            'description': 'A test repository',
            'url': 'https://github.com/owner/repo',
            'default_branch': 'main'
        }
        
        assert info == expected
    
    def test_get_repository_info_no_description(self) -> None:
        """Test getting repository info when description is None."""
        self.mock_repo.name = 'repo'
        self.mock_repo.full_name = 'owner/repo'
        self.mock_repo.description = None
        self.mock_repo.html_url = 'https://github.com/owner/repo'
        self.mock_repo.default_branch = 'main'
        
        info = self.client.get_repository_info()
        
        assert info['description'] == ''
    
    def test_close_resolved_todos(self) -> None:
        """Test closing issues for resolved TODOs."""
        current_todos = [
            TodoItem('file1.py', 1, 'Still exists', 'TODO')
        ]
        current_hash = self.client._generate_todo_hash(current_todos[0])
        
        # Mock existing issues - one still current, one resolved
        still_exists_issue = Mock(spec=Issue)
        still_exists_issue.state = 'open'
        still_exists_issue.body = f"Content\n*TODO Hash: `{current_hash}`*"
        
        resolved_issue = Mock(spec=Issue)
        resolved_issue.state = 'open'
        resolved_issue.number = 42
        resolved_issue.title = 'TODO: Resolved issue'
        resolved_issue.body = "Content\n*TODO Hash: `resolved123`*"
        resolved_issue.edit = Mock()
        resolved_issue.create_comment = Mock()
        
        self.mock_repo.get_issues.return_value = [still_exists_issue, resolved_issue]
        
        closed_issues = self.client.close_resolved_todos(current_todos)
        
        assert len(closed_issues) == 1
        assert closed_issues[0] == resolved_issue
        
        # Verify the resolved issue was closed
        resolved_issue.edit.assert_called_once_with(state='closed')
        resolved_issue.create_comment.assert_called_once()
    
    def test_close_resolved_todos_github_error(self) -> None:
        """Test handling errors when closing resolved TODOs."""
        current_todos = []
        
        # Mock an issue that should be closed
        issue = Mock(spec=Issue)
        issue.state = 'open'
        issue.number = 42
        issue.body = "Content\n*TODO Hash: `hash123`*"
        issue.edit = Mock(side_effect=GithubException(500, "Server Error", None))
        
        self.mock_repo.get_issues.return_value = [issue]
        
        closed_issues = self.client.close_resolved_todos(current_todos)
        
        assert len(closed_issues) == 0
