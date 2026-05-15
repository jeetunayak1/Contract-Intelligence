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
    
    # ========================================================================
    # OPERATIONAL METRICS
    # ========================================================================
    
    def fetch_issue_metrics(
        self,
        labels: Optional[List[str]] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch operational metrics from GitHub issues in IncidentMetrics format
        
        Args:
            labels: Filter by labels (e.g., ['incident', 'bug'])
            days: Number of days to look back
            
        Returns:
            List of incident metrics compatible with IncidentMetrics model
        """
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return []
        
        try:
            from datetime import datetime, timedelta
            
            since = datetime.utcnow() - timedelta(days=days)
            
            issues = self.repo.get_issues(
                state='all',
                labels=labels or [],
                since=since,
                sort='created',
                direction='desc'
            )
            
            metrics = []
            for issue in issues:
                if issue.pull_request:  # Skip PRs
                    continue
                
                # Calculate resolution time
                resolution_hours = None
                if issue.closed_at and issue.created_at:
                    delta = issue.closed_at - issue.created_at
                    resolution_hours = delta.total_seconds() / 3600
                
                # Determine priority from labels
                priority = None
                for label in issue.labels:
                    label_name = label.name.upper()
                    if label_name in ['P1', 'P2', 'P3', 'P4', 'P5']:
                        priority = label_name
                        break
                
                # Skip if no priority (not an incident)
                if not priority:
                    continue
                
                # Extract service from labels (look for service-* labels)
                service = "unknown-service"
                label_names = [l.name.lower() for l in issue.labels]
                for label_name in label_names:
                    if label_name.startswith('service-'):
                        service = label_name.replace('service-', '')
                        break
                    # Also check for common service names
                    elif label_name in ['payments-api', 'order-processing', 'notification-service',
                                       'reporting-service', 'auth-service', 'api-gateway']:
                        service = label_name
                        break
                
                # Parse affected users from issue body
                affected_users = 0
                if issue.body:
                    import re
                    # Look for patterns like "affecting 12000 users" or "12,000 users affected"
                    match = re.search(r'(\d+[,\d]*)\s*users?\s*(affected|impacted)', issue.body.lower())
                    if match:
                        affected_users = int(match.group(1).replace(',', ''))
                
                # Format for IncidentMetrics model
                metrics.append({
                    'incident_id': f"GH-{issue.number}",
                    'priority': priority,
                    'service': service,
                    'created_at': issue.created_at.isoformat() if issue.created_at else datetime.utcnow().isoformat(),
                    'resolved_at': issue.closed_at.isoformat() if issue.closed_at else None,
                    'acknowledged_at': None,  # GitHub doesn't track this
                    'workaround_at': None,  # GitHub doesn't track this
                    'resolution_hours': resolution_hours,
                    'acknowledge_minutes': None,
                    'workaround_hours': None,
                    'affected_users': affected_users,
                    'downtime_minutes': None
                })
            
            logger.info(f"Fetched metrics for {len(metrics)} GitHub incidents (filtered by priority)")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to fetch issue metrics: {e}")
            return []
    
    def fetch_pr_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Fetch PR review and merge metrics
        
        Args:
            days: Number of days to look back
            
        Returns:
            PR metrics summary
        """
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return {}
        
        try:
            from datetime import datetime, timedelta
            
            since = datetime.utcnow() - timedelta(days=days)
            
            pulls = self.repo.get_pulls(
                state='all',
                sort='created',
                direction='desc'
            )
            
            total_prs = 0
            merged_prs = 0
            total_review_time = 0
            reviewed_prs = 0
            
            for pr in pulls:
                if pr.created_at < since:
                    break
                
                total_prs += 1
                
                if pr.merged:
                    merged_prs += 1
                    
                    # Calculate review time
                    if pr.created_at and pr.merged_at:
                        delta = pr.merged_at - pr.created_at
                        review_hours = delta.total_seconds() / 3600
                        total_review_time += review_hours
                        reviewed_prs += 1
            
            avg_review_hours = total_review_time / reviewed_prs if reviewed_prs > 0 else 0
            merge_rate = (merged_prs / total_prs * 100) if total_prs > 0 else 0
            
            return {
                'total_prs': total_prs,
                'merged_prs': merged_prs,
                'merge_rate_percent': round(merge_rate, 1),
                'avg_review_hours': round(avg_review_hours, 1),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch PR metrics: {e}")
            return {}
    
    def fetch_deployment_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Fetch deployment frequency metrics
        
        Args:
            days: Number of days to look back
            
        Returns:
            Deployment metrics
        """
        if not self.repo:
            logger.warning("GitHub repo not configured")
            return {}
        
        try:
            from datetime import datetime, timedelta
            
            since = datetime.utcnow() - timedelta(days=days)
            
            # Count releases as deployments
            releases = self.repo.get_releases()
            
            deployment_count = 0
            for release in releases:
                if release.created_at and release.created_at >= since:
                    deployment_count += 1
            
            deployments_per_week = (deployment_count / days) * 7 if days > 0 else 0
            
            return {
                'total_deployments': deployment_count,
                'deployments_per_week': round(deployments_per_week, 1),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch deployment metrics: {e}")
            return {}


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