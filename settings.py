# Settings Manager with JSON Persistence
# =======================================

import json
import os

# Default settings file path
SETTINGS_FILE = "settings.json"

# Default configuration values
DEFAULTS = {
    # Network
    "wifi_ssid": "YOUR_WIFI_SSID",
    "wifi_password": "YOUR_WIFI_PASSWORD",
    "web_port": 80,
    "rotctl_port": 4533,
    
    # Motor Pins
    "az_pin_a": 2,
    "az_pin_b": 3,
    "el_pin_a": 4,
    "el_pin_b": 5,
    
    # ADC Pins
    "az_adc_pin": 26,
    "el_adc_pin": 27,
    
    # Azimuth Calibration
    "az_v_min": 0.54,
    "az_v_max": 2.32,
    "az_deg_min": 0.0,
    "az_deg_max": 360.0,
    
    # Elevation Calibration
    "el_v_min": 0.53,
    "el_v_max": 0.98,
    "el_deg_min": 0.0,
    "el_deg_max": 90.0,
    
    # ADC Reference
    "adc_vref": 3.3,
    
    # PWM Settings
    "pwm_freq": 1000,
    "pwm_fast": 65535,
    "pwm_slow": 32768,
    "pwm_min": 19660,
    
    # Positioning
    "tolerance": 1.0,
    "slow_threshold": 5.0,
    "position_update_ms": 50,
    
    # Safety Limits
    "az_limit_min": 0.0,
    "az_limit_max": 360.0,
    "el_limit_min": 0.0,
    "el_limit_max": 90.0,
    
    # Park Position
    "park_az": 0.0,
    "park_el": 0.0,
}


class Settings:
    """Manages application settings with JSON persistence."""
    
    def __init__(self, filename: str = SETTINGS_FILE):
        self.filename = filename
        self._settings = {}
        self.load()
        
    def load(self):
        """Load settings from file, using defaults for missing values."""
        self._settings = DEFAULTS.copy()
        
        try:
            with open(self.filename, 'r') as f:
                saved = json.load(f)
                # Merge saved settings over defaults
                for key, value in saved.items():
                    if key in self._settings:
                        self._settings[key] = value
        except OSError:
            # File doesn't exist, use defaults
            print("[settings] No settings file, using defaults")
        except ValueError as e:
            # Invalid JSON
            print(f"[settings] Invalid settings file: {e}")
            
    def save(self):
        """Save current settings to file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self._settings, f)
            print("[settings] Settings saved")
            return True
        except Exception as e:
            print(f"[settings] Save failed: {e}")
            return False
            
    def get(self, key: str, default=None):
        """Get a setting value."""
        return self._settings.get(key, default)
        
    def set(self, key: str, value):
        """Set a setting value (does not auto-save)."""
        if key in DEFAULTS:
            # Type coercion based on default type
            default_type = type(DEFAULTS[key])
            try:
                if default_type == int:
                    value = int(value)
                elif default_type == float:
                    value = float(value)
                elif default_type == bool:
                    value = bool(value)
                else:
                    value = str(value)
            except (ValueError, TypeError):
                return False
                
            self._settings[key] = value
            return True
        return False
        
    def update(self, updates: dict):
        """Update multiple settings at once."""
        changed = False
        for key, value in updates.items():
            if self.set(key, value):
                changed = True
        return changed
        
    def get_all(self) -> dict:
        """Get all current settings."""
        return self._settings.copy()
        
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self._settings = DEFAULTS.copy()
        
    def export_as_config(self) -> str:
        """Export settings in config.py format for reference."""
        lines = ["# Generated Configuration", ""]
        for key, value in self._settings.items():
            const_name = key.upper()
            if isinstance(value, str):
                lines.append(f'{const_name} = "{value}"')
            else:
                lines.append(f'{const_name} = {value}')
        return "\n".join(lines)


# Global settings instance
settings = Settings()


# Compatibility layer - allows importing like config module
def __getattr__(name):
    """Allow attribute-style access for backwards compatibility."""
    key = name.lower()
    if key in DEFAULTS:
        return settings.get(key)
    raise AttributeError(f"No setting named {name}")
