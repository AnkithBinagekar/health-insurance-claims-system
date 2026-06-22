class ClaimsSystemBaseError(Exception):
    """Base exception for all system-level errors."""
    pass

class AgentExecutionError(ClaimsSystemBaseError):
    """Raised when an agent encounters an unrecoverable runtime error."""
    pass

class PolicyLoadError(ClaimsSystemBaseError):
    """Raised when policy_terms.json cannot be read or parsed."""
    pass

class DocumentStorageError(ClaimsSystemBaseError):
    """Raised when document bytes cannot be persisted to temp storage."""
    pass