"""
GitHub Service
Real GitHub API integration for issue management and webhooks
"""
import logging
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    logging.warning("PyGithub not installed. GitHub integration will use mock data.")

logger = logging.getLogger(__name__)


class GitHubService:
    """
    Service for interacting with GitHub API
    Manages issues, webhooks, and repository operations
    """
    
    def __init__(self, access_token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize GitHub service
        
        Args:
            access_token: GitHub personal access token
            repo_name: Repository name in format "owner/repo"
        """
        self.access_token = access_token or os.getenv('GITHUB_ACCESS_TOKEN')
        self.repo_name = repo_name or os.getenv('GITHUB_REPO_NAME')
        
        self.github = None
        self.repo = None
        
        if GITHUB_AVAILABLE and self.access_token:
            try:
                self.github = Github(self.access_token)
                if self.repo_name:
                    self.repo = self.github.get_repo(self.repo_name)
                    logger.info(f"Connected to GitHub repo: {self.repo_name}")
            except Exception as e:
                logger.error(f"Failed to initialize GitHub client: {e}")
        else:
            logger.warning("GitHub service initialized without credentials")
    
    # ========================================================================
    # ISSUE OPERATIONS
    # ========================================================================
    
    def get_issue(self, issue_number: int) -> Optional[Dict[str, Any]]:
        """Get issue by number"""
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return None
        
        try:
            issue = self.repo.get_issue(issue_number)
            return self._issue_to_dict(issue)
        except GithubException as e:
            logger.error(f"Failed to get issue #{issue_number}: {e}")
            return None
    
    def list_open_issues(
        self,
        labels: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List open issues, optionally filtered by labels
        
        Args:
            labels: Filter by labels (e.g., ['incident', 'p1'])
            limit: Maximum number of issues to return
        """
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return []
        
        try:
            issues = self.repo.get_issues(
                state='open',
                labels=labels or [],
                sort='created',
                direction='desc'
            )
            
            result = []
            for issue in issues[:limit]:
                if not issue.pull_request:  # Exclude pull requests
                    result.append(self._issue_to_dict(issue))
            
            return result
            
        except GithubException as e:
            logger.error(f"Failed to list issues: {e}")
            return []
    
    def list_incident_issues(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List issues labeled as incidents"""
        return self.list_open_issues(labels=['incident'], limit=limit)
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create new issue
        
        Args:
            title: Issue title
            body: Issue description
            labels: Labels to apply
            assignees: Users to assign
        """
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return None
        
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )
            
            logger.info(f"Created issue #{issue.number}: {title}")
            return self._issue_to_dict(issue)
            
        except GithubException as e:
            logger.error(f"Failed to create issue: {e}")
            return None
    
    def add_comment(self, issue_number: int, comment: str) -> bool:
        """Add comment to issue"""
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return False
        
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            logger.info(f"Added comment to issue #{issue_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to add comment: {e}")
            return False
    
    def close_issue(self, issue_number: int, comment: Optional[str] = None) -> bool:
        """Close issue with optional comment"""
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return False
        
        try:
            issue = self.repo.get_issue(issue_number)
            
            if comment:
                issue.create_comment(comment)
            
            issue.edit(state='closed')
            logger.info(f"Closed issue #{issue_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to close issue: {e}")
            return False
    
    def add_label(self, issue_number: int, label: str) -> bool:
        """Add label to issue"""
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return False
        
        try:
            issue = self.repo.get_issue(issue_number)
            issue.add_to_labels(label)
            logger.info(f"Added label '{label}' to issue #{issue_number}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to add label: {e}")
            return False
    
    # ========================================================================
    # WEBHOOK OPERATIONS
    # ========================================================================
    
    def setup_webhook(
        self,
        webhook_url: str,
        secret: Optional[str] = None,
        events: Optional[List[str]] = None
    ) -> bool:
        """
        Setup webhook for repository
        
        Args:
            webhook_url: URL to receive webhook events
            secret: Secret for webhook signature verification
            events: Events to subscribe to (default: issues, issue_comment)
        """
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return False
        
        if events is None:
            events = ['issues', 'issue_comment']
        
        try:
            config = {
                'url': webhook_url,
                'content_type': 'json',
            }
            
            if secret:
                config['secret'] = secret
            
            hook = self.repo.create_hook(
                name='web',
                config=config,
                events=events,
                active=True
            )
            
            logger.info(f"Created webhook: {hook.id}")
            return True
            
        except GithubException as e:
            logger.error(f"Failed to create webhook: {e}")
            return False
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """List all webhooks for repository"""
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return []
        
        try:
            hooks = self.repo.get_hooks()
            return [
                {
                    'id': hook.id,
                    'url': hook.config.get('url'),
                    'events': hook.events,
                    'active': hook.active
                }
                for hook in hooks
            ]
        except GithubException as e:
            logger.error(f"Failed to list webhooks: {e}")
            return []
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _issue_to_dict(self, issue) -> Dict[str, Any]:
        """Convert GitHub issue object to dictionary"""
        return {
            'number': issue.number,
            'title': issue.title,
            'body': issue.body,
            'state': issue.state,
            'labels': [label.name for label in issue.labels],
            'assignees': [assignee.login for assignee in issue.assignees],
            'created_at': issue.created_at.isoformat() if issue.created_at else None,
            'updated_at': issue.updated_at.isoformat() if issue.updated_at else None,
            'closed_at': issue.closed_at.isoformat() if issue.closed_at else None,
            'html_url': issue.html_url,
            'user': issue.user.login if issue.user else None,
            'comments': issue.comments
        }
    
    def is_connected(self) -> bool:
        """Check if GitHub service is connected"""
        return self.github is not None and self.repo is not None


# Singleton instance
_github_service = None


def get_github_service(
    access_token: Optional[str] = None,
    repo_name: Optional[str] = None
) -> GitHubService:
    """Get or create GitHub service singleton"""
    global _github_service
    if _github_service is None:
        _github_service = GitHubService(access_token, repo_name)
    return _github_service


# Made with Bob - Real GitHub Integration