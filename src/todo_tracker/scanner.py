"""
TODO Scanner Module

Scans codebases for TODO comments and extracts their details.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TodoItem:
    """
    Represents a TODO item found in the codebase.
    
    Attributes:
        file_path: Path to the file containing the TODO
        line_number: Line number where the TODO was found
        content: The TODO comment content
        todo_type: The type of TODO found (TODO, todo, ToDo)
    """
    file_path: str
    line_number: int
    content: str
    todo_type: str


class TodoScanner:
    """
    Scans a codebase for TODO comments.
    
    This class provides functionality to recursively scan directories for
    TODO comments while excluding specified directories and file patterns.
    """
    
    def __init__(self, ignore_dirs: Optional[List[str]] = None, ignore_patterns: Optional[List[str]] = None):
        """
        Initialize the TodoScanner.
        
        Args:
            ignore_dirs: List of directory names to ignore (default: ['.git', '__pycache__', 'node_modules'])
            ignore_patterns: List of file patterns to ignore (default: ['*.pyc', '*.log'])
        """
        self.ignore_dirs = ignore_dirs or ['.git', '__pycache__', 'node_modules', '.pytest_cache']
        self.ignore_patterns = ignore_patterns or ['*.pyc', '*.log', '*.tmp']
        
        # Regex pattern to match TODO comments
        # Matches: TODO, todo, ToDo (case variations) followed by optional colon and content
        self.todo_pattern = re.compile(
            r'(?P<todo_type>TODO|todo|ToDo)(?:\s*:?\s*)?(?P<content>.*)',
            re.IGNORECASE
        )
    
    def should_ignore_file(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        Args:
            file_path: Path object of the file to check
            
        Returns:
            True if the file should be ignored, False otherwise
        """
        # Check if file matches any ignore patterns
        for pattern in self.ignore_patterns:
            if file_path.match(pattern):
                return True
        return False
    
    def should_ignore_directory(self, dir_name: str) -> bool:
        """
        Check if a directory should be ignored.
        
        Args:
            dir_name: Name of the directory to check
            
        Returns:
            True if the directory should be ignored, False otherwise
        """
        return dir_name in self.ignore_dirs
    
    def scan_file(self, file_path: Path) -> List[TodoItem]:
        """
        Scan a single file for TODO comments.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of TodoItem objects found in the file
        """
        todos = []
        
        try:
            # Try to read the file with UTF-8 encoding, fallback to latin-1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                match = self.todo_pattern.search(line)
                if match:
                    todo_type = match.group('todo_type')
                    content = match.group('content').strip()
                    
                    # If no content after TODO, use the whole line trimmed
                    if not content:
                        content = line.strip()
                    
                    todo_item = TodoItem(
                        file_path=str(file_path),
                        line_number=line_num,
                        content=content,
                        todo_type=todo_type
                    )
                    todos.append(todo_item)
                    
        except (IOError, OSError, PermissionError) as e:
            # Skip files that can't be read
            print(f"Warning: Could not read file {file_path}: {e}")
            
        return todos
    
    def scan_directory(self, directory_path: str) -> List[TodoItem]:
        """
        Recursively scan a directory for TODO comments.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of all TodoItem objects found in the directory tree
        """
        all_todos = []
        root_path = Path(directory_path)
        
        if not root_path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        if not root_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        for root, dirs, files in os.walk(root_path):
            # Remove ignored directories from the list to prevent walking into them
            dirs[:] = [d for d in dirs if not self.should_ignore_directory(d)]
            
            for file_name in files:
                file_path = Path(root) / file_name
                
                # Skip ignored files
                if self.should_ignore_file(file_path):
                    continue
                
                # Scan the file for TODOs
                file_todos = self.scan_file(file_path)
                all_todos.extend(file_todos)
        
        return all_todos
    
    def get_summary(self, todos: List[TodoItem]) -> Dict[str, Any]:
        """
        Generate a summary of found TODOs.
        
        Args:
            todos: List of TodoItem objects
            
        Returns:
            Dictionary containing summary statistics
        """
        if not todos:
            return {
                'total_todos': 0,
                'files_with_todos': 0,
                'todo_types': {},
                'files': {}
            }
        
        files_with_todos = set()
        todo_types = {}
        files_summary = {}
        
        for todo in todos:
            files_with_todos.add(todo.file_path)
            
            # Count TODO types
            todo_types[todo.todo_type] = todo_types.get(todo.todo_type, 0) + 1
            
            # Count per file
            if todo.file_path not in files_summary:
                files_summary[todo.file_path] = 0
            files_summary[todo.file_path] += 1
        
        return {
            'total_todos': len(todos),
            'files_with_todos': len(files_with_todos),
            'todo_types': todo_types,
            'files': files_summary
        }
