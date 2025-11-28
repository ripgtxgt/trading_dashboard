#!/usr/bin/env python3
"""
Test Mode Configuration Module
Manages test/live trading mode switching and configuration
"""

import os
import json
from pathlib import Path

# Configuration file path
CONFIG_FILE = Path(__file__).parent.parent / 'test_mode_config.json'

# Default configuration
DEFAULT_CONFIG = {
    'enabled': False,  # Test mode disabled by default (live trading)
    'initial_balance': 10.0,  # Initial balance for test mode (USDT)
    'leverage': 10,  # Leverage multiplier
    'slippage': 0.001,  # 0.1% slippage simulation
    'fee_rate': 0.0006,  # 0.06% trading fee (KuCoin taker fee)
}


class TestModeConfig:
    """Test mode configuration manager"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    return {**DEFAULT_CONFIG, **config}
            except Exception as e:
                print(f"[Test Mode] Failed to load config: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[Test Mode] Failed to save config: {e}")
    
    def is_enabled(self):
        """Check if test mode is enabled"""
        return self.config.get('enabled', False)
    
    def enable(self):
        """Enable test mode"""
        self.config['enabled'] = True
        self._save_config()
        print("[Test Mode] Test mode ENABLED")
    
    def disable(self):
        """Disable test mode (switch to live trading)"""
        self.config['enabled'] = False
        self._save_config()
        print("[Test Mode] Test mode DISABLED (Live trading)")
    
    def get_config(self):
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, **kwargs):
        """Update configuration"""
        for key, value in kwargs.items():
            if key in DEFAULT_CONFIG:
                self.config[key] = value
        self._save_config()
        print(f"[Test Mode] Config updated: {kwargs}")
    
    def reset(self):
        """Reset to default configuration"""
        self.config = DEFAULT_CONFIG.copy()
        self._save_config()
        print("[Test Mode] Config reset to default")


# Global instance
_test_config = None


def get_test_config():
    """Get global test mode configuration instance"""
    global _test_config
    if _test_config is None:
        _test_config = TestModeConfig()
    return _test_config


def is_test_mode():
    """Quick check if test mode is enabled"""
    return get_test_config().is_enabled()


# CLI interface
if __name__ == "__main__":
    import sys
    
    config = get_test_config()
    
    if len(sys.argv) < 2:
        print("Test Mode Configuration")
        print("=" * 50)
        print(f"Status: {'ENABLED (Test)' if config.is_enabled() else 'DISABLED (Live)'}")
        print(f"Config: {json.dumps(config.get_config(), indent=2)}")
        print("\nUsage:")
        print("  python test_mode.py enable   - Enable test mode")
        print("  python test_mode.py disable  - Disable test mode (live trading)")
        print("  python test_mode.py status   - Show current status")
        print("  python test_mode.py reset    - Reset to default config")
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == 'enable':
        config.enable()
    elif command == 'disable':
        config.disable()
    elif command == 'status':
        print(json.dumps({
            'enabled': config.is_enabled(),
            'mode': 'test' if config.is_enabled() else 'live',
            'config': config.get_config()
        }, indent=2))
    elif command == 'reset':
        config.reset()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
