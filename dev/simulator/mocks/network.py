# Mock network module for MicroPython
# ====================================
# Simulates WiFi WLAN interface for Linux testing

import sys
import os

# Add parent directories to find physics module
_sim_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _sim_root not in sys.path:
    sys.path.insert(0, _sim_root)

from physics.state import state

# Interface constants
STA_IF = 0  # Station (client) interface
AP_IF = 1   # Access Point interface

# Status constants (from MicroPython)
STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_WRONG_PASSWORD = -3
STAT_NO_AP_FOUND = -2
STAT_CONNECT_FAIL = -1
STAT_GOT_IP = 3


class WLAN:
    """Mock WLAN interface class."""

    def __init__(self, interface_id):
        """Initialize WLAN interface (STA_IF or AP_IF)."""
        self._interface = interface_id
        self._active = False
        self._ssid = None
        self._password = None
        self._status = STAT_IDLE

        # Default IPs
        self._sta_ip = "127.0.0.1"
        self._sta_subnet = "255.255.255.0"
        self._sta_gateway = "127.0.0.1"
        self._sta_dns = "127.0.0.1"

        self._ap_ip = "192.168.4.1"
        self._ap_subnet = "255.255.255.0"
        self._ap_gateway = "192.168.4.1"
        self._ap_dns = "192.168.4.1"

        self._ap_essid = "PicoRotor-Setup"
        self._ap_password = "rotorsetup"

    def active(self, is_active=None):
        """Get or set interface active state."""
        if is_active is None:
            return self._active

        self._active = bool(is_active)
        if not self._active:
            self._status = STAT_IDLE
        return self._active

    def connect(self, ssid, password=None):
        """
        Connect to a WiFi network.
        In the simulator, this always succeeds instantly.
        """
        if self._interface != STA_IF:
            return

        self._ssid = ssid
        self._password = password
        self._status = STAT_CONNECTING

        # Simulate instant successful connection
        self._status = STAT_GOT_IP
        state.set_wifi_connected(self._sta_ip)
        print(f"[SIMULATOR] WiFi connected to '{ssid}' (simulated)")

    def disconnect(self):
        """Disconnect from WiFi network."""
        self._ssid = None
        self._password = None
        self._status = STAT_IDLE

    def status(self, param=None):
        """Get connection status."""
        if param is not None:
            # Some status parameters
            return None
        return self._status

    def isconnected(self):
        """Check if connected to a network."""
        return self._status == STAT_GOT_IP

    def ifconfig(self, config=None):
        """Get or set network configuration."""
        if self._interface == STA_IF:
            if config is None:
                return (self._sta_ip, self._sta_subnet,
                        self._sta_gateway, self._sta_dns)
            self._sta_ip, self._sta_subnet, self._sta_gateway, self._sta_dns = config
        else:  # AP_IF
            if config is None:
                return (self._ap_ip, self._ap_subnet,
                        self._ap_gateway, self._ap_dns)
            self._ap_ip, self._ap_subnet, self._ap_gateway, self._ap_dns = config

    def config(self, **kwargs):
        """
        Configure interface parameters.
        For AP mode: essid, password, channel, etc.
        """
        if 'essid' in kwargs:
            self._ap_essid = kwargs['essid']
        if 'password' in kwargs:
            self._ap_password = kwargs['password']

        # When configuring AP mode
        if self._interface == AP_IF and self._active:
            state.set_ap_mode(self._ap_ip)
            print(f"[SIMULATOR] AP mode active: {self._ap_essid}")

    def scan(self):
        """Scan for available networks (returns empty list in simulator)."""
        return []


# Convenience functions
def hostname(name=None):
    """Get or set network hostname."""
    if name is None:
        return "pico-rotor"
    # Setting hostname is no-op in simulator
