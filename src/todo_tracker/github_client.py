"""
GitHub Client Module

Handles GitHub API interactions for creating and managing TODO issues.
"""

import hashlib
from typing import List, Dict, Optional, Tuple
from github import Github, Repository, Issue
from github.GithubException import GithubException

from .scanner import TodoItem


class GitHubTodoClient:
    """
    GitHub client for managing TODO-related issues.
    
    This class handles creating, updating, and tracking GitHub issues
    that correspond to TODO comments found in the codebase.
    """
    
    def __init__(self, token: str, repo_name: str):
        """
        Initialize the GitHub client.
        
        Args:
            token: GitHub personal access token
            repo_name: Repository name in format 'owner/repo'
        """
        self.github = Github(token)
        self.repo_name = repo_name
        self.repo: Repository = self.github.get_repo(repo_name)
        self.todo_label = "todo-tracker"
        
        # Ensure the todo-tracker label exists
        self._ensure_label_exists()
    
    def _ensure_label_exists(self) -> None:
        """
        Ensure the todo-tracker label exists in the repository.
        Creates it if it doesn't exist.
        """
        try:
            self.repo.get_label(self.todo_label)
        except GithubException as e:
            if e.status == 404:
                # Label doesn't exist, create it
                self.repo.create_label(
                    name=self.todo_label,
                    color="d4c5f9",  # Light purple
                    description="Issues created automatically from TODO comments"
                )
            else:
                raise
    
    def _generate_todo_hash(self, todo_item: TodoItem) -> str:
        """
        Generate a unique hash for a TODO item.
        
        This hash is used to identify TODOs and prevent duplicates.
        Based on file path, line number, and content.
        
        Args:
            todo_item: TodoItem to generate hash for
            
        Returns:
            Hexadecimal hash string
        """
        content = f"{todo_item.file_path}:{todo_item.line_number}:{todo_item.content}"
        return hashlib.sha256(content.encode()).hexdigest()[:8]
    
    def _create_issue_title(self, todo_item: TodoItem) -> str:
        """
        Create a standardized issue title for a TODO item.
        
        Args:
            todo_item: TodoItem to create title for
            
        Returns:
            Formatted issue title
        """
        file_name = todo_item.file_path.split('/')[-1]
        return f"TODO: {todo_item.content[:50]}{'...' if len(todo_item.content) > 50 else ''} ({file_name}:{todo_item.line_number})"
    
    def _create_issue_body(self, todo_item: TodoItem, todo_hash: str) -> str:
        """
        Create the issue body content for a TODO item.
        
        Args:
            todo_item: TodoItem to create body for
            todo_hash: Unique hash for the TODO
            
        Returns:
            Formatted issue body in markdown
        """
        # Extract relative path for GitHub link
        # Convert absolute path to relative path from repository root
        import os
        file_path = todo_item.file_path
        
        # If it's an absolute path, try to make it relative
        if os.path.isabs(file_path):
            # Find the repository root by looking for .git directory
            current_dir = os.path.dirname(file_path)
            while current_dir != os.path.dirname(current_dir):  # Not at filesystem root
                if os.path.exists(os.path.join(current_dir, '.git')):
                    # Found repository root, make path relative
                    file_path = os.path.relpath(file_path, current_dir)
                    break
                current_dir = os.path.dirname(current_dir)
        
        return f"""## TODO Found in Code

**File:** `{todo_item.file_path}`  
**Line:** {todo_item.line_number}  
**Type:** `{todo_item.todo_type}`  

### Content
```
{todo_item.content}
```

### Location
[View in repository]({self.repo.html_url}/blob/{self.repo.default_branch}/{file_path}#L{todo_item.line_number})

---
*This issue was automatically created by the TODO Tracker.*  
*TODO Hash: `{todo_hash}`*
"""
    
    def _get_existing_todo_issues(self) -> Dict[str, Issue]:
        """
        Get all existing TODO tracker issues from the repository.
        
        Returns:
            Dictionary mapping TODO hashes to Issue objects
        """
        existing_issues = {}
        
        try:
            issues = self.repo.get_issues(
                labels=[self.todo_label],
                state="all"  # Include both open and closed issues
            )
            
            for issue in issues:
                # Extract TODO hash from issue body
                if "TODO Hash:" in issue.body:
                    hash_line = [line for line in issue.body.split('\n') if 'TODO Hash:' in line]
                    if hash_line:
                        todo_hash = hash_line[0].split('`')[1]  # Extract hash from markdown code
                        existing_issues[todo_hash] = issue
                        
        except GithubException as e:
            print(f"Warning: Could not fetch existing issues: {e}")
            
        return existing_issues
    
    def create_issues_for_todos(self, todos: List[TodoItem], dry_run: bool = False) -> Tuple[List[Issue], List[str]]:
        """
        Create GitHub issues for TODO items.
        
        Args:
            todos: List of TodoItem objects to create issues for
            dry_run: If True, don't actually create issues, just return what would be created
            
        Returns:
            Tuple of (created_issues, skipped_hashes) where:
            - created_issues: List of Issue objects that were created
            - skipped_hashes: List of TODO hashes that were skipped (already exist)
        """
        created_issues = []
        skipped_hashes = []
        
        # Get existing issues to avoid duplicates
        existing_issues = self._get_existing_todo_issues()
        
        for todo in todos:
            todo_hash = self._generate_todo_hash(todo)
            
            # Check if issue already exists
            if todo_hash in existing_issues:
                skipped_hashes.append(todo_hash)
                continue
            
            # Create issue title and body
            title = self._create_issue_title(todo)
            body = self._create_issue_body(todo, todo_hash)
            
            if dry_run:
                print(f"[DRY RUN] Would create issue: {title}")
                continue
            
            try:
                # Create the issue
                issue = self.repo.create_issue(
                    title=title,
                    body=body,
                    labels=[self.todo_label]
                )
                created_issues.append(issue)
                print(f"Created issue #{issue.number}: {title}")
                
            except GithubException as e:
                print(f"Error creating issue for TODO {todo_hash}: {e}")
        
        return created_issues, skipped_hashes
    
    def get_repository_info(self) -> Dict[str, str]:
        """
        Get basic repository information.
        
        Returns:
            Dictionary with repository details
        """
        return {
            'name': self.repo.name,
            'full_name': self.repo.full_name,
            'description': self.repo.description or '',
            'url': self.repo.html_url,
            'default_branch': self.repo.default_branch
        }
    
    def close_resolved_todos(self, current_todos: List[TodoItem]) -> List[Issue]:
        """
        Close issues for TODOs that no longer exist in the codebase.
        
        Args:
            current_todos: List of currently found TodoItem objects
            
        Returns:
            List of Issue objects that were closed
        """
        current_hashes = {self._generate_todo_hash(todo) for todo in current_todos}
        existing_issues = self._get_existing_todo_issues()
        closed_issues = []
        
        for todo_hash, issue in existing_issues.items():
            # If issue is open but TODO no longer exists, close it
            if issue.state == 'open' and todo_hash not in current_hashes:
                try:
                    issue.edit(state='closed')
                    issue.create_comment("This TODO has been resolved or removed from the codebase.")
                    closed_issues.append(issue)
                    print(f"Closed resolved issue #{issue.number}: {issue.title}")
                except GithubException as e:
                    print(f"Error closing issue #{issue.number}: {e}")
        
        return closed_issues
