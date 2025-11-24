"""
Custom Exceptions
"""


class BugTriageException(Exception):
    """Base exception for Bug Triage service"""
    pass


class ConfigurationError(BugTriageException):
    """Configuration related errors"""
    pass


class GitOperationError(BugTriageException):
    """Git operation related errors"""
    pass


class SlackNotificationError(BugTriageException):
    """Slack notification related errors"""
    pass


class ClaudeAnalysisError(BugTriageException):
    """Claude analysis related errors"""
    pass
