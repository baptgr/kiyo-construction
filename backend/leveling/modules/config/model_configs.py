from typing import Dict, Any, List
from .prompts import CONSTRUCTION_AGENT_INSTRUCTIONS

# Default configurations
DEFAULT_CONFIG = {
    "configurable": {
        "model": "gpt-4o",
        "system_instructions": CONSTRUCTION_AGENT_INSTRUCTIONS
    }
}

# Predefined configurations
CONFIGS = {
    "default": DEFAULT_CONFIG,
    
    "gpt-4.1-standard": {
        "configurable": {
            "model": "gpt-4.1",
            "system_instructions": CONSTRUCTION_AGENT_INSTRUCTIONS
        }
    },
    
    "o3-standard": {
        "configurable": {
            "model": "o3",
            "system_instructions": CONSTRUCTION_AGENT_INSTRUCTIONS
        }
    },

    "o4-mini-standard": {
        "configurable": {
            "model": "o4-mini",
            "system_instructions": CONSTRUCTION_AGENT_INSTRUCTIONS
        }
    },

    "o3-mini-standard": {
        "configurable": {
            "model": "o3-mini",
            "system_instructions": CONSTRUCTION_AGENT_INSTRUCTIONS
        }
    }
}

def get_config(config_name: str = "default") -> Dict[str, Any]:
    """Get a configuration by name.
    
    Args:
        config_name: Name of the configuration to retrieve
        
    Returns:
        The configuration dictionary with configurable parameters
    """
    return CONFIGS.get(config_name, DEFAULT_CONFIG)

def list_configs() -> Dict[str, Dict[str, Any]]:
    """Get a list of all available configurations.
    
    Returns:
        Dictionary of all named configurations
    """
    return CONFIGS

def get_config_names() -> List[str]:
    """Get a list of all available configuration names.
    
    Returns:
        List of configuration names
    """
    return list(CONFIGS.keys())