# Terminal Display Module
# =======================
# Rich-based terminal UI for simulator visualization

import asyncio
import sys
import os

# Add parent directories for imports
_sim_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _sim_root not in sys.path:
    sys.path.insert(0, _sim_root)

from physics.state import state
from physics.antenna import physics

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[DISPLAY] Rich library not available - display disabled")
    print("[DISPLAY] Install with: pip install rich")


class TerminalDisplay:
    """
    Terminal-based display for the simulator using Rich library.
    Shows antenna position, motor states, and system status.
    """

    UPDATE_HZ = 10  # Display refresh rate

    def __init__(self):
        self._running = False
        self._task = None
        self._console = Console() if RICH_AVAILABLE else None
        self._live = None
        self._enabled = RICH_AVAILABLE

    def _create_compass(self, azimuth: float) -> str:
        """Create a simple ASCII compass showing azimuth direction."""
        # Compass directions
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        # Normalize to 0-360
        az = azimuth % 360
        # Find closest direction (each spans 45 degrees)
        idx = int((az + 22.5) / 45) % 8
        return directions[idx]

    def _create_position_bar(self, value: float, min_val: float, max_val: float,
                              width: int = 30) -> str:
        """Create an ASCII progress bar for position."""
        if max_val <= min_val:
            ratio = 0.5
        else:
            ratio = (value - min_val) / (max_val - min_val)
            ratio = max(0, min(1, ratio))

        filled = int(ratio * width)
        empty = width - filled
        return f"[{'=' * filled}{' ' * empty}]"

    def _get_motor_state_str(self) -> str:
        """Get motor state description."""
        pwm = state.get_all_pwm()
        if not pwm:
            return "Stopped"

        states = []
        az_a = pwm.get(2, 0)
        az_b = pwm.get(3, 0)
        el_a = pwm.get(4, 0)
        el_b = pwm.get(5, 0)

        if az_a > 0:
            pct = int(az_a / 655.35)
            states.append(f"AZ CW {pct}%")
        elif az_b > 0:
            pct = int(az_b / 655.35)
            states.append(f"AZ CCW {pct}%")

        if el_a > 0:
            pct = int(el_a / 655.35)
            states.append(f"EL UP {pct}%")
        elif el_b > 0:
            pct = int(el_b / 655.35)
            states.append(f"EL DOWN {pct}%")

        return ", ".join(states) if states else "Stopped"

    def _render_display(self) -> Panel:
        """Render the main display panel."""
        display_state = state.get_display_state()
        az = display_state["az"]
        el = display_state["el"]
        led = display_state["led"]
        ip = display_state["ip"]

        # Get velocities
        az_vel, el_vel = physics.get_velocities()

        # Create the main table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Label", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Extra", style="dim")

        # Position rows
        az_bar = self._create_position_bar(az, 0, 360)
        el_bar = self._create_position_bar(el, 0, 90)
        compass = self._create_compass(az)

        table.add_row(
            "Azimuth:",
            f"{az:6.1f}°",
            f"{az_bar} {compass}"
        )
        table.add_row(
            "Elevation:",
            f"{el:6.1f}°",
            f"{el_bar}"
        )

        # Velocity row
        vel_str = ""
        if abs(az_vel) > 0.1 or abs(el_vel) > 0.1:
            vel_str = f"AZ: {az_vel:+.1f}°/s  EL: {el_vel:+.1f}°/s"
        table.add_row("Velocity:", vel_str, "")

        # Motor state
        motor_state = self._get_motor_state_str()
        table.add_row("Motors:", motor_state, "")

        # LED state
        led_str = "[green]ON[/green]" if led else "[dim]OFF[/dim]"
        table.add_row("LED:", led_str, "")

        # Network
        if display_state["wifi"]:
            net_str = f"[green]WiFi[/green] {ip}"
        elif display_state["ap_mode"]:
            net_str = f"[yellow]AP Mode[/yellow] {ip}"
        else:
            net_str = "[dim]Disconnected[/dim]"
        table.add_row("Network:", net_str, "")

        # Create panel
        title = "[bold blue]Pico Rotor Simulator[/bold blue]"
        panel = Panel(
            table,
            title=title,
            subtitle="[dim]Ctrl+C to exit[/dim]",
            border_style="blue"
        )

        return panel

    async def _display_loop(self):
        """Main display update loop."""
        dt = 1.0 / self.UPDATE_HZ

        with Live(self._render_display(), console=self._console,
                  refresh_per_second=self.UPDATE_HZ, transient=True) as live:
            self._live = live
            while self._running:
                live.update(self._render_display())
                await asyncio.sleep(dt)

    def start(self):
        """Start the display."""
        if not self._enabled:
            return

        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._display_loop())
            print("[DISPLAY] Terminal display started")

    def stop(self):
        """Stop the display."""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

    def disable(self):
        """Disable the display (for headless mode)."""
        self._enabled = False


# Global display instance
display = TerminalDisplay()
