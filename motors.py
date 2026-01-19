# Motor Control Module with PWM
# =============================

from machine import Pin, PWM
from settings import settings

class Motor:
    """H-Bridge DC motor controller with PWM speed control."""
    
    def __init__(self, pin_a: int, pin_b: int, name: str = "motor"):
        self.name = name
        self.pwm_a = PWM(Pin(pin_a))
        self.pwm_b = PWM(Pin(pin_b))
        self._update_freq()
        self.stop()
        
    def _update_freq(self):
        """Update PWM frequency from settings."""
        freq = settings.get("pwm_freq", 1000)
        self.pwm_a.freq(freq)
        self.pwm_b.freq(freq)
        
    def stop(self):
        """Stop the motor (brake)."""
        self.pwm_a.duty_u16(0)
        self.pwm_b.duty_u16(0)
        
    def forward(self, speed: int = None):
        """Run motor forward at specified PWM duty cycle."""
        if speed is None:
            speed = settings.get("pwm_fast", 65535)
        speed = self._clamp_speed(speed)
        self.pwm_b.duty_u16(0)
        self.pwm_a.duty_u16(speed)
        
    def reverse(self, speed: int = None):
        """Run motor in reverse at specified PWM duty cycle."""
        if speed is None:
            speed = settings.get("pwm_fast", 65535)
        speed = self._clamp_speed(speed)
        self.pwm_a.duty_u16(0)
        self.pwm_b.duty_u16(speed)
        
    def _clamp_speed(self, speed: int) -> int:
        """Clamp speed to valid PWM range."""
        pwm_min = settings.get("pwm_min", 19660)
        if speed < pwm_min:
            return 0  # Below minimum effective, just stop
        return min(speed, 65535)


class RotorMotors:
    """Manages both azimuth and elevation motors."""
    
    def __init__(self):
        az_a = settings.get("az_pin_a", 2)
        az_b = settings.get("az_pin_b", 3)
        el_a = settings.get("el_pin_a", 4)
        el_b = settings.get("el_pin_b", 5)
        
        self.azimuth = Motor(az_a, az_b, "azimuth")
        self.elevation = Motor(el_a, el_b, "elevation")
        
    def stop_all(self):
        """Emergency stop both motors."""
        self.azimuth.stop()
        self.elevation.stop()
        
    def az_cw(self, speed: int = None):
        """Rotate azimuth clockwise (increasing degrees)."""
        self.azimuth.forward(speed)
        
    def az_ccw(self, speed: int = None):
        """Rotate azimuth counter-clockwise (decreasing degrees)."""
        self.azimuth.reverse(speed)
        
    def el_up(self, speed: int = None):
        """Raise elevation (increasing degrees)."""
        self.elevation.forward(speed)
        
    def el_down(self, speed: int = None):
        """Lower elevation (decreasing degrees)."""
        self.elevation.reverse(speed)
