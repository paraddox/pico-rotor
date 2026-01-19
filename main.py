# Pico Rotor Controller - Main Application
# =========================================

import network
import uasyncio as asyncio
import time
from machine import Pin

from settings import settings

# Onboard LED for status indication
led = Pin("LED", Pin.OUT)


def connect_wifi():
    """Connect to WiFi network using settings."""
    ssid = settings.get("wifi_ssid", "")
    password = settings.get("wifi_password", "")
    
    if not ssid:
        print("[wifi] No SSID configured!")
        return None
        
    print(f"[wifi] Connecting to {ssid}...")
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    # Wait for connection with timeout
    max_wait = 20
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("[wifi] Waiting...")
        led.toggle()
        time.sleep(1)
        
    if wlan.status() != 3:
        print(f"[wifi] Connection failed: status={wlan.status()}")
        return None
        
    ip = wlan.ifconfig()[0]
    print(f"[wifi] Connected! IP: {ip}")
    led.on()
    
    return ip


def start_ap_mode():
    """Start access point mode for initial configuration."""
    print("[wifi] Starting AP mode for configuration...")
    
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="PicoRotor-Setup", password="rotorsetup")
    
    # Wait for AP to be active
    while not ap.active():
        time.sleep(0.1)
        
    ip = ap.ifconfig()[0]
    print(f"[wifi] AP Mode active!")
    print(f"[wifi] Connect to 'PicoRotor-Setup' (password: rotorsetup)")
    print(f"[wifi] Then visit http://{ip}/settings")
    
    return ip


async def blink_led(fast: bool = False):
    """Blink LED to indicate status."""
    interval = 200 if fast else 1000
    while True:
        led.toggle()
        await asyncio.sleep_ms(interval)


async def main():
    """Main application entry point."""
    print("=" * 40)
    print("  Pico Rotor Controller v1.0")
    print("=" * 40)
    
    # Try to connect to WiFi
    ip = connect_wifi()
    
    # If WiFi fails, start AP mode
    if ip is None:
        ip = start_ap_mode()
        # Fast blink to indicate AP mode
        blink_task = asyncio.create_task(blink_led(fast=True))
    else:
        # Normal blink for connected mode
        blink_task = asyncio.create_task(blink_led(fast=False))
    
    # Import components
    from controller import RotorController
    from rotctld import RotctldServer
    from webserver import WebServer
    
    # Initialize components
    print("[init] Starting rotor controller...")
    controller = RotorController()
    
    print("[init] Starting rotctld server...")
    rotctld = RotctldServer(controller)
    
    print("[init] Starting web server...")
    webserver = WebServer(controller)
    
    # Start all services
    await rotctld.start()
    await webserver.start()
    controller.start_control_loop()
    
    web_port = settings.get("web_port", 80)
    rotctl_port = settings.get("rotctl_port", 4533)
    
    print("=" * 40)
    print(f"  Web Interface: http://{ip}:{web_port}/")
    print(f"  Settings:      http://{ip}:{web_port}/settings")
    print(f"  rotctld:       {ip}:{rotctl_port}")
    print("=" * 40)
    print("[ready] System ready!")
    
    # Run forever
    while True:
        await asyncio.sleep(60)


# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[exit] Shutdown requested")
    except Exception as e:
        print(f"[ERROR] Fatal: {e}")
        # Error indication - rapid blink
        for _ in range(50):
            led.toggle()
            time.sleep(0.05)
