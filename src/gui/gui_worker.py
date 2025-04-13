"""Worker module for handling long-running GUI operations.

This module provides thread management for GUI operations to prevent freezing.
"""

import logging
from threading import Thread, Lock
from queue import Queue, Empty, Full
from typing import Callable, Any, Dict, Optional
import tkinter as tk
from .exceptions import CancelledException

class GUIWorker:
    """Worker class for handling long-running GUI operations in separate threads."""
    
    def __init__(self, max_queue_size: int = 100):
        """Initialize the worker with a task queue.
        
        Args:
            max_queue_size: Maximum number of tasks that can be queued
        """
        self.task_queue = Queue(maxsize=max_queue_size)
        self.result_queue = Queue()
        self.running = False
        self._lock = Lock()
        self._current_task: Optional[Callable] = None
    
    def start(self) -> None:
        """Start the worker thread."""
        with self._lock:
            if not self.running:
                self.running = True
                self.worker_thread = Thread(target=self._process_queue, daemon=True)
                self.worker_thread.start()
                logging.info("GUIWorker thread started")
    
    def stop(self) -> None:
        """Stop the worker thread and clean up resources."""
        with self._lock:
            if self.running:
                self.running = False
                if hasattr(self, 'worker_thread'):
                    try:
                        self.worker_thread.join(timeout=2.0)
                        if self.worker_thread.is_alive():
                            logging.warning("Worker thread did not terminate gracefully")
                    except Exception as e:
                        logging.error(f"Error stopping worker thread: {e}")
                self._clear_queues()
                logging.info("GUIWorker thread stopped")
    
    def add_task(self, task: Callable, callback: Callable[[Any], None], *args, **kwargs) -> None:
        """Add a task to the queue.
        
        Args:
            task: The function to execute in the background
            callback: Function to call with the result
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
        
        Raises:
            ValueError: If the worker is not running
            Queue.Full: If the task queue is full
        """
        if not self.running:
            raise ValueError("Worker is not running")
        try:
            self.task_queue.put((task, callback, args, kwargs), timeout=1.0)
            logging.debug(f"Added task {task.__name__} to queue")
        except Full:
            raise Full("Task queue is full")
    
    def _process_queue(self) -> None:
        """Process tasks from the queue."""
        while self.running:
            try:
                task, callback, args, kwargs = self.task_queue.get(timeout=0.1)
                self._current_task = task
                try:
                    if not self.running:
                        raise CancelledException("Task cancelled - worker stopping")
                    result = task(*args, **kwargs)
                    self.result_queue.put((callback, result))
                    logging.debug(f"Task {task.__name__} completed successfully")
                except Exception as e:
                    logging.error(f"Error in task {task.__name__}: {str(e)}")
                    self.result_queue.put((callback, e))
                finally:
                    self._current_task = None
                    self.task_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logging.error(f"Unexpected error in worker thread: {str(e)}")

    def process_results(self, root: tk.Tk) -> None:
        """Process any available results.
        
        Args:
            root: The tkinter root window
        """
        try:
            while True:
                callback, result = self.result_queue.get_nowait()
                try:
                    if isinstance(result, Exception):
                        callback(None, error=str(result))
                    else:
                        callback(result)
                except Exception as e:
                    logging.error(f"Error in result callback: {str(e)}")
                finally:
                    self.result_queue.task_done()
        except Empty:
            if self.running:
                root.after(100, lambda: self.process_results(root))
    
    def _clear_queues(self) -> None:
        """Clear all pending tasks and results."""
        try:
            while True:
                self.task_queue.get_nowait()
                self.task_queue.task_done()
        except Empty:
            pass
        
        try:
            while True:
                self.result_queue.get_nowait()
                self.result_queue.task_done()
        except Empty:
            pass