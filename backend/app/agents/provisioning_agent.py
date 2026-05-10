import logging
import requests
from typing import Dict, Any, List
from datetime import datetime
from ..core.cloudant_db import cloudant_db
from ..core.config import settings

logger = logging.getLogger(__name__)

class ProvisioningAgent:
    """
    Provisioning Agent
    Parses the final approved SOW and uses the GitHub API to create issues 
    for each milestone with appropriate labels and due dates.
    """
    def __init__(self):
        self.github_token = settings.GITHUB_TOKEN
        self.github_owner = settings.GITHUB_OWNER
        self.github_repo = settings.GITHUB_REPO

    async def _get_global_settings(self) -> Dict[str, Any]:
        return await cloudant_db.get_document("global_api_settings") or {}

    async def provision_approved_sow(self, sow_id: str) -> Dict[str, Any]:
        doc = await cloudant_db.get_document(sow_id)
        if not doc:
            raise ValueError(f"SOW {sow_id} not found")
            
        global_settings = await self._get_global_settings()
        token = global_settings.get("github_token") or self.github_token
        owner = global_settings.get("github_owner") or self.github_owner
        repo = global_settings.get("github_repo") or self.github_repo

        if not token or not owner or not repo:
            logger.warning("GitHub credentials missing. Cannot provision.")
            return {"status": "failed", "reason": "Missing GitHub credentials"}

        created_issues = []
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Find milestones and deliverables
        obligations = doc.get("obligations", [])
        
        for ob in obligations:
            # We want to provision issues for milestones and deliverables
            title = f"[{doc['sow_number']}] {ob.get('description', 'Milestone')}"
            deadline = ob.get("deadline", "")
            labels = ["sow-milestone", doc.get("sow_number")]
            
            risk_level = ob.get("risk_level", "low")
            if risk_level in ["high", "critical"]:
                labels.append(f"risk-{risk_level}")
                
            body = (
                f"**SOW:** {doc.get('project_name')} ({doc['sow_number']})\n"
                f"**Type:** {ob.get('type', 'deliverable')}\n"
                f"**Deadline / SLA:** {deadline}\n\n"
                f"**Penalty Exposure:** ${ob.get('penalty_amount', 0)}\n\n"
                f"*Automatically provisioned by SOW Sentinel Provisioning Agent.*"
            )

            response = requests.post(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                headers=headers,
                json={
                    "title": title,
                    "body": body,
                    "labels": labels
                }
            )

            if response.status_code == 201:
                issue_data = response.json()
                
                # Save the mapping back to the database
                mapping = {
                    "id": f"MAP-{ob['id']}",
                    "sow_id": sow_id,
                    "obligation_id": ob["id"],
                    "integration_type": "github",
                    "external_id": str(issue_data["number"]),
                    "external_url": issue_data["html_url"],
                    "sync_status": "active"
                }
                ob["mapped_to"] = mapping
                created_issues.append({
                    "obligation_id": ob["id"],
                    "issue_number": issue_data["number"],
                    "url": issue_data["html_url"]
                })
            else:
                logger.error(f"Failed to create GitHub issue: {response.text}")

        if created_issues:
            await cloudant_db.update_document(doc["_id"], doc)

        return {
            "status": "success",
            "provisioned_issues_count": len(created_issues),
            "issues": created_issues
        }

provisioning_agent = ProvisioningAgent()
