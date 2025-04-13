"""Worker module for handling long-running GUI operations.

This module provides thread management for GUI operations to prevent freezing.
"""

from threading import Thread
from queue import Queue
from typing import Callable, Any, Dict
import tkinter as tk

class GUIWorker:
    """Worker class for handling long-running GUI operations in separate threads."""
    
    def __init__(self):
        """Initialize the worker with a task queue."""
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.running = False
    
    def start(self) -> None:
        """Start the worker thread."""
        if not self.running:
            self.running = True
            self.worker_thread = Thread(target=self._process_queue, daemon=True)
            self.worker_thread.start()
    
    def stop(self) -> None:
        """Stop the worker thread."""
        self.running = False
        if hasattr(self, 'worker_thread'):
            self.worker_thread.join()
    
    def add_task(self, task: Callable, callback: Callable[[Any], None], *args, **kwargs) -> None:
        """Add a task to the queue.
        
        Args:
            task: The function to execute in the background
            callback: Function to call with the result
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
        """
        self.task_queue.put((task, callback, args, kwargs))
    
    def _process_queue(self) -> None:
        """Process tasks from the queue."""
        while self.running:
            try:
                task, callback, args, kwargs = self.task_queue.get(timeout=0.1)
                try:
                    result = task(*args, **kwargs)
                    self.result_queue.put((callback, result))
                except Exception as e:
                    self.result_queue.put((callback, e))
            except queue.Empty:
                continue
    
    def process_results(self, root: tk.Tk) -> None:
        """Process any available results.
        
        Args:
            root: The tkinter root window
        """
        try:
            while True:
                callback, result = self.result_queue.get_nowait()
                if isinstance(result, Exception):
                    callback(None, error=str(result))
                else:
                    callback(result)
        except queue.Empty:
            if self.running:
                root.after(100, lambda: self.process_results(root))