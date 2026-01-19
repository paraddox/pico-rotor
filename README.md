# Pico Rotor Controller

Satellite antenna rotor controller for Raspberry Pi Pico W with dual-axis (azimuth/elevation) support.

## Features

- **Hamlib rotctld Protocol** - TCP server compatible with GPredict, SDRConsole, and other amateur radio software
- **Web Interface** - Mobile-friendly control panel with real-time position display
- **Web-Based Settings** - Configure all parameters via browser (no code editing required)
- **PWM Speed Control** - Two-speed motor control for precision positioning
- **Dual Operating Modes** - Manual control and automatic tracking
- **Live Calibration** - Real-time voltage display for easy potentiometer calibration
- **AP Mode Fallback** - Creates WiFi hotspot if configured network unavailable

## Hardware Requirements

- Raspberry Pi Pico W
- H-Bridge motor driver (L298N, TB6612, or similar)
- Two DC motors (azimuth and elevation)
- Two potentiometers for position feedback
- 5V power supply (motor dependent)

## Wiring

### Motor Connections (H-Bridge)

| Function       | Pico Pin | H-Bridge |
|----------------|----------|----------|
| Azimuth A      | GP2      | IN1      |
| Azimuth B      | GP3      | IN2      |
| Elevation A    | GP4      | IN3      |
| Elevation B    | GP5      | IN4      |

### Position Sensors (Potentiometers)

| Function  | Pico Pin | Voltage Range      |
|-----------|----------|--------------------|
| Azimuth   | GP26     | 0.54V (0°) - 2.32V (360°) |
| Elevation | GP27     | 0.53V (0°) - 0.98V (90°)  |

## Installation

1. Install MicroPython on your Pico W (if not already installed):
   - Download from https://micropython.org/download/RPI_PICO_W/
   - Hold BOOTSEL button while connecting USB
   - Copy the .uf2 file to the mounted drive

2. Copy all `.py` files to the Pico:
   ```bash
   # Using mpremote (pip install mpremote)
   mpremote cp settings.py :
   mpremote cp motors.py :
   mpremote cp position.py :
   mpremote cp controller.py :
   mpremote cp rotctld.py :
   mpremote cp webserver.py :
   mpremote cp main.py :
   ```

3. Reset the Pico. On first boot:
   - If no WiFi configured, it creates AP "PicoRotor-Setup" (password: rotorsetup)
   - Connect to this network and visit http://192.168.4.1/settings
   - Configure your WiFi credentials and other settings
   - Click Save, then Reboot

4. The Pico will now connect to your WiFi and show its IP in the serial console.

## Web Settings

All parameters are configurable via the web interface at `http://<ip>/settings`:

### Network Settings
- WiFi SSID and password
- Web server port (default: 80)
- Rotctld port (default: 4533)

### GPIO Pins
- Motor control pins for azimuth and elevation
- ADC pins for position potentiometers

### Calibration
- Voltage-to-degree mapping for each axis
- Live voltage display helps with calibration
- Min/max degree ranges

### Motor Control
- PWM frequency (Hz)
- Fast speed, slow speed, minimum speed values
- ADC reference voltage

### Positioning
- Tolerance (stop accuracy in degrees)
- Slow threshold (when to switch to precision speed)
- Control loop update interval

### Limits & Park
- Azimuth and elevation travel limits
- Park position coordinates

## Usage

### Web Interface

Open `http://<pico-ip>/` in a browser. The interface provides:

- **Position Display** - Real-time azimuth and elevation readings
- **Direction Buttons** - Press and hold to move continuously
- **Go To Position** - Enter coordinates and click GO
- **Park Button** - Return to 0°, 0°
- **Emergency Stop** - Immediately halt all movement

### GPredict Configuration

1. Edit → Preferences → Interfaces → Rotators
2. Add new rotator:
   - **Name:** Pico Rotor
   - **Host:** <pico-ip>
   - **Port:** 4533
   - **Az Type:** 0° to 360°
   - **El Type:** 0° to 90°

### SDRConsole Configuration

Use the rotator tracking feature with:
- Protocol: Hamlib rotctld
- IP: <pico-ip>
- Port: 4533

### Command Line Testing

Test with netcat:
```bash
# Get position
echo "p" | nc <pico-ip> 4533

# Set position (az=180, el=45)
echo "P 180 45" | nc <pico-ip> 4533

# Stop
echo "S" | nc <pico-ip> 4533

# Park
echo "K" | nc <pico-ip> 4533
```

## rotctld Protocol Reference

| Command | Description | Response |
|---------|-------------|----------|
| `p` | Get position | `AZ\nEL` |
| `P az el` | Set position | `RPRT 0` |
| `S` | Stop | `RPRT 0` |
| `K` | Park | `RPRT 0` |
| `_` | Get info | Info string |
| `q` | Quit connection | (closes) |

## Configuration

All settings are stored in `settings.json` and can be modified via the web interface. The file is created automatically on first run.

Key parameters (also accessible via `/settings` page):

```python
# Positioning tolerance (degrees)
TOLERANCE = 1.0          # Stop when within this range

# Speed thresholds
SLOW_THRESHOLD = 5.0     # Use slow speed within this range of target
PWM_FAST = 65535         # Full speed
PWM_SLOW = 32768         # Precision speed
PWM_MIN = 19660          # Minimum effective (~30%)

# Update rate
POSITION_UPDATE_MS = 50  # Control loop interval
```

## Calibration

If your potentiometers have different voltage ranges:

1. Move to 0° position, note the voltage reading
2. Move to max position, note the voltage reading
3. Update `config.py`:

```python
# Azimuth calibration
AZ_V_MIN = 0.54    # Voltage at 0°
AZ_V_MAX = 2.32    # Voltage at 360°

# Elevation calibration
EL_V_MIN = 0.53    # Voltage at 0°
EL_V_MAX = 0.98    # Voltage at 90°
```

## Troubleshooting

### Motors don't move
- Check H-bridge power supply
- Verify wiring connections
- Try increasing `PWM_MIN` if motors stall

### Position readings unstable
- Increase averaging samples in `position.py`
- Check potentiometer connections
- Add 0.1µF capacitors on ADC inputs

### WiFi won't connect
- Verify SSID/password in config
- Check that 2.4GHz network is available
- Pico W doesn't support 5GHz

### GPredict won't connect
- Confirm port 4533 is correct
- Check firewall settings
- Test with `nc` first

## File Structure

```
pico-rotor/
├── settings.py    # Settings manager with JSON persistence
├── motors.py      # Motor control with PWM
├── position.py    # ADC position sensing
├── controller.py  # Main control logic
├── rotctld.py     # Hamlib protocol server
├── webserver.py   # Web interface (control + settings pages)
├── main.py        # Application entry point
├── settings.json  # (created at runtime) Saved settings
└── README.md      # This file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Control page |
| `/settings` | GET | Settings page |
| `/api/status` | GET | Current position and state |
| `/api/mode` | POST | Set mode (manual/auto) |
| `/api/move` | POST | Start manual movement |
| `/api/stop` | POST | Stop all movement |
| `/api/goto` | POST | Go to position |
| `/api/park` | POST | Go to park position |
| `/api/settings` | GET | Get all settings |
| `/api/settings` | POST | Update settings |
| `/api/settings/reset` | POST | Reset to defaults |
| `/api/reboot` | POST | Reboot controller |

## Development

A Linux simulator is available for testing the firmware without hardware. See [`dev/simulator/README.md`](dev/simulator/README.md) for full documentation.

Quick start:
```bash
pip install rich
python dev/simulator/run.py
```

Then access the web interface at http://127.0.0.1/ and test rotctld at port 4533.

## License

MIT License - Use freely for amateur radio applications.
