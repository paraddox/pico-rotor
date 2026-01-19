# Simulator State - Thread-safe shared state singleton
# ====================================================

import threading
import random
from typing import Dict, Optional

class SimulatorState:
    """
    Thread-safe singleton holding all simulated hardware state.
    All mock hardware components read/write to this shared state.
    """

    _instance: Optional['SimulatorState'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._state_lock = threading.RLock()

        # Antenna position (degrees)
        self._az_position = 180.0
        self._el_position = 45.0

        # Motor PWM duty cycles per pin (0-65535)
        self._pwm_duty: Dict[int, int] = {}

        # Pin states (for LED, etc.)
        self._pin_states: Dict[str, int] = {
            "LED": 0
        }

        # WiFi state
        self._wifi_connected = False
        self._wifi_ip = "127.0.0.1"
        self._ap_mode = False
        self._ap_ip = "192.168.4.1"

        # Calibration values (from settings.py defaults)
        self._az_v_min = 0.54
        self._az_v_max = 2.32
        self._az_deg_min = 0.0
        self._az_deg_max = 360.0

        self._el_v_min = 0.53
        self._el_v_max = 0.98
        self._el_deg_min = 0.0
        self._el_deg_max = 90.0

        self._adc_vref = 3.3
        self._adc_noise_mv = 5.0  # Gaussian noise stddev in mV

        # ADC pin mapping
        self._az_adc_pin = 26
        self._el_adc_pin = 27

        # Speed multiplier for faster testing
        self._speed_mult = 1.0

        self._initialized = True

    def reset(self, start_az: float = 180.0, start_el: float = 45.0,
              speed_mult: float = 1.0):
        """Reset state with initial positions."""
        with self._state_lock:
            self._az_position = start_az
            self._el_position = start_el
            self._speed_mult = speed_mult
            self._pwm_duty.clear()
            self._pin_states["LED"] = 0
            self._wifi_connected = False
            self._ap_mode = False

    # Position accessors
    @property
    def az_position(self) -> float:
        with self._state_lock:
            return self._az_position

    @az_position.setter
    def az_position(self, value: float):
        with self._state_lock:
            self._az_position = max(self._az_deg_min,
                                     min(self._az_deg_max, value))

    @property
    def el_position(self) -> float:
        with self._state_lock:
            return self._el_position

    @el_position.setter
    def el_position(self, value: float):
        with self._state_lock:
            self._el_position = max(self._el_deg_min,
                                     min(self._el_deg_max, value))

    @property
    def speed_mult(self) -> float:
        with self._state_lock:
            return self._speed_mult

    # PWM duty cycle management
    def set_pwm_duty(self, pin: int, duty: int):
        """Set PWM duty cycle for a pin (0-65535)."""
        with self._state_lock:
            self._pwm_duty[pin] = max(0, min(65535, duty))

    def get_pwm_duty(self, pin: int) -> int:
        """Get PWM duty cycle for a pin."""
        with self._state_lock:
            return self._pwm_duty.get(pin, 0)

    def get_all_pwm(self) -> Dict[int, int]:
        """Get all non-zero PWM states."""
        with self._state_lock:
            return {k: v for k, v in self._pwm_duty.items() if v > 0}

    # Pin state management
    def set_pin(self, pin: str, value: int):
        """Set digital pin state."""
        with self._state_lock:
            self._pin_states[pin] = value

    def get_pin(self, pin: str) -> int:
        """Get digital pin state."""
        with self._state_lock:
            return self._pin_states.get(pin, 0)

    def toggle_pin(self, pin: str):
        """Toggle digital pin state."""
        with self._state_lock:
            current = self._pin_states.get(pin, 0)
            self._pin_states[pin] = 0 if current else 1

    @property
    def led_on(self) -> bool:
        """Check if LED is on."""
        return self.get_pin("LED") == 1

    # ADC simulation
    def read_adc(self, pin: int) -> int:
        """
        Read simulated ADC value (0-65535) for a pin.
        Converts position to voltage to ADC with noise.
        """
        with self._state_lock:
            if pin == self._az_adc_pin:
                position = self._az_position
                v_min, v_max = self._az_v_min, self._az_v_max
                deg_min, deg_max = self._az_deg_min, self._az_deg_max
            elif pin == self._el_adc_pin:
                position = self._el_position
                v_min, v_max = self._el_v_min, self._el_v_max
                deg_min, deg_max = self._el_deg_min, self._el_deg_max
            else:
                # Unknown pin - return mid-scale with noise
                return 32768 + int(random.gauss(0, 100))

            # Convert position to voltage
            deg_range = deg_max - deg_min
            if deg_range == 0:
                voltage = v_min
            else:
                ratio = (position - deg_min) / deg_range
                voltage = v_min + ratio * (v_max - v_min)

            # Add Gaussian noise
            noise_v = random.gauss(0, self._adc_noise_mv / 1000.0)
            voltage += noise_v

            # Clamp to valid voltage range
            voltage = max(0, min(self._adc_vref, voltage))

            # Convert to 16-bit ADC value
            adc_value = int((voltage / self._adc_vref) * 65535)
            return max(0, min(65535, adc_value))

    # WiFi state
    def set_wifi_connected(self, ip: str):
        """Mark WiFi as connected with given IP."""
        with self._state_lock:
            self._wifi_connected = True
            self._wifi_ip = ip
            self._ap_mode = False

    def set_ap_mode(self, ip: str = "192.168.4.1"):
        """Enable AP mode."""
        with self._state_lock:
            self._wifi_connected = False
            self._ap_mode = True
            self._ap_ip = ip

    @property
    def is_wifi_connected(self) -> bool:
        with self._state_lock:
            return self._wifi_connected

    @property
    def is_ap_mode(self) -> bool:
        with self._state_lock:
            return self._ap_mode

    @property
    def ip_address(self) -> str:
        with self._state_lock:
            if self._wifi_connected:
                return self._wifi_ip
            elif self._ap_mode:
                return self._ap_ip
            return "0.0.0.0"

    def get_display_state(self) -> dict:
        """Get state snapshot for display purposes."""
        with self._state_lock:
            return {
                "az": round(self._az_position, 1),
                "el": round(self._el_position, 1),
                "led": self._pin_states.get("LED", 0),
                "pwm": dict(self._pwm_duty),
                "wifi": self._wifi_connected,
                "ap_mode": self._ap_mode,
                "ip": self.ip_address
            }


# Global singleton instance
state = SimulatorState()
