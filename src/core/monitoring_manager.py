"""Monitoring manager for SentinelPC.

This module handles system monitoring, health checks, and performance tracking.
"""

import logging
import psutil
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SystemMetrics:
    """Container for system performance metrics."""
    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    network_io: Dict[str, int]
    timestamp: datetime

class MonitoringManager:
    """Manages system monitoring and performance tracking."""
    
    def __init__(self, metrics_history_size: int = 100):
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[SystemMetrics] = []
        self.metrics_history_size = metrics_history_size
        self.health_status = "healthy"
        self._initialize_monitoring()
    
    def _initialize_monitoring(self) -> None:
        """Initialize monitoring system."""
        try:
            self.logger.info("Initializing system monitoring")
            # Initial metrics collection to verify functionality
            self.collect_metrics()
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring: {e}")
            self.health_status = "error"
    
    def collect_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics.
        
        Returns:
            SystemMetrics: Current system metrics if successful, None otherwise
        """
        try:
            # Collect CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Collect memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Collect disk usage for all mounted partitions
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = usage.percent
                except Exception as e:
                    self.logger.warning(f"Failed to get disk usage for {partition.mountpoint}: {e}")
            
            # Collect network I/O statistics
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
            
            # Create metrics object
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage=disk_usage,
                network_io=network_io,
                timestamp=datetime.now()
            )
            
            # Add to history and maintain size limit
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.metrics_history_size:
                self.metrics_history.pop(0)
            
            self._update_health_status(metrics)
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return None
    
    def _update_health_status(self, metrics: SystemMetrics) -> None:
        """Update system health status based on metrics.
        
        Args:
            metrics: Current system metrics
        """
        try:
            # Define thresholds for health status
            cpu_threshold = 90.0
            memory_threshold = 90.0
            disk_threshold = 90.0
            
            # Check CPU usage
            if metrics.cpu_percent > cpu_threshold:
                self.health_status = "warning"
                self.logger.warning(f"High CPU usage: {metrics.cpu_percent}%")
            
            # Check memory usage
            if metrics.memory_percent > memory_threshold:
                self.health_status = "warning"
                self.logger.warning(f"High memory usage: {metrics.memory_percent}%")
            
            # Check disk usage
            for mount_point, usage in metrics.disk_usage.items():
                if usage > disk_threshold:
                    self.health_status = "warning"
                    self.logger.warning(f"High disk usage on {mount_point}: {usage}%")
            
            # If no warnings, set status to healthy
            if self.health_status != "warning":
                self.health_status = "healthy"
                
        except Exception as e:
            self.logger.error(f"Failed to update health status: {e}")
            self.health_status = "error"
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics.
        
        Returns:
            SystemMetrics: Most recent metrics if available, None otherwise
        """
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self) -> List[SystemMetrics]:
        """Get historical metrics data.
        
        Returns:
            List[SystemMetrics]: List of historical metrics
        """
        return self.metrics_history
    
    def get_health_status(self) -> str:
        """Get current system health status.
        
        Returns:
            str: Current health status (healthy, warning, or error)
        """
        return self.health_status
    
    def get_performance_summary(self) -> Dict[str, float]:
        """Get summary of system performance metrics.
        
        Returns:
            Dict[str, float]: Summary of average performance metrics
        """
        if not self.metrics_history:
            return {}
        
        try:
            # Calculate averages from history
            cpu_avg = sum(m.cpu_percent for m in self.metrics_history) / len(self.metrics_history)
            memory_avg = sum(m.memory_percent for m in self.metrics_history) / len(self.metrics_history)
            
            return {
                'avg_cpu_usage': round(cpu_avg, 2),
                'avg_memory_usage': round(memory_avg, 2)
            }
        except Exception as e:
            self.logger.error(f"Failed to generate performance summary: {e}")
            return {}