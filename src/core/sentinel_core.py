"""SentinelPC Core Module

This module serves as the central core component of the SentinelPC application,
managing and coordinating all optimization operations.
"""

import logging
from typing import Dict, Any, Optional, List
from queue import Queue, Empty
from .config_manager import ConfigManager
from .performance_optimizer import PerformanceOptimizer
from .environment_manager import EnvironmentManager
from .monitoring_manager import MonitoringManager
from .logging_manager import LoggingManager

class SentinelCore:
    """Core class managing all SentinelPC optimization operations."""
    
    def __init__(self):
        """Initialize SentinelCore with all required components."""
        self.logger = LoggingManager().get_logger(__name__)
        self.config = ConfigManager()
        self.optimizer = PerformanceOptimizer()
        self.env_manager = EnvironmentManager()
        self.monitoring = MonitoringManager()
        self.version = "1.0.0"
        self._message_queue = Queue()
    
    def initialize(self) -> bool:
        """Initialize all core components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing SentinelPC Core v%s", self.version)
            
            # Initialize components in order
            # Config is already loaded in __init__
            if not self.config.get_config():
                raise RuntimeError("Failed to load configuration")
                
            if not self.env_manager.initialize(self.config.get_config()):
                raise RuntimeError("Failed to initialize environment manager")
                
            if not self.optimizer.initialize(self.config.get_config()):
                raise RuntimeError("Failed to initialize performance optimizer")
                
            if not self.monitoring.initialize():
                raise RuntimeError("Failed to initialize monitoring manager")
                
            return True
            
        except Exception as e:
            self.logger.error("Failed to initialize SentinelPC Core: %s", str(e))
            return False
    
    def optimize_system(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """Run system optimization with optional profile.
        
        Args:
            profile: Optional profile name to use for optimization
        
        Returns:
            Dict containing optimization results
        """
        try:
            self.logger.info("Starting optimization%s",
                          f" with profile: {profile}" if profile else "")
            
            # Get system state before optimization
            initial_state = self.env_manager.get_system_state()
            initial_metrics = self.monitoring.get_system_metrics()
            
            # Run optimization
            optimization_result = self.optimizer.optimize_system(
                profile=profile if profile else self.config.get_default_profile()
            )
            
            # Get system state after optimization
            final_state = self.env_manager.get_system_state()
            final_metrics = self.monitoring.get_system_metrics()
            
            return {
                "success": True,
                "initial_state": initial_state,
                "initial_metrics": initial_metrics,
                "final_state": final_state,
                "final_metrics": final_metrics,
                "optimizations": optimization_result
            }
            
        except Exception as e:
            self.logger.error("Optimization failed: %s", str(e))
            return {"success": False, "error": str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information and state.
        
        Returns:
            Dict containing system information
        """
        try:
            system_info = self.env_manager.get_system_info()
            system_metrics = self.monitoring.get_system_metrics()
            system_state = self.env_manager.get_system_state()
            
            return {
                "success": True,
                "system_info": system_info,
                "system_metrics": system_metrics,
                "system_state": system_state
            }
        except Exception as e:
            self.logger.error("Failed to get system info: %s", str(e))
            return {"success": False, "error": str(e)}
    
    def get_startup_programs(self) -> Dict[str, Any]:
        """Get list of startup programs.
        
        Returns:
            Dict containing startup program information
        """
        try:
            return self.env_manager.get_startup_programs()
        except Exception as e:
            self.logger.error("Failed to get startup programs: %s", str(e))
            return {"success": False, "error": str(e)}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics.
        
        Returns:
            Dict containing system metrics
        """
        try:
            metrics = self.monitoring.get_system_metrics()
            history = self.monitoring.get_performance_history()
            return {
                "success": True,
                "current_metrics": metrics,
                "history": history
            }
        except Exception as e:
            self.logger.error("Failed to get system metrics: %s", str(e))
            return {"success": False, "error": str(e)}
    
    def update_config(self, config_updates: Dict[str, Any]) -> bool:
        """Update configuration settings.
        
        Args:
            config_updates: Dictionary of configuration updates
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if self.config.update_config(config_updates):
                # Reinitialize components with new config
                self.optimizer.initialize(self.config.get_config())
                self.env_manager.initialize(self.config.get_config())
                return True
            return False
        except Exception as e:
            self.logger.error("Failed to update config: %s", str(e))
            return False
    
    def shutdown(self) -> None:
        """Clean shutdown of core components."""
        try:
            self.logger.info("Shutting down SentinelPC Core")
            self.optimizer.cleanup()
            self.env_manager.cleanup()
            self.config.save_config()
        except Exception as e:
            self.logger.error("Error during shutdown: %s", str(e))