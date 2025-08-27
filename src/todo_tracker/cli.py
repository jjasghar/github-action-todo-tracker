"""
Command Line Interface for TODO Tracker

Provides a CLI for scanning repositories and creating GitHub issues for TODOs.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click

from .scanner import TodoScanner
from .github_client import GitHubTodoClient


@click.command()
@click.option(
    '--repo-path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default='.',
    help='Path to the repository to scan (default: current directory)'
)
@click.option(
    '--github-token',
    envvar='GITHUB_TOKEN',
    required=True,
    help='GitHub personal access token (can be set via GITHUB_TOKEN env var)'
)
@click.option(
    '--repo-name',
    envvar='GITHUB_REPOSITORY',
    required=True,
    help='GitHub repository name in format owner/repo (can be set via GITHUB_REPOSITORY env var)'
)
@click.option(
    '--dry-run',
    is_flag=True,
    default=False,
    help='Perform a dry run without creating actual issues'
)
@click.option(
    '--close-resolved',
    is_flag=True,
    default=False,
    help='Close issues for TODOs that no longer exist in the codebase'
)
@click.option(
    '--ignore-dirs',
    multiple=True,
    default=None,
    help='Additional directories to ignore (can be specified multiple times)'
)
@click.option(
    '--ignore-patterns',
    multiple=True,
    default=None,
    help='Additional file patterns to ignore (can be specified multiple times)'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    default=False,
    help='Enable verbose output'
)
def main(
    repo_path: str,
    github_token: str,
    repo_name: str,
    dry_run: bool,
    close_resolved: bool,
    ignore_dirs: tuple,
    ignore_patterns: tuple,
    verbose: bool
) -> None:
    """
    Scan a repository for TODO comments and create GitHub issues for them.
    
    This tool recursively scans the specified repository path for TODO comments
    (TODO, todo, ToDo) and creates corresponding GitHub issues. It prevents
    duplicate issue creation by tracking TODOs with unique hashes.
    
    Examples:
        # Scan current directory and create issues
        todo-tracker --github-token $TOKEN --repo-name owner/repo
        
        # Dry run to see what would be created
        todo-tracker --github-token $TOKEN --repo-name owner/repo --dry-run
        
        # Scan specific directory with custom ignores
        todo-tracker --repo-path /path/to/repo --github-token $TOKEN --repo-name owner/repo --ignore-dirs build dist
    """
    if verbose:
        click.echo(f"Starting TODO scan of: {repo_path}")
        click.echo(f"Repository: {repo_name}")
        click.echo(f"Dry run: {dry_run}")
    
    try:
        # Initialize scanner with custom ignore settings if provided
        scanner_kwargs = {}
        if ignore_dirs:
            scanner_kwargs['ignore_dirs'] = list(ignore_dirs)
        if ignore_patterns:
            scanner_kwargs['ignore_patterns'] = list(ignore_patterns)
        
        scanner = TodoScanner(**scanner_kwargs)
        
        # Scan for TODOs
        if verbose:
            click.echo("Scanning for TODOs...")
        
        todos = scanner.scan_directory(repo_path)
        
        if not todos:
            click.echo("No TODOs found in the repository.")
            return
        
        # Print summary
        summary = scanner.get_summary(todos)
        click.echo(f"\nScan Summary:")
        click.echo(f"  Total TODOs found: {summary['total_todos']}")
        click.echo(f"  Files with TODOs: {summary['files_with_todos']}")
        click.echo(f"  TODO types: {summary['todo_types']}")
        
        if verbose:
            click.echo(f"\nTODOs by file:")
            for file_path, count in summary['files'].items():
                click.echo(f"  {file_path}: {count}")
        
        # Initialize GitHub client
        if verbose:
            click.echo(f"\nConnecting to GitHub repository: {repo_name}")
        
        github_client = GitHubTodoClient(github_token, repo_name)
        
        # Get repository info
        repo_info = github_client.get_repository_info()
        if verbose:
            click.echo(f"Connected to: {repo_info['full_name']}")
            click.echo(f"Default branch: {repo_info['default_branch']}")
        
        # Create issues for TODOs
        if verbose:
            click.echo("\nCreating GitHub issues...")
        
        created_issues, skipped_hashes = github_client.create_issues_for_todos(todos, dry_run)
        
        if dry_run:
            click.echo(f"\n[DRY RUN] Would create {len(todos) - len(skipped_hashes)} new issues")
            click.echo(f"[DRY RUN] Would skip {len(skipped_hashes)} existing TODOs")
        else:
            click.echo(f"\nCreated {len(created_issues)} new issues")
            click.echo(f"Skipped {len(skipped_hashes)} existing TODOs")
            
            # List created issues
            if created_issues and verbose:
                click.echo("\nCreated issues:")
                for issue in created_issues:
                    click.echo(f"  #{issue.number}: {issue.title}")
                    click.echo(f"    URL: {issue.html_url}")
        
        # Close resolved TODOs if requested
        if close_resolved and not dry_run:
            if verbose:
                click.echo("\nChecking for resolved TODOs...")
            
            closed_issues = github_client.close_resolved_todos(todos)
            
            if closed_issues:
                click.echo(f"Closed {len(closed_issues)} resolved TODO issues")
                if verbose:
                    for issue in closed_issues:
                        click.echo(f"  #{issue.number}: {issue.title}")
            else:
                click.echo("No resolved TODOs to close")
        
        click.echo("\nTODO tracking completed successfully!")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@click.command()
@click.option(
    '--repo-path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default='.',
    help='Path to the repository to scan'
)
@click.option(
    '--ignore-dirs',
    multiple=True,
    default=None,
    help='Additional directories to ignore'
)
@click.option(
    '--ignore-patterns',
    multiple=True,
    default=None,
    help='Additional file patterns to ignore'
)
def scan_only(repo_path: str, ignore_dirs: tuple, ignore_patterns: tuple) -> None:
    """
    Scan a repository for TODOs without creating GitHub issues.
    
    This command is useful for testing the scanner or getting a quick overview
    of TODOs in a repository without needing GitHub credentials.
    """
    try:
        scanner_kwargs = {}
        if ignore_dirs:
            scanner_kwargs['ignore_dirs'] = list(ignore_dirs)
        if ignore_patterns:
            scanner_kwargs['ignore_patterns'] = list(ignore_patterns)
        
        scanner = TodoScanner(**scanner_kwargs)
        todos = scanner.scan_directory(repo_path)
        
        if not todos:
            click.echo("No TODOs found in the repository.")
            return
        
        summary = scanner.get_summary(todos)
        
        click.echo(f"Scan Results for: {repo_path}")
        click.echo("=" * 50)
        click.echo(f"Total TODOs: {summary['total_todos']}")
        click.echo(f"Files with TODOs: {summary['files_with_todos']}")
        click.echo(f"TODO types: {summary['todo_types']}")
        
        click.echo("\nTODOs found:")
        for todo in todos:
            click.echo(f"  {todo.file_path}:{todo.line_number} [{todo.todo_type}] {todo.content}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


# Group commands
@click.group()
def cli() -> None:
    """GitHub Action TODO Tracker - Scan repositories for TODOs and create GitHub issues."""
    pass


cli.add_command(main, name='track')
cli.add_command(scan_only, name='scan')


if __name__ == '__main__':
    cli()
