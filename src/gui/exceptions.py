# c:\Users\johnw\OneDrive\Desktop\SentinelPC\src\gui\exceptions.py
"""Custom exceptions for GUI operations.

This module contains custom exceptions used specifically within the SentinelPC
GUI layer, including interactions with the GUI worker and UI elements.
"""

from typing import Optional

# --- Base GUI Exception ---


class GuiException(Exception):
    """Base class for exceptions raised by the GUI module."""

    def __init__(self, message: str = "An unspecified GUI error occurred."):
        super().__init__(message)


# --- Worker Related Exceptions ---


class WorkerError(GuiException):
    """Base class for exceptions related to the GUIWorker."""

    def __init__(self, message: str = "An error occurred in the GUI worker."):
        super().__init__(message)


class WorkerNotRunningError(WorkerError):
    """Exception raised when attempting to use a worker that is not running."""

    def __init__(
        self, message: str = "Operation failed: The GUI worker is not running."
    ):
        super().__init__(message)


class WorkerQueueFullError(WorkerError):
    """Exception raised when the worker's task queue is full."""

    def __init__(
        self, message: str = "Operation failed: The GUI worker task queue is full."
    ):
        super().__init__(message)


class CancelledException(WorkerError):
    """Exception raised when a worker task is cancelled.

    This can occur due to worker shutdown or an explicit cancellation request.
    It inherits from WorkerError as it relates to task execution within the worker.
    """

    def __init__(self, reason: Optional[str] = None):
        """Initialize the CancelledException.

        Args:
            reason: An optional string explaining why the task was cancelled.
        """
        self.reason = reason if reason else "Task cancelled without specific reason."
        message = f"Worker task cancelled: {self.reason}"
        super().__init__(message)


# --- UI Related Exceptions ---


class GuiResourceError(GuiException):
    """Exception raised when a GUI resource (e.g., image, theme) cannot be loaded."""

    def __init__(self, resource_name: str, message: Optional[str] = None):
        """Initialize the GuiResourceError.

        Args:
            resource_name: The name or path of the resource that failed to load.
            message: An optional specific error message.
        """
        self.resource_name = resource_name
        if message is None:
            message = f"Failed to load GUI resource: '{resource_name}'."
        else:
            message = f"Failed to load GUI resource '{resource_name}': {message}"
        super().__init__(message)


class GuiCallbackError(GuiException):
    """Exception raised when an error occurs within a GUI callback function."""

    def __init__(self, callback_name: str, original_exception: Exception):
        """Initialize the GuiCallbackError.

        Args:
            callback_name: The name of the callback function where the error occurred.
            original_exception: The original exception that was caught.
        """
        self.callback_name = callback_name
        self.original_exception = original_exception
        message = f"Error executing GUI callback '{callback_name}': {type(original_exception).__name__}: {original_exception}"
        super().__init__(message)
