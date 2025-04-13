"""Custom exceptions for GUI operations.

This module contains custom exceptions used in GUI operations.
"""

class CancelledException(Exception):
    """Exception raised when a task is cancelled.
    
    This exception is raised when a task is cancelled due to worker shutdown
    or explicit cancellation request.
    """
    pass