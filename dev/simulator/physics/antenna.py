# Antenna Physics Engine
# ======================
# Simulates motor-driven antenna movement with realistic physics

import asyncio
from .state import state


class AntennaPhysics:
    """
    Physics simulation for antenna rotor movement.

    Converts PWM motor signals into smooth antenna position changes
    with realistic acceleration and momentum.
    """

    # Default motor pin assignments (from settings.py)
    AZ_PIN_A = 2  # Azimuth forward (CW)
    AZ_PIN_B = 3  # Azimuth reverse (CCW)
    EL_PIN_A = 4  # Elevation up
    EL_PIN_B = 5  # Elevation down

    # PWM threshold - motors don't move below this
    PWM_MIN = 19660

    # Maximum angular velocities (degrees per second)
    MAX_AZ_SPEED = 6.0
    MAX_EL_SPEED = 4.0

    # Physics update rate
    UPDATE_HZ = 50

    # Momentum smoothing (0 = instant response, 1 = no response)
    MOMENTUM = 0.3

    def __init__(self):
        self._running = False
        self._task = None

        # Current velocities (degrees per second)
        self._az_velocity = 0.0
        self._el_velocity = 0.0

    def _pwm_to_velocity(self, duty: int, max_speed: float) -> float:
        """
        Convert PWM duty cycle to angular velocity.

        Args:
            duty: PWM duty cycle (0-65535)
            max_speed: Maximum speed in degrees/second

        Returns:
            Velocity in degrees/second (0 if below threshold)
        """
        if duty < self.PWM_MIN:
            return 0.0

        # Linear mapping from PWM_MIN-65535 to 0-max_speed
        pwm_range = 65535 - self.PWM_MIN
        ratio = (duty - self.PWM_MIN) / pwm_range
        return ratio * max_speed

    def _get_motor_velocity(self) -> tuple:
        """
        Calculate target velocities from current PWM states.

        Returns:
            (az_velocity, el_velocity) in degrees/second
        """
        # Get PWM duties for each motor channel
        az_a = state.get_pwm_duty(self.AZ_PIN_A)
        az_b = state.get_pwm_duty(self.AZ_PIN_B)
        el_a = state.get_pwm_duty(self.EL_PIN_A)
        el_b = state.get_pwm_duty(self.EL_PIN_B)

        # Azimuth: A = CW (increasing), B = CCW (decreasing)
        if az_a > az_b:
            az_vel = self._pwm_to_velocity(az_a, self.MAX_AZ_SPEED)
        elif az_b > az_a:
            az_vel = -self._pwm_to_velocity(az_b, self.MAX_AZ_SPEED)
        else:
            az_vel = 0.0

        # Elevation: A = Up (increasing), B = Down (decreasing)
        if el_a > el_b:
            el_vel = self._pwm_to_velocity(el_a, self.MAX_EL_SPEED)
        elif el_b > el_a:
            el_vel = -self._pwm_to_velocity(el_b, self.MAX_EL_SPEED)
        else:
            el_vel = 0.0

        return (az_vel, el_vel)

    async def _physics_loop(self):
        """Main physics update loop."""
        dt = 1.0 / self.UPDATE_HZ

        while self._running:
            # Get speed multiplier for faster testing
            speed_mult = state.speed_mult

            # Get target velocities from motor states
            target_az_vel, target_el_vel = self._get_motor_velocity()

            # Apply speed multiplier
            target_az_vel *= speed_mult
            target_el_vel *= speed_mult

            # Smooth velocity changes (momentum)
            self._az_velocity = (
                self._az_velocity * self.MOMENTUM +
                target_az_vel * (1 - self.MOMENTUM)
            )
            self._el_velocity = (
                self._el_velocity * self.MOMENTUM +
                target_el_vel * (1 - self.MOMENTUM)
            )

            # Stop completely if very slow and motor is off
            if abs(target_az_vel) < 0.1 and abs(self._az_velocity) < 0.1:
                self._az_velocity = 0.0
            if abs(target_el_vel) < 0.1 and abs(self._el_velocity) < 0.1:
                self._el_velocity = 0.0

            # Integrate position
            if self._az_velocity != 0:
                new_az = state.az_position + self._az_velocity * dt
                state.az_position = new_az

            if self._el_velocity != 0:
                new_el = state.el_position + self._el_velocity * dt
                state.el_position = new_el

            # Sleep until next update
            await asyncio.sleep(dt)

    def start(self):
        """Start the physics simulation."""
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._physics_loop())
            print("[PHYSICS] Antenna physics engine started")

    def stop(self):
        """Stop the physics simulation."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
            print("[PHYSICS] Antenna physics engine stopped")

    def get_velocities(self) -> tuple:
        """Get current velocities (az, el) in degrees/second."""
        return (self._az_velocity, self._el_velocity)


# Global physics engine instance
physics = AntennaPhysics()
