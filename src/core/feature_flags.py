"""Feature Flags Module

This module implements a feature flag system for SentinelPC, allowing dynamic
feature enablement and A/B testing capabilities.
"""

from typing import Dict, Any, Optional
import json
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class FeatureState(Enum):
    """
    Enum representing possible states of a feature.

    Possible states include:
        - ENABLED: Feature is fully enabled.
        - DISABLED: Feature is disabled.
        - BETA: Feature is in beta testing.
        - ALPHA: Feature is in alpha testing.
    """

    ENABLED = "enabled"
    DISABLED = "disabled"
    BETA = "beta"
    ALPHA = "alpha"


@dataclass
class Feature:
    """Represents a feature with its configuration.

    Attributes:
        name: The name of the feature.
        state: The current state of the feature.
        description: A description of the feature.
        dependencies: A list of feature names that this feature depends on.
        config: A dictionary containing configuration settings.
    """

    name: str
    state: FeatureState
    description: str
    dependencies: list[str] = None
    config: Dict[str, Any] = None


class FeatureFlags:
    """Manages feature flags for the application."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the feature flags system.

        Args:
            config_path: Optional path to feature flags configuration file
        """
        self._features: Dict[str, Feature] = {}
        self._config_path = config_path or Path("config/features.json")
        self._load_features()

    def _load_features(self) -> None:
        """Load feature configurations from file."""
        if not self._config_path.exists():
            self._initialize_default_features()
            return

        try:
            with open(self._config_path, "r") as f:
                data = json.load(f)
                for name, config in data.items():
                    state = FeatureState(config.get("state", "disabled"))
                    desc = config.get("description", "")
                    deps = config.get("dependencies", [])
                    feat_config = config.get("config", {})

                    self._features[name] = Feature(
                        name=name,
                        state=state,
                        description=desc,
                        dependencies=deps,
                        config=feat_config,
                    )
        except Exception as e:
            print(f"Error loading feature flags: {e}")
            self._initialize_default_features()

    def _initialize_default_features(self) -> None:
        """Initialize default feature configurations."""
        self._features = {
            "ai_auto_tune": Feature(
                name="ai_auto_tune",
                state=FeatureState.BETA,
                description="AI-powered system optimization",
                config={"model_type": "light"},
            ),
            "cloud_sync": Feature(
                name="cloud_sync",
                state=FeatureState.ALPHA,
                description="Cloud synchronization of settings and profiles",
                config={"sync_interval": 3600},
            ),
            "real_time_stats": Feature(
                name="real_time_stats",
                state=FeatureState.ENABLED,
                description="Real-time system performance monitoring",
            ),
            "plugin_system": Feature(
                name="plugin_system",
                state=FeatureState.DISABLED,
                description="Plugin system for extending functionality",
            ),
        }
        self._save_features()

    def _save_features(self) -> None:
        """Save current feature configurations to file."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_path, "w") as f:
                json.dump(
                    {
                        name: {
                            "state": feature.state.value,
                            "description": feature.description,
                            "dependencies": feature.dependencies,
                            "config": feature.config,
                        }
                        for name, feature in self._features.items()
                    },
                    f,
                    indent=4,
                )
        except Exception as e:
            print(f"Error saving feature flags: {e}")

    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled.

        Args:
            feature_name: Name of the feature to check

        Returns:
            bool: True if feature is enabled or in beta/alpha
        """
        feature = self._features.get(feature_name)
        if not feature:
            return False
        return feature.state in [
            FeatureState.ENABLED,
            FeatureState.BETA,
            FeatureState.ALPHA,
        ]

    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """Get configuration for a specific feature.

        Args:
            feature_name: Name of the feature

        Returns:
            Dict containing feature configuration
        """
        feature = self._features.get(feature_name)
        return feature.config if feature else {}

    def set_feature_state(self, feature_name: str, state: FeatureState) -> bool:
        """Update the state of a feature.

        Args:
            feature_name: Name of the feature to update
            state: New state for the feature

        Returns:
            bool: True if update successful
        """
        if feature_name not in self._features:
            return False

        self._features[feature_name].state = state
        self._save_features()
        return True

    def get_all_features(self) -> Dict[str, Feature]:
        """Get all feature configurations.

        Returns:
            Dict containing all features and their configurations
        """
        return self._features.copy()
