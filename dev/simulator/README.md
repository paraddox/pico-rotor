# Pico Rotor Simulator

A simulation environment that runs the actual pico-rotor MicroPython firmware on Linux with mocked hardware and visual display of antenna movement.

## Purpose

- Test firmware logic without physical hardware
- Debug control algorithms and web interface
- Rapid development iteration
- Demonstration and training

## Requirements

- Python 3.8+
- Rich library (optional, for terminal display)

```bash
pip install rich
```

## Quick Start

From the project root directory:

```bash
# Run with default settings
python dev/simulator/run.py

# Start at different position
python dev/simulator/run.py --start-az=90 --start-el=30

# Run 5x faster for quick testing
python dev/simulator/run.py --speed-mult=5

# Headless mode (no terminal display)
python dev/simulator/run.py --no-display
```

## Accessing the Simulated System

Once running:

- **Web Interface:** http://127.0.0.1:80/
- **Settings Page:** http://127.0.0.1:80/settings
- **rotctld Protocol:** Port 4533

Test with netcat:
```bash
# Get current position
echo "p" | nc 127.0.0.1 4533

# Move to az=270, el=60
echo "P 270 60" | nc 127.0.0.1 4533

# Stop movement
echo "S" | nc 127.0.0.1 4533
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--start-az=DEGREES` | Initial azimuth position | 180 |
| `--start-el=DEGREES` | Initial elevation position | 45 |
| `--speed-mult=MULT` | Speed multiplier for testing | 1.0 |
| `--no-display` | Disable terminal display | off |

## Architecture

```
dev/simulator/
├── run.py              # Entry point - sets up mocks and runs firmware
├── mocks/              # MicroPython hardware mocks
│   ├── machine.py      # Pin, PWM, ADC, reset()
│   ├── network.py      # WLAN, STA_IF, AP_IF
│   └── uasyncio.py     # Wraps asyncio + sleep_ms()
├── physics/
│   ├── state.py        # SimulatorState singleton (shared state)
│   └── antenna.py      # Physics engine (motor→position)
└── display/
    └── terminal.py     # Rich-based terminal UI
```

### How It Works

1. **Mock Injection:** The mocks directory is prepended to `sys.path` before any firmware imports. When firmware does `import machine`, it gets our mock instead of the real MicroPython module.

2. **Shared State:** All mocks read/write to a thread-safe `SimulatorState` singleton. PWM commands from the motor module update the state, which the physics engine reads.

3. **Physics Engine:** Runs at 50Hz, converting PWM duty cycles to angular velocities, then integrating to update positions. Includes momentum smoothing for realistic movement.

4. **ADC Simulation:** When firmware reads ADC values, the mock converts the simulated position back to voltage (with calibration) and adds Gaussian noise.

5. **Display:** Rich library renders a live terminal display at 10Hz showing position, velocities, motor states, and network status.

## Physics Model

**Motor Speed Mapping:**
- Below PWM 19660: Motor stopped (below minimum effective duty)
- PWM 19660-65535: Linear velocity mapping
- Max azimuth speed: 6°/s
- Max elevation speed: 4°/s

**Position Integration:**
- 50Hz update rate
- Momentum factor (0.3) smooths velocity changes
- Positions clamped to calibration limits

**ADC Noise:**
- Gaussian noise with 5mV standard deviation
- Simulates real potentiometer readings

## Troubleshooting

**"Rich library not available"**
```bash
pip install rich
```
Or run with `--no-display` for headless mode.

**Port 80 requires root**

On Linux, binding to port 80 requires elevated privileges. Either:
- Run with sudo: `sudo python dev/simulator/run.py`
- Or modify firmware's `settings.json` to use port 8080

**Address already in use**

Another process is using port 80 or 4533. Either stop that process or modify the ports in `settings.json`.

## Limitations

- WiFi connection always succeeds instantly
- No network latency simulation
- Timer callbacks not fully implemented
- Single-threaded async (no true parallelism)
