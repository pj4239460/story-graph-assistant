"""
Token statistics utilities
"""
from __future__ import annotations
from datetime import datetime
from ..models.project import Project


def record_usage(project: Project, feature: str, usage: dict) -> None:
    """
    Record token usage
    
    Args:
        project: Project object
        feature: Feature name (e.g., "summary", "ooc", "what_if")
        usage: Usage dictionary returned by LLM
    """
    if not usage:
        return
    
    # Calculate total tokens
    total = usage.get("total_tokens") or (
        usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
    )
    
    if total <= 0:
        return
    
    stats = project.tokenStats
    
    # Update project total usage
    stats.projectUsed += total
    
    # Update usage by feature
    stats.byFeature[feature] = stats.byFeature.get(feature, 0) + total
    
    # Update daily usage (reset if date changed)
    today = datetime.now().strftime("%Y-%m-%d")
    if stats.todayDate != today:
        stats.todayDate = today
        stats.todayUsed = 0
    
    stats.todayUsed += total


def check_token_limit(project: Project, estimated_tokens: int = 0) -> tuple[bool, str]:
    """
    Check if token limit is exceeded
    
    Returns:
        (allowed_to_continue, message)
    """
    stats = project.tokenStats
    settings = project.aiSettings
    
    # Check project limit
    if stats.projectUsed + estimated_tokens > settings.projectTokenLimit:
        return False, f"Project token limit reached ({settings.projectTokenLimit})"
    
    # Check daily soft limit (warning only, not blocking)
    if stats.todayUsed + estimated_tokens > settings.dailyTokenSoftLimit:
        return True, f"Daily token usage exceeds soft limit ({settings.dailyTokenSoftLimit})"
    
    return True, ""
