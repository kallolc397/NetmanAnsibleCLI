"""
Git integration module for the Network Device Management tool.

This module handles Git operations for configuration version control.
"""
import os
import time
import git
from pathlib import Path

class GitManager:
    """Manages Git operations for configuration tracking."""
    
    def __init__(self, repo_path="configs"):
        """Initialize with the Git repository path."""
        self.repo_path = repo_path
        self._ensure_repo_exists()
    
    def _ensure_repo_exists(self):
        """Ensure the Git repository exists and is initialized."""
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path, exist_ok=True)
        
        if not os.path.exists(os.path.join(self.repo_path, '.git')):
            self.init_repo(self.repo_path)
    
    def init_repo(self, path=None):
        """
        Initialize a Git repository.
        
        Args:
            path (str, optional): Path where to initialize the repository
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            path = path or self.repo_path
            
            # Ensure the directory exists
            os.makedirs(path, exist_ok=True)
            
            # Initialize the repository
            repo = git.Repo.init(path)
            
            # Create .gitignore file if it doesn't exist
            gitignore_path = os.path.join(path, '.gitignore')
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, 'w') as f:
                    f.write("# Generated by NetMan\n")
                    f.write("*.tmp\n")
                    f.write("*.bak\n")
            
            # Create an initial commit if the repo is empty
            if not repo.heads:
                try:
                    # Configure git user if not already configured
                    try:
                        repo.git.config('user.name', 'NetMan')
                        repo.git.config('user.email', 'netman@example.com')
                    except:
                        pass  # Continue even if config fails
                        
                    # Add and commit the .gitignore file
                    repo.git.add(gitignore_path)
                    repo.git.commit('-m', 'Initial commit')
                except Exception as commit_error:
                    print(f"Warning: Could not create initial commit: {str(commit_error)}")
                    # This is not critical, we can continue without the initial commit
            
            return True
        except Exception as e:
            print(f"Error initializing Git repository: {str(e)}")
            return False
    
    def commit_changes(self, message=None):
        """
        Commit all changes in the repository.
        
        Args:
            message (str, optional): Commit message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            repo = git.Repo(self.repo_path)
            
            # Check if there are changes to commit
            if not repo.is_dirty(untracked_files=True):
                print("No changes to commit")
                return True
            
            # Add all changes
            repo.git.add(A=True)
            
            # Create commit message if not provided
            if not message:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                message = f"Configuration update at {timestamp}"
            
            # Commit changes
            repo.git.commit('-m', message)
            
            return True
        except Exception as e:
            print(f"Error committing changes: {str(e)}")
            return False
    
    def get_file_at_revision(self, file_path, revision):
        """
        Get the content of a file at a specific revision.
        
        Args:
            file_path (str): Path to the file relative to the repository root
            revision (str): Git revision (commit hash, branch, or reference)
            
        Returns:
            str: File content or None if failed
        """
        try:
            repo = git.Repo(self.repo_path)
            
            # Get the file content at the specified revision
            return repo.git.show(f"{revision}:{file_path}")
        except Exception as e:
            print(f"Error getting file at revision: {str(e)}")
            return None
    
    def show_diff(self, hostname, revisions="HEAD~1..HEAD"):
        """
        Show the configuration differences for a device between revisions.
        
        Args:
            hostname (str): Device hostname
            revisions (str): Git revision range (e.g., "HEAD~1..HEAD")
            
        Returns:
            str: Diff output or None if failed
        """
        try:
            repo = git.Repo(self.repo_path)
            
            # Get the path to the latest config file
            config_file = os.path.join(hostname, f"{hostname}_latest.cfg")
            
            # Check if the file exists
            if not os.path.exists(os.path.join(self.repo_path, config_file)):
                return None
            
            # Get the diff
            diff = repo.git.diff(revisions, '--', config_file)
            
            return diff
        except Exception as e:
            print(f"Error showing diff: {str(e)}")
            return None
    
    def get_commit_history(self, hostname, max_count=10):
        """
        Get commit history for a device's configuration.
        
        Args:
            hostname (str): Device hostname
            max_count (int): Maximum number of commits to retrieve
            
        Returns:
            list: List of commit dictionaries or None if failed
        """
        try:
            repo = git.Repo(self.repo_path)
            
            # Get the path to the latest config file
            config_file = os.path.join(hostname, f"{hostname}_latest.cfg")
            
            # Check if the file exists
            if not os.path.exists(os.path.join(self.repo_path, config_file)):
                return None
            
            # Get the commit history
            commits = []
            for commit in repo.iter_commits(paths=config_file, max_count=max_count):
                commits.append({
                    'hash': commit.hexsha,
                    'short_hash': commit.hexsha[:7],
                    'author': commit.author.name,
                    'date': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(commit.committed_date)),
                    'message': commit.message
                })
            
            return commits
        except Exception as e:
            print(f"Error getting commit history: {str(e)}")
            return None
