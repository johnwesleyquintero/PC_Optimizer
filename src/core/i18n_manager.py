"""Internationalization manager for SentinelPC.

This module handles language localization and translation management for the application.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional


class I18nManager:
    """Manages internationalization and localization for SentinelPC."""

    def __init__(self, lang_dir: str = "locales"):
        self.logger = logging.getLogger(__name__)
        self.lang_dir = Path(lang_dir)
        self.current_lang = "en"  # Default language
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Load all available translation files."""
        try:
            if not self.lang_dir.exists():
                self.lang_dir.mkdir(parents=True)
                self.logger.info(f"Created language directory: {self.lang_dir}")

            for lang_file in self.lang_dir.glob("*.json"):
                lang_code = lang_file.stem
                try:
                    with open(lang_file, "r", encoding="utf-8") as f:
                        self.translations[lang_code] = json.load(f)
                    self.logger.debug(f"Loaded translations for {lang_code}")
                except json.JSONDecodeError:
                    self.logger.error(f"Failed to parse translation file: {lang_file}")
                except Exception as e:
                    self.logger.error(
                        f"Error loading translations for {lang_code}: {e}"
                    )
        except Exception as e:
            self.logger.error(f"Failed to initialize translations: {e}")
            self.translations["en"] = {}  # Fallback to empty English translations

    def set_language(self, lang_code: str) -> bool:
        """Set the current language for the application.

        Args:
            lang_code: The language code to set (e.g., 'en', 'es', 'fr')

        Returns:
            bool: True if language was set successfully, False otherwise
        """
        if lang_code in self.translations:
            self.current_lang = lang_code
            self.logger.info(f"Language set to: {lang_code}")
            return True
        self.logger.warning(
            f"Language {lang_code} not available, using {self.current_lang}"
        )
        return False

    def get_text(self, key: str, default: Optional[str] = None) -> str:
        """Get translated text for the given key.

        Args:
            key: The translation key to look up
            default: Default text to return if key is not found

        Returns:
            str: Translated text or default/key if not found
        """
        try:
            return self.translations[self.current_lang].get(key, default or key)
        except KeyError:
            self.logger.warning(f"Translation not found for key: {key}")
            return default or key

    def add_translation(self, lang_code: str, translations: Dict[str, str]) -> bool:
        """Add or update translations for a language.

        Args:
            lang_code: The language code to add/update
            translations: Dictionary of translation key-value pairs

        Returns:
            bool: True if translations were added successfully
        """
        try:
            lang_file = self.lang_dir / f"{lang_code}.json"
            with open(lang_file, "w", encoding="utf-8") as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            self.translations[lang_code] = translations
            self.logger.info(f"Added/updated translations for {lang_code}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add translations for {lang_code}: {e}")
            return False

    def get_available_languages(self) -> list:
        """Get list of available language codes.

        Returns:
            list: List of available language codes
        """
        return list(self.translations.keys())
