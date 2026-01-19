# Mock machine module for MicroPython
# ====================================
# Simulates Pin, PWM, ADC hardware for Linux testing

import sys
import os

# Add parent directories to find physics module
_sim_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _sim_root not in sys.path:
    sys.path.insert(0, _sim_root)

from physics.state import state


class Pin:
    """Mock GPIO Pin class."""

    # Constants
    OUT = 1
    IN = 0
    PULL_UP = 1
    PULL_DOWN = 2

    def __init__(self, pin_id, mode=None, pull=None, value=None):
        """
        Initialize a pin.
        pin_id can be an int (GPIO number) or "LED" for onboard LED.
        """
        if isinstance(pin_id, str):
            self._pin_id = pin_id
        else:
            self._pin_id = str(pin_id)

        self._mode = mode or Pin.IN
        self._pull = pull

        if value is not None:
            state.set_pin(self._pin_id, value)

    def on(self):
        """Set pin high."""
        state.set_pin(self._pin_id, 1)

    def off(self):
        """Set pin low."""
        state.set_pin(self._pin_id, 0)

    def toggle(self):
        """Toggle pin state."""
        state.toggle_pin(self._pin_id)

    def value(self, val=None):
        """Get or set pin value."""
        if val is None:
            return state.get_pin(self._pin_id)
        else:
            state.set_pin(self._pin_id, val)

    def __repr__(self):
        return f"Pin({self._pin_id})"


class PWM:
    """Mock PWM controller class."""

    def __init__(self, pin):
        """Initialize PWM on a pin."""
        if isinstance(pin, Pin):
            self._pin_id = int(pin._pin_id) if pin._pin_id.isdigit() else pin._pin_id
        else:
            self._pin_id = pin

        self._freq = 1000
        self._duty = 0

    def freq(self, value=None):
        """Get or set PWM frequency."""
        if value is None:
            return self._freq
        self._freq = value

    def duty_u16(self, value=None):
        """Get or set PWM duty cycle (0-65535)."""
        if value is None:
            return self._duty
        self._duty = max(0, min(65535, value))
        # Update simulator state
        if isinstance(self._pin_id, int):
            state.set_pwm_duty(self._pin_id, self._duty)

    def deinit(self):
        """Disable PWM."""
        self._duty = 0
        if isinstance(self._pin_id, int):
            state.set_pwm_duty(self._pin_id, 0)

    def __repr__(self):
        return f"PWM(pin={self._pin_id}, freq={self._freq}, duty={self._duty})"


class ADC:
    """Mock ADC (Analog-to-Digital Converter) class."""

    def __init__(self, pin):
        """Initialize ADC on a pin."""
        if isinstance(pin, Pin):
            self._pin_id = int(pin._pin_id) if pin._pin_id.isdigit() else 0
        elif isinstance(pin, int):
            self._pin_id = pin
        else:
            self._pin_id = 0

    def read_u16(self) -> int:
        """Read 16-bit ADC value (0-65535)."""
        return state.read_adc(self._pin_id)

    def __repr__(self):
        return f"ADC(pin={self._pin_id})"


def reset():
    """Reset the microcontroller (exits simulation)."""
    print("[SIMULATOR] Reset requested - restarting simulation...")
    # In a real simulation, we might restart. For now, just exit.
    sys.exit(0)


def freq(value=None):
    """Get or set CPU frequency (no-op in simulator)."""
    if value is None:
        return 125_000_000  # Pico default
    # Setting frequency is a no-op in simulation
    return value


def unique_id():
    """Return a unique ID for this device."""
    return b'\x12\x34\x56\x78\x9a\xbc\xde\xf0'


# Timer class (basic implementation)
class Timer:
    """Mock Timer class."""

    ONE_SHOT = 0
    PERIODIC = 1

    def __init__(self, timer_id=-1):
        self._id = timer_id
        self._callback = None

    def init(self, mode=PERIODIC, freq=-1, period=-1, callback=None):
        """Initialize timer (mostly no-op in simulator)."""
        self._callback = callback

    def deinit(self):
        """Deinitialize timer."""
        self._callback = None


# WDT class (watchdog timer - no-op in simulator)
class WDT:
    """Mock Watchdog Timer class."""

    def __init__(self, timeout=8388):
        self._timeout = timeout

    def feed(self):
        """Feed the watchdog (no-op)."""
        pass
