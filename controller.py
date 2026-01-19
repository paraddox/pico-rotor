# Rotor Controller Module
# =======================
# Integrates motors and position sensors with automatic positioning

import uasyncio as asyncio
from settings import settings
from motors import RotorMotors
from position import RotorPosition

class RotorState:
    """Enumeration of rotor states."""
    IDLE = "idle"
    MOVING_AZ = "moving_az"
    MOVING_EL = "moving_el"
    MOVING_BOTH = "moving_both"
    MANUAL_AZ_CW = "manual_az_cw"
    MANUAL_AZ_CCW = "manual_az_ccw"
    MANUAL_EL_UP = "manual_el_up"
    MANUAL_EL_DOWN = "manual_el_down"
    PARKING = "parking"


class RotorController:
    """Main rotor controller with automatic and manual positioning."""
    
    def __init__(self):
        self.motors = RotorMotors()
        self.position = RotorPosition()
        
        # Target positions
        self.target_az = None
        self.target_el = None
        
        # Current state
        self.state = RotorState.IDLE
        self.mode = "manual"  # "manual" or "auto"
        
        # Stop flag for interrupting movements
        self._stop_requested = False
        
        # Control loop task
        self._control_task = None
        
    def get_status(self) -> dict:
        """Get current rotor status."""
        az, el = self.position.get_position()
        az_v, el_v = self.position.get_voltages()
        return {
            "azimuth": az,
            "elevation": el,
            "az_voltage": round(az_v, 3),
            "el_voltage": round(el_v, 3),
            "target_az": self.target_az,
            "target_el": self.target_el,
            "state": self.state,
            "mode": self.mode
        }
    
    def stop(self):
        """Emergency stop - halt all movement immediately."""
        self._stop_requested = True
        self.motors.stop_all()
        self.target_az = None
        self.target_el = None
        self.state = RotorState.IDLE
        
    def set_mode(self, mode: str):
        """Set operating mode (manual/auto)."""
        if mode in ("manual", "auto"):
            self.mode = mode
            
    # -------------------------
    # Manual Control Methods
    # -------------------------
    
    def manual_az_cw(self):
        """Start manual azimuth clockwise rotation."""
        self._stop_requested = False
        self.target_az = None
        self.target_el = None
        self.state = RotorState.MANUAL_AZ_CW
        self.motors.az_cw(settings.get("pwm_fast", 65535))
        
    def manual_az_ccw(self):
        """Start manual azimuth counter-clockwise rotation."""
        self._stop_requested = False
        self.target_az = None
        self.target_el = None
        self.state = RotorState.MANUAL_AZ_CCW
        self.motors.az_ccw(settings.get("pwm_fast", 65535))
        
    def manual_el_up(self):
        """Start manual elevation up."""
        self._stop_requested = False
        self.target_az = None
        self.target_el = None
        self.state = RotorState.MANUAL_EL_UP
        self.motors.el_up(settings.get("pwm_fast", 65535))
        
    def manual_el_down(self):
        """Start manual elevation down."""
        self._stop_requested = False
        self.target_az = None
        self.target_el = None
        self.state = RotorState.MANUAL_EL_DOWN
        self.motors.el_down(settings.get("pwm_fast", 65535))
    
    # -------------------------
    # Automatic Positioning
    # -------------------------
    
    def set_target(self, az: float = None, el: float = None):
        """Set target position and start movement."""
        self._stop_requested = False
        
        # Validate and set targets
        if az is not None:
            az_min = settings.get("az_limit_min", 0.0)
            az_max = settings.get("az_limit_max", 360.0)
            az = max(az_min, min(az_max, az))
            self.target_az = az
            
        if el is not None:
            el_min = settings.get("el_limit_min", 0.0)
            el_max = settings.get("el_limit_max", 90.0)
            el = max(el_min, min(el_max, el))
            self.target_el = el
            
        # Update state
        if self.target_az is not None and self.target_el is not None:
            self.state = RotorState.MOVING_BOTH
        elif self.target_az is not None:
            self.state = RotorState.MOVING_AZ
        elif self.target_el is not None:
            self.state = RotorState.MOVING_EL
            
    def park(self):
        """Move to park position."""
        self.state = RotorState.PARKING
        park_az = settings.get("park_az", 0.0)
        park_el = settings.get("park_el", 0.0)
        self.set_target(park_az, park_el)
        
    def _calculate_speed(self, current: float, target: float) -> int:
        """Calculate PWM speed based on distance to target."""
        tolerance = settings.get("tolerance", 1.0)
        slow_threshold = settings.get("slow_threshold", 5.0)
        pwm_fast = settings.get("pwm_fast", 65535)
        pwm_slow = settings.get("pwm_slow", 32768)
        pwm_min = settings.get("pwm_min", 19660)
        
        distance = abs(target - current)
        
        if distance <= tolerance:
            return 0  # At target
        elif distance <= slow_threshold:
            # Proportional slow speed
            ratio = distance / slow_threshold
            speed = int(pwm_min + (pwm_slow - pwm_min) * ratio)
            return speed
        else:
            return pwm_fast
            
    async def control_loop(self):
        """Main control loop - runs continuously."""
        while True:
            update_ms = settings.get("position_update_ms", 50)
            
            if self._stop_requested:
                self.motors.stop_all()
                await asyncio.sleep_ms(update_ms)
                continue
                
            # Get current position
            current_az, current_el = self.position.get_position()
            tolerance = settings.get("tolerance", 1.0)
            
            # Control azimuth
            if self.target_az is not None:
                az_error = self.target_az - current_az
                
                if abs(az_error) <= tolerance:
                    self.motors.azimuth.stop()
                    self.target_az = None
                else:
                    speed = self._calculate_speed(current_az, self.target_az)
                    if az_error > 0:
                        self.motors.az_cw(speed)
                    else:
                        self.motors.az_ccw(speed)
                        
            # Control elevation
            if self.target_el is not None:
                el_error = self.target_el - current_el
                
                if abs(el_error) <= tolerance:
                    self.motors.elevation.stop()
                    self.target_el = None
                else:
                    speed = self._calculate_speed(current_el, self.target_el)
                    if el_error > 0:
                        self.motors.el_up(speed)
                    else:
                        self.motors.el_down(speed)
                        
            # Update state if both targets reached
            if self.target_az is None and self.target_el is None:
                if self.state in (RotorState.MOVING_AZ, RotorState.MOVING_EL, 
                                  RotorState.MOVING_BOTH, RotorState.PARKING):
                    self.state = RotorState.IDLE
                    
            await asyncio.sleep_ms(update_ms)
            
    def start_control_loop(self):
        """Start the control loop as an async task."""
        if self._control_task is None:
            self._control_task = asyncio.create_task(self.control_loop())
