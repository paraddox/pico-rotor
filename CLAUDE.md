# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MicroPython firmware for Raspberry Pi Pico W that controls satellite antenna rotors with dual-axis (azimuth/elevation) support. Integrates with amateur radio software (GPredict, SDRConsole) via the Hamlib rotctld protocol.

## Deployment

No build step. Deploy directly to Pico W using mpremote:

```bash
# Install mpremote if needed
pip install mpremote

# Deploy all files to Pico
mpremote cp settings.py motors.py position.py controller.py rotctld.py webserver.py main.py :

# Or deploy a single file after changes
mpremote cp controller.py :

# Monitor serial output for debugging
mpremote connect
```

## Testing

No automated tests. Testing is hardware-based:
- Deploy to Pico W and verify via serial console output
- Test rotctld protocol: `echo "p" | nc <pico-ip> 4533`
- Test web interface at `http://<pico-ip>/`

## Architecture

Async-first design using `uasyncio` with three concurrent services:

```
main.py (startup, WiFi)
    ├── RotorController (controller.py) - state machine, control loop
    │       ├── Motors (motors.py) - PWM H-bridge control
    │       └── PositionSensor (position.py) - ADC potentiometer reading
    ├── RotctldServer (rotctld.py) - TCP server for Hamlib protocol
    └── WebServer (webserver.py) - HTTP API + embedded UI
```

**RotorController states:** IDLE, MOVING_AZ, MOVING_EL, MOVING_BOTH, MANUAL_*, PARKING

**Settings** (settings.py): JSON persistence with defaults, all hardware params configurable at runtime via `/settings` page.

## MicroPython Considerations

- Uses MicroPython-specific modules: `machine`, `network`, `uasyncio`
- No external dependencies - pure MicroPython stdlib
- Memory constrained - avoid large strings/buffers
- `webserver.py` contains embedded HTML/CSS/JS (855 lines) - the UI is inline, not separate files

## Key Patterns

- All modules use `[tag]` prefix logging (e.g., `[CTRL]`, `[MOTOR]`)
- Control loop runs at configurable interval (default 50ms)
- Speed ramping: proportional PWM based on distance to target
- WiFi resilience: falls back to AP mode "PicoRotor-Setup" if STA fails
