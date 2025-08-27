"""
Unit tests for the CLI module.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from click.testing import CliRunner

from todo_tracker.cli import main, scan_only
from todo_tracker.scanner import TodoItem


class TestCLI:
    """Test cases for CLI functionality."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('todo_tracker.cli.TodoScanner')
    @patch('todo_tracker.cli.GitHubTodoClient')
    def test_main_command_success(self, mock_github_client: Mock, mock_scanner: Mock) -> None:
        """Test successful execution of main command."""
        # Mock scanner
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        
        mock_todos = [
            TodoItem('file.py', 1, 'Fix this', 'TODO'),
            TodoItem('file.py', 5, 'Add feature', 'todo')
        ]
        mock_scanner_instance.scan_directory.return_value = mock_todos
        mock_scanner_instance.get_summary.return_value = {
            'total_todos': 2,
            'files_with_todos': 1,
            'todo_types': {'TODO': 1, 'todo': 1},
            'files': {'file.py': 2}
        }
        
        # Mock GitHub client
        mock_client_instance = Mock()
        mock_github_client.return_value = mock_client_instance
        mock_client_instance.get_repository_info.return_value = {
            'full_name': 'owner/repo',
            'default_branch': 'main'
        }
        mock_client_instance.create_issues_for_todos.return_value = ([], [])
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(main, [
                '--repo-path', temp_dir,
                '--github-token', 'fake_token',
                '--repo-name', 'owner/repo'
            ])
        
        assert result.exit_code == 0
        assert 'Total TODOs found: 2' in result.output
        assert 'TODO tracking completed successfully!' in result.output
    
    @patch('todo_tracker.cli.TodoScanner')
    def test_main_command_no_todos(self, mock_scanner: Mock) -> None:
        """Test main command when no TODOs are found."""
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.scan_directory.return_value = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(main, [
                '--repo-path', temp_dir,
                '--github-token', 'fake_token',
                '--repo-name', 'owner/repo'
            ])
        
        assert result.exit_code == 0
        assert 'No TODOs found in the repository.' in result.output
    
    @patch('todo_tracker.cli.TodoScanner')
    @patch('todo_tracker.cli.GitHubTodoClient')
    def test_main_command_dry_run(self, mock_github_client: Mock, mock_scanner: Mock) -> None:
        """Test main command in dry run mode."""
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.scan_directory.return_value = [
            TodoItem('file.py', 1, 'Fix this', 'TODO')
        ]
        mock_scanner_instance.get_summary.return_value = {
            'total_todos': 1,
            'files_with_todos': 1,
            'todo_types': {'TODO': 1},
            'files': {'file.py': 1}
        }
        
        mock_client_instance = Mock()
        mock_github_client.return_value = mock_client_instance
        mock_client_instance.get_repository_info.return_value = {
            'full_name': 'owner/repo',
            'default_branch': 'main'
        }
        mock_client_instance.create_issues_for_todos.return_value = ([], [])
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(main, [
                '--repo-path', temp_dir,
                '--github-token', 'fake_token',
                '--repo-name', 'owner/repo',
                '--dry-run'
            ])
        
        assert result.exit_code == 0
        assert '[DRY RUN]' in result.output
    
    def test_main_command_missing_token(self) -> None:
        """Test main command with missing GitHub token."""
        result = self.runner.invoke(main, [
            '--repo-name', 'owner/repo'
        ])
        
        assert result.exit_code == 2  # Click error exit code
        assert 'github-token' in result.output.lower()
    
    def test_main_command_missing_repo_name(self) -> None:
        """Test main command with missing repository name."""
        result = self.runner.invoke(main, [
            '--github-token', 'fake_token'
        ])
        
        assert result.exit_code == 2  # Click error exit code
        assert 'repo-name' in result.output.lower()
    
    @patch('todo_tracker.cli.TodoScanner')
    @patch('todo_tracker.cli.GitHubTodoClient')
    def test_main_command_with_custom_ignores(self, mock_github_client: Mock, mock_scanner: Mock) -> None:
        """Test main command with custom ignore settings."""
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.scan_directory.return_value = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(main, [
                '--repo-path', temp_dir,
                '--github-token', 'fake_token',
                '--repo-name', 'owner/repo',
                '--ignore-dirs', 'custom1',
                '--ignore-dirs', 'custom2',
                '--ignore-patterns', '*.custom'
            ])
        
        # Verify scanner was called with custom ignores
        mock_scanner.assert_called_once_with(
            ignore_dirs=['custom1', 'custom2'],
            ignore_patterns=['*.custom']
        )
        
        assert result.exit_code == 0
    
    @patch('todo_tracker.cli.TodoScanner')
    @patch('todo_tracker.cli.GitHubTodoClient')
    def test_main_command_close_resolved(self, mock_github_client: Mock, mock_scanner: Mock) -> None:
        """Test main command with close-resolved option."""
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.scan_directory.return_value = [
            TodoItem('file.py', 1, 'Fix this', 'TODO')
        ]
        mock_scanner_instance.get_summary.return_value = {
            'total_todos': 1,
            'files_with_todos': 1,
            'todo_types': {'TODO': 1},
            'files': {'file.py': 1}
        }
        
        mock_client_instance = Mock()
        mock_github_client.return_value = mock_client_instance
        mock_client_instance.get_repository_info.return_value = {
            'full_name': 'owner/repo',
            'default_branch': 'main'
        }
        mock_client_instance.create_issues_for_todos.return_value = ([], [])
        mock_client_instance.close_resolved_todos.return_value = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(main, [
                '--repo-path', temp_dir,
                '--github-token', 'fake_token',
                '--repo-name', 'owner/repo',
                '--close-resolved'
            ])
        
        assert result.exit_code == 0
        mock_client_instance.close_resolved_todos.assert_called_once()
    
    @patch('todo_tracker.cli.TodoScanner')
    def test_main_command_scanner_error(self, mock_scanner: Mock) -> None:
        """Test main command when scanner raises an error."""
        mock_scanner.side_effect = Exception("Scanner error")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(main, [
                '--repo-path', temp_dir,
                '--github-token', 'fake_token',
                '--repo-name', 'owner/repo'
            ])
        
        assert result.exit_code == 1
        assert 'Error:' in result.output
    
    @patch('todo_tracker.cli.TodoScanner')
    def test_scan_only_command(self, mock_scanner: Mock) -> None:
        """Test scan-only command."""
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        
        mock_todos = [
            TodoItem('file.py', 1, 'Fix this', 'TODO'),
            TodoItem('file.py', 5, 'Add feature', 'todo')
        ]
        mock_scanner_instance.scan_directory.return_value = mock_todos
        mock_scanner_instance.get_summary.return_value = {
            'total_todos': 2,
            'files_with_todos': 1,
            'todo_types': {'TODO': 1, 'todo': 1},
            'files': {'file.py': 2}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(scan_only, [
                '--repo-path', temp_dir
            ])
        
        assert result.exit_code == 0
        assert 'Total TODOs: 2' in result.output
        assert 'file.py:1 [TODO] Fix this' in result.output
        assert 'file.py:5 [todo] Add feature' in result.output
    
    @patch('todo_tracker.cli.TodoScanner')
    def test_scan_only_command_no_todos(self, mock_scanner: Mock) -> None:
        """Test scan-only command when no TODOs are found."""
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.scan_directory.return_value = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(scan_only, [
                '--repo-path', temp_dir
            ])
        
        assert result.exit_code == 0
        assert 'No TODOs found in the repository.' in result.output
    
    @patch('todo_tracker.cli.TodoScanner')
    def test_scan_only_command_error(self, mock_scanner: Mock) -> None:
        """Test scan-only command when an error occurs."""
        mock_scanner.side_effect = Exception("Scanner error")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(scan_only, [
                '--repo-path', temp_dir
            ])
        
        assert result.exit_code == 1
        assert 'Error:' in result.output
