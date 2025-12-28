"""
Internationalization support
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional


class I18n:
    """Internationalization manager"""
    
    def __init__(self, locale: str = "zh"):
        self.locale = locale
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files"""
        i18n_dir = Path(__file__).parent.parent.parent / "i18n"
        
        for locale_file in ["zh.json", "en.json"]:
            file_path = i18n_dir / locale_file
            if file_path.exists():
                locale_key = locale_file.replace(".json", "")
                with open(file_path, "r", encoding="utf-8") as f:
                    self.translations[locale_key] = json.load(f)
    
    def t(self, key: str, **kwargs) -> str:
        """
        Translate key
        
        Args:
            key: Translation key (supports nested keys with dots)
            **kwargs: Formatting parameters
            
        Returns:
            Translated text
        """
        # Get translation dictionary for current language
        trans = self.translations.get(self.locale, {})
        
        # Support nested keys "section.key"
        keys = key.split(".")
        value = trans
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, key)
            else:
                return key
        
        # Return key itself if translation not found
        if not isinstance(value, str):
            return key
        
        # Format with parameters
        try:
            return value.format(**kwargs)
        except KeyError:
            return value
    
    def set_locale(self, locale: str):
        """Switch language"""
        if locale in self.translations:
            self.locale = locale


# Global instance
_i18n_instance: Optional[I18n] = None


def get_i18n(locale: str = "zh") -> I18n:
    """Get i18n instance"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(locale)
    return _i18n_instance
