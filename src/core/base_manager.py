"""Base interface definitions for SentinelPC manager classes.

This module defines the base interfaces that all manager classes must implement, ensuring consistent method signatures and behavior.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseManager(ABC):
    """
    Base interface for all manager classes.

    This abstract base class defines the common methods that all manager
    classes in SentinelPC should implement.
    """

    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the manager with optional configuration.

        Args:
            config: Optional configuration dictionary

        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up resources used by the manager.

        Returns:
            bool: True if cleanup successful, False otherwise
        """
        pass


class BaseEnvironmentManager(BaseManager):
    """
    Interface for environment management functionality.

    This abstract base class defines the methods for managing the system
    environment.
    """

    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information.

        Returns:
            Dict containing system information
        """
        pass

    @abstractmethod
    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state metrics.

        Returns:
            Dict containing system state information
        """
        pass


class BaseMonitoringManager(BaseManager):
    """
    Interface for system monitoring functionality.

    This abstract base class defines the methods for monitoring system
    performance and health.
    """

    @abstractmethod
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics.

        Returns:
            Dict containing system metrics
        """
        pass

    @abstractmethod
    def get_performance_history(self) -> Dict[str, Any]:
        """Get historical performance data.

        Returns:
            Dict containing performance history
        """
        pass


class BasePerformanceOptimizer(BaseManager):
    """
    Interface for performance optimization functionality.

    This abstract base class defines the methods for optimizing system
    performance.
    """

    @abstractmethod
    def optimize_system(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """Optimize system performance.

        Args:
            profile: Optional optimization profile to use

        Returns:
            Dict containing optimization results
        """
        pass

    @abstractmethod
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status.

        Returns:
            Dict containing optimization status
        """
        pass
