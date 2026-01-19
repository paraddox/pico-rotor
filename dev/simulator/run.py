#!/usr/bin/env python3
"""
Pico Rotor Simulator
====================

Runs the actual pico-rotor MicroPython firmware on Linux with mocked
hardware and visual display of antenna movement.

Usage:
    python dev/simulator/run.py [options]

Options:
    --start-az=DEGREES   Initial azimuth position (default: 180)
    --start-el=DEGREES   Initial elevation position (default: 45)
    --speed-mult=MULT    Speed multiplier for testing (default: 1.0)
    --no-display         Disable terminal display (headless mode)

Examples:
    python dev/simulator/run.py
    python dev/simulator/run.py --start-az=90 --start-el=30
    python dev/simulator/run.py --speed-mult=5
    python dev/simulator/run.py --no-display
"""

import sys
import os
import argparse

# Get paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SIMULATOR_ROOT = SCRIPT_DIR
MOCKS_DIR = os.path.join(SIMULATOR_ROOT, "mocks")
FIRMWARE_ROOT = os.path.dirname(os.path.dirname(SIMULATOR_ROOT))

# CRITICAL: Prepend mocks directory to sys.path BEFORE any firmware imports
# This ensures firmware 'import machine' gets our mock instead of real module
sys.path.insert(0, MOCKS_DIR)
sys.path.insert(0, SIMULATOR_ROOT)
sys.path.insert(0, FIRMWARE_ROOT)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the Pico Rotor firmware in simulation mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                         Run with default settings
  %(prog)s --start-az=90           Start facing East
  %(prog)s --speed-mult=5          5x faster movement for testing
  %(prog)s --no-display            Run without terminal display

After starting:
  - Web interface: http://127.0.0.1:80/
  - rotctld:       nc 127.0.0.1 4533
"""
    )

    parser.add_argument(
        "--start-az",
        type=float,
        default=180.0,
        metavar="DEGREES",
        help="Initial azimuth position (0-360, default: 180)"
    )

    parser.add_argument(
        "--start-el",
        type=float,
        default=45.0,
        metavar="DEGREES",
        help="Initial elevation position (0-90, default: 45)"
    )

    parser.add_argument(
        "--speed-mult",
        type=float,
        default=1.0,
        metavar="MULT",
        help="Speed multiplier for faster testing (default: 1.0)"
    )

    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Disable terminal display (headless mode)"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    print("=" * 50)
    print("  Pico Rotor Simulator")
    print("=" * 50)
    print(f"  Starting position: AZ={args.start_az}° EL={args.start_el}°")
    print(f"  Speed multiplier:  {args.speed_mult}x")
    print(f"  Display:           {'disabled' if args.no_display else 'enabled'}")
    print("=" * 50)
    print()

    # Initialize simulator state
    from physics.state import state
    state.reset(
        start_az=args.start_az,
        start_el=args.start_el,
        speed_mult=args.speed_mult
    )

    # Initialize physics engine
    from physics.antenna import physics

    # Initialize display (optional)
    from display.terminal import display
    if args.no_display:
        display.disable()

    # Run everything with asyncio
    import asyncio

    async def run_simulation():
        """Run the complete simulation."""
        # Start physics engine
        physics.start()

        # Start display
        if not args.no_display:
            display.start()

        # Change to firmware directory so settings.json is found
        original_dir = os.getcwd()
        os.chdir(FIRMWARE_ROOT)

        try:
            # Import and run the firmware main module
            # This import triggers all the firmware initialization
            print("[SIMULATOR] Loading firmware...")
            import main as firmware_main

            # The firmware's main() is async, so we await it
            await firmware_main.main()

        except KeyboardInterrupt:
            print("\n[SIMULATOR] Shutdown requested")
        except Exception as e:
            print(f"\n[SIMULATOR] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            os.chdir(original_dir)
            physics.stop()
            display.stop()

    try:
        asyncio.run(run_simulation())
    except KeyboardInterrupt:
        print("\n[SIMULATOR] Goodbye!")


if __name__ == "__main__":
    main()
