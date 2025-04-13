"""SentinelPC Core Module

This module serves as the central core component of the SentinelPC application,
managing and coordinating all optimization operations.
"""

import logging
from typing import Dict, Any, Optional
from .config_manager import ConfigManager
from .performance_optimizer import PerformanceOptimizer
from .environment_manager import EnvironmentManager
from .logging_manager import LoggingManager

class SentinelCore:
    """Core class managing all SentinelPC optimization operations."""
    
    def __init__(self):
        """Initialize SentinelCore with all required components."""
        self.logger = LoggingManager().get_logger(__name__)
        self.config = ConfigManager()
        self.optimizer = PerformanceOptimizer()
        self.env_manager = EnvironmentManager()
        self.version = "1.0.0"
    
    def initialize(self) -> bool:
        """Initialize all core components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing SentinelPC Core v%s", self.version)
            self.config.load_config()
            self.env_manager.initialize()
            self.optimizer.initialize(self.config)
            return True
        except Exception as e:
            self.logger.error("Failed to initialize SentinelPC Core: %s", str(e))
            return False
    
    def run_optimization(self, profile: Optional[str] = None) -> Dict[str, Any]:
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
            
            # Run optimization
            optimization_result = self.optimizer.optimize(
                profile=profile if profile else self.config.get_default_profile()
            )
            
            # Get system state after optimization
            final_state = self.env_manager.get_system_state()
            
            return {
                "success": True,
                "initial_state": initial_state,
                "final_state": final_state,
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
            return self.env_manager.get_system_info()
        except Exception as e:
            self.logger.error("Failed to get system info: %s", str(e))
            return {"error": str(e)}
    
    def update_config(self, config_updates: Dict[str, Any]) -> bool:
        """Update configuration settings.
        
        Args:
            config_updates: Dictionary of configuration updates
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            self.config.update_config(config_updates)
            return True
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