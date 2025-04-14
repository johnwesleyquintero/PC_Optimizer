# c:\Users\johnw\OneDrive\Desktop\SentinelPC\src\gui\gui_worker.py
"""Worker module for handling long-running GUI operations.

This module provides a robust mechanism for executing potentially blocking tasks
in a separate thread, preventing the main GUI thread from freezing. It uses
queues for communication between the GUI thread and the worker thread.
"""

import logging
from threading import Thread, Lock
from queue import Queue, Empty, Full
from typing import Callable, Any, Optional, Tuple
import tkinter as tk
import time  # Import time for join timeout logic

from .exceptions import CancelledException

logger = logging.getLogger(__name__)  # Use module-level logger


class GUIWorker:
    """Manages a separate thread to execute tasks without blocking the GUI.

    Tasks are added via `add_task`, executed sequentially in the worker thread,
    and their results (or exceptions) are passed back to the main GUI thread
    via callbacks scheduled using `root.after`.
    """

    def __init__(self, max_queue_size: int = 100, name: str = "GUIWorkerThread"):
        """Initialize the worker with task and result queues.

        Args:
            max_queue_size: Maximum number of tasks allowed in the queue.
            name: Name for the worker thread (useful for debugging).
        """
        if max_queue_size <= 0:
            raise ValueError("max_queue_size must be positive")

        self.task_queue: Queue[Tuple[Callable, Callable, tuple, dict]] = Queue(
            maxsize=max_queue_size
        )
        self.result_queue: Queue[Tuple[Callable, Any]] = Queue()
        self._running = False
        self._stop_requested = False  # Flag to signal shutdown request
        self._lock = Lock()
        self._worker_thread: Optional[Thread] = None
        self._thread_name = name
        logger.info(f"{self._thread_name}: Initialized (Max Queue: {max_queue_size})")

    @property
    def is_running(self) -> bool:
        """Check if the worker thread is currently active."""
        with self._lock:
            return self._running

    def start(self) -> None:
        """Start the worker thread if it's not already running."""
        with self._lock:
            if self._running:
                logger.warning(
                    f"{self._thread_name}: Start called but already running."
                )
                return
            if self._worker_thread and self._worker_thread.is_alive():
                logger.warning(
                    f"{self._thread_name}: Start called but thread is still alive (unexpected state)."
                )
                # Optionally try to join previous thread here? Or raise error?
                # For now, just log and proceed to create a new one.

            self._running = True
            self._stop_requested = False
            self._worker_thread = Thread(
                target=self._process_queue, name=self._thread_name, daemon=True
            )
            self._worker_thread.start()
            logger.info(f"{self._thread_name}: Worker thread started.")

    def stop(self, timeout: float = 2.0) -> None:
        """Request the worker thread to stop and wait for it to terminate.

        Args:
            timeout: Maximum time in seconds to wait for the thread to join.
        """
        should_join = False
        with self._lock:
            if not self._running and not (
                self._worker_thread and self._worker_thread.is_alive()
            ):
                logger.info(f"{self._thread_name}: Stop called but already stopped.")
                return  # Already stopped or never started

            if self._stop_requested:
                logger.warning(
                    f"{self._thread_name}: Stop called again while already stopping."
                )
                # Allow join attempt again if needed
                if self._worker_thread and self._worker_thread.is_alive():
                    should_join = True
            else:
                logger.info(
                    f"{self._thread_name}: Stop requested. Signaling worker thread..."
                )
                self._stop_requested = True
                # Do not set self._running = False here yet, let the thread finish processing
                if self._worker_thread:
                    should_join = True

        if should_join and self._worker_thread:
            thread_to_join = self._worker_thread  # Capture ref outside lock
            logger.info(
                f"{self._thread_name}: Waiting up to {timeout}s for worker thread to join..."
            )
            thread_to_join.join(timeout=timeout)
            if thread_to_join.is_alive():
                logger.warning(
                    f"{self._thread_name}: Worker thread did not terminate within {timeout}s."
                )
                # Thread is still alive - potentially stuck in a task.
                # Setting running to False now to prevent adding new tasks.
                with self._lock:
                    self._running = False
            else:
                logger.info(f"{self._thread_name}: Worker thread joined successfully.")
                with self._lock:
                    self._running = False  # Confirm stopped state
                    self._worker_thread = None  # Clear reference
        else:
            # Case where thread wasn't running or didn't exist
            with self._lock:
                self._running = False
                self._worker_thread = None

        # Always attempt cleanup, even if join timed out
        logger.info(f"{self._thread_name}: Cleaning up queues...")
        self._clear_queues()
        logger.info(f"{self._thread_name}: Worker stopped.")

    def add_task(
        self,
        task: Callable,
        callback: Callable[[Optional[Any], Optional[str]], None],
        *args,
        **kwargs,
    ) -> bool:
        """Add a task to the execution queue.

        Args:
            task: The function to execute in the background worker thread.
            callback: The function to call in the GUI thread upon completion.
                      It will receive two arguments: `result` (the return value
                      of the task, or None if an error occurred) and `error`
                      (an error message string if an exception occurred, else None).
            *args: Positional arguments to pass to the task function.
            **kwargs: Keyword arguments to pass to the task function.

        Returns:
            True if the task was added successfully, False otherwise (e.g., queue full).

        Raises:
            ValueError: If the worker is not running or is stopping.
        """
        with self._lock:
            if not self._running or self._stop_requested:
                # Raise an error or log and return False? Raising is clearer about state.
                msg = (
                    "Worker is not running."
                    if not self._running
                    else "Worker is stopping."
                )
                logger.error(
                    f"{self._thread_name}: Cannot add task '{getattr(task, '__name__', 'unknown')}': {msg}"
                )
                raise ValueError(msg)

        try:
            # Note: Using a short timeout to prevent blocking the GUI thread if queue is full
            self.task_queue.put((task, callback, args, kwargs), block=True, timeout=0.1)
            logger.debug(
                f"{self._thread_name}: Added task '{getattr(task, '__name__', 'unknown')}' to queue."
            )
            return True
        except Full:
            logger.error(
                f"{self._thread_name}: Task queue is full. Cannot add task '{getattr(task, '__name__', 'unknown')}'."
            )
            # Optionally raise Full exception here instead of returning False
            # raise Full("Task queue is full")
            return False
        except Exception as e:
            logger.exception(
                f"{self._thread_name}: Unexpected error adding task '{getattr(task, '__name__', 'unknown')}': {e}"
            )
            return False

    def _process_queue(self) -> None:
        """The main loop for the worker thread, processing tasks from the queue."""
        logger.info(f"{self._thread_name}: Worker loop started.")
        while not self._stop_requested:
            try:
                # Use a timeout to allow checking stop_requested periodically
                task, callback, args, kwargs = self.task_queue.get(timeout=0.5)
                
                try:
                    # Execute the task
                    result = task(*args, **kwargs)
                    error = None
                except Exception as e:
                    logger.exception(f"{self._thread_name}: Task execution failed: {e}")
                    result = None
                    error = str(e)
                
                # Queue the result/error for processing in the main thread
                self.result_queue.put((callback, (result, error)))
                
            except Empty:
                # Queue.get timeout - normal, just continue the loop
                continue
            except Exception as e:
                logger.exception(f"{self._thread_name}: Unexpected error in worker loop: {e}")
                # Don't break the loop on unexpected errors
                # Wait indefinitely for a task, but check stop_requested periodically
                task, callback, args, kwargs = self.task_queue.get(
                    block=True, timeout=0.2
                )
            except Empty:
                # Timeout occurred, loop back to check self._stop_requested
                continue
            except Exception as e:
                logger.exception(
                    f"{self._thread_name}: Error getting task from queue: {e}"
                )
                time.sleep(0.1)  # Avoid busy-looping on unexpected queue errors
                continue

            # Double-check stop request *after* getting a task, before running it
            if self._stop_requested:
                logger.info(
                    f"{self._thread_name}: Stop requested, discarding task '{getattr(task, '__name__', 'unknown')}'."
                )
                self.task_queue.task_done()  # Mark task as done even if discarded
                continue  # Skip execution

            task_name = getattr(task, "__name__", "unknown_task")
            try:
                logger.debug(f"{self._thread_name}: Starting task '{task_name}'...")
                result = task(*args, **kwargs)
                logger.debug(
                    f"{self._thread_name}: Task '{task_name}' completed successfully."
                )
                self.result_queue.put((callback, result))
            except CancelledException as ce:
                logger.warning(
                    f"{self._thread_name}: Task '{task_name}' cancelled: {ce}"
                )
                # Pass the cancellation reason back if needed, or just treat as error
                self.result_queue.put((callback, ce))  # Pass exception itself
            except Exception as e:
                logger.exception(
                    f"{self._thread_name}: Error executing task '{task_name}': {e}"
                )
                # Pass the exception itself to the result queue
                self.result_queue.put((callback, e))
            finally:
                # Crucial: Ensure task_done is called even if errors occur
                self.task_queue.task_done()

        logger.info(f"{self._thread_name}: Worker loop finished.")

    def process_results(self, root: tk.Tk) -> None:
        """Processes results from the result queue in the main GUI thread.

        This method should be called periodically from the Tkinter main loop
        (e.g., using `root.after`).

        Args:
            root: The Tkinter root window, used for scheduling the next check.
        """
        # Check if the root window still exists
        if not root.winfo_exists():
            logger.warning(
                f"{self._thread_name}: Root window destroyed, stopping result processing."
            )
            # Consider calling self.stop() here if not already handled elsewhere
            return

        try:
            # Process all currently available results
            while True:
                callback, result_or_error = self.result_queue.get_nowait()

                try:
                    if isinstance(result_or_error, Exception):
                        # Pass exception message as the error string
                        error_msg = (
                            f"{type(result_or_error).__name__}: {str(result_or_error)}"
                        )
                        logger.warning(
                            f"{self._thread_name}: Executing callback for failed task: {error_msg}"
                        )
                        callback(None, error=error_msg)
                    else:
                        # Task succeeded
                        logger.debug(
                            f"{self._thread_name}: Executing callback for successful task."
                        )
                        callback(result_or_error, error=None)
                except Exception as e:
                    # Catch errors *within* the callback function itself
                    logger.exception(
                        f"{self._thread_name}: Error occurred within result callback '{getattr(callback, '__name__', 'unknown')}': {e}"
                    )
                finally:
                    # Mark result as processed regardless of callback success/failure
                    self.result_queue.task_done()

        except Empty:
            # No more results currently in the queue
            pass
        except Exception as e:
            # Catch unexpected errors during queue processing
            logger.exception(f"{self._thread_name}: Error processing result queue: {e}")

        # Schedule the next check only if the worker is intended to be running
        # Use self.is_running property which checks _running under lock
        if self.is_running:
            root.after(100, lambda: self.process_results(root))
        else:
            logger.debug(
                f"{self._thread_name}: Worker not running, stopping result processing loop."
            )

    def _clear_queues(self) -> None:
        """Safely clear all items from task and result queues."""
        logger.debug(f"{self._thread_name}: Clearing task and result queues.")
        # Clear task queue
        while not self.task_queue.empty():
            try:
                task_info = self.task_queue.get_nowait()
                task_name = getattr(task_info[0], "__name__", "unknown")
                logger.debug(
                    f"{self._thread_name}: Discarding task '{task_name}' from queue during cleanup."
                )
                self.task_queue.task_done()
            except Empty:
                break  # Should not happen if not empty, but safety first
            except Exception as e:
                logger.error(
                    f"{self._thread_name}: Error clearing task queue item: {e}"
                )
                break  # Avoid potential infinite loop on unexpected errors

        # Clear result queue
        while not self.result_queue.empty():
            try:
                self.result_queue.get_nowait()
                self.result_queue.task_done()
            except Empty:
                break
            except Exception as e:
                logger.error(
                    f"{self._thread_name}: Error clearing result queue item: {e}"
                )
                break
        logger.debug(f"{self._thread_name}: Queues cleared.")
