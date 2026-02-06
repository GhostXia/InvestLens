import json
import os
import logging
from typing import List, Dict, Any
# pyre-ignore[21]: pydantic installed but not found
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Use absolute path to config directory
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config")
SOURCES_FILE = "sources.json"

class DataSourceConfig(BaseModel):
    name: str
    provider_type: str # "alpha_vantage", "yfinance" (built-in fallback, not really editable but listed?)
    api_key: str = ""
    endpoint_override: str = ""
    enabled: bool = True

class ConfigManager:
    """
    Manages loading and saving of dynamic configuration.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._ensure_config_dir()
        return cls._instance

    def _ensure_config_dir(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        # Create default sources if file doesn't exist
        file_path = os.path.join(CONFIG_DIR, SOURCES_FILE)
        if not os.path.exists(file_path):
            self.save_data_sources([])

    def load_data_sources(self) -> List[Dict[str, Any]]:
        file_path = os.path.join(CONFIG_DIR, SOURCES_FILE)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            logger.error(f"Failed to load sources: {e}")
            return []

    def save_data_sources(self, sources: List[Dict[str, Any]]):
        file_path = os.path.join(CONFIG_DIR, SOURCES_FILE)
        try:
            with open(file_path, 'w') as f:
                json.dump(sources, f, indent=4)
            logger.info("Data sources saved.")
        except Exception as e:
            logger.error(f"Failed to save sources: {e}")

config_manager = ConfigManager()
