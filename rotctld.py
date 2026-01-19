# Hamlib rotctld Protocol Server
# ==============================
# Implements rotctld protocol over TCP for GPredict/hamlib compatibility

import uasyncio as asyncio
from settings import settings

class RotctldServer:
    """Hamlib rotctld protocol server."""
    
    MODEL_ID = 1  # ROT_MODEL_DUMMY in hamlib
    
    def __init__(self, controller):
        self.controller = controller
        self.server = None
        self.clients = []
        
    async def start(self):
        """Start the rotctld server."""
        port = settings.get("rotctl_port", 4533)
        self.server = await asyncio.start_server(
            self._handle_client,
            "0.0.0.0",
            port
        )
        print(f"[rotctld] Server listening on port {port}")
        
    async def _handle_client(self, reader, writer):
        """Handle a single client connection."""
        addr = writer.get_extra_info('peername')
        print(f"[rotctld] Client connected: {addr}")
        self.clients.append(writer)
        
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                    
                line = data.decode().strip()
                if not line:
                    continue
                    
                response = self._process_command(line)
                if response is None:
                    break
                    
                writer.write((response + "\n").encode())
                await writer.drain()
                
        except Exception as e:
            print(f"[rotctld] Error: {e}")
        finally:
            self.clients.remove(writer)
            writer.close()
            await writer.wait_closed()
            print(f"[rotctld] Client disconnected: {addr}")
            
    def _process_command(self, line: str) -> str:
        """Process a rotctld command and return response."""
        parts = line.split()
        if not parts:
            return "RPRT -1"
            
        cmd = parts[0]
        args = parts[1:]
        
        # Get position
        if cmd in ("p", "\\get_pos"):
            az, el = self.controller.position.get_position()
            return f"{az:.1f}\n{el:.1f}"
            
        # Set position
        elif cmd in ("P", "\\set_pos"):
            if len(args) >= 2:
                try:
                    az = float(args[0])
                    el = float(args[1])
                    
                    az_min = settings.get("az_limit_min", 0.0)
                    az_max = settings.get("az_limit_max", 360.0)
                    el_min = settings.get("el_limit_min", 0.0)
                    el_max = settings.get("el_limit_max", 90.0)
                    
                    if not (az_min <= az <= az_max):
                        return "RPRT -1"
                    if not (el_min <= el <= el_max):
                        return "RPRT -1"
                        
                    self.controller.set_target(az, el)
                    return "RPRT 0"
                except ValueError:
                    return "RPRT -1"
            return "RPRT -1"
            
        # Stop
        elif cmd in ("S", "\\stop"):
            self.controller.stop()
            return "RPRT 0"
            
        # Park
        elif cmd in ("K", "\\park"):
            self.controller.park()
            return "RPRT 0"
            
        # Quit
        elif cmd in ("q", "\\quit"):
            return None
            
        # Get info
        elif cmd in ("_", "\\get_info"):
            return "Pico Rotor Controller v1.0"
            
        # Dump state
        elif cmd == "\\dump_state":
            return self._format_dump_state()
            
        # Dump capabilities
        elif cmd in ("1", "\\dump_caps"):
            return self._format_dump_caps()
            
        # Move direction
        elif cmd in ("M", "\\move"):
            if len(args) >= 2:
                try:
                    direction = int(args[0])
                    
                    if direction == 0:
                        self.controller.stop()
                    elif direction == 1:
                        self.controller.manual_el_up()
                    elif direction == 2:
                        self.controller.manual_el_down()
                    elif direction == 4:
                        self.controller.manual_az_ccw()
                    elif direction == 8:
                        self.controller.manual_az_cw()
                        
                    return "RPRT 0"
                except ValueError:
                    return "RPRT -1"
            return "RPRT -1"
            
        # Reset
        elif cmd in ("R", "\\reset"):
            self.controller.stop()
            self.controller.park()
            return "RPRT 0"
            
        else:
            return "RPRT -1"
            
    def _format_dump_state(self) -> str:
        """Format the dump_state response."""
        lines = [
            "0",
            f"{self.MODEL_ID}",
            f"{settings.get('az_limit_min', 0.0):.1f}",
            f"{settings.get('az_limit_max', 360.0):.1f}",
            f"{settings.get('el_limit_min', 0.0):.1f}",
            f"{settings.get('el_limit_max', 90.0):.1f}",
        ]
        return "\n".join(lines)
        
    def _format_dump_caps(self) -> str:
        """Format the dump_caps response."""
        lines = [
            "Caps dump for model: 1",
            "Model name: Pico Rotor",
            "Mfg name: DIY",
            "Backend version: 1.0",
            "Backend status: Stable",
            f"Min Azimuth: {settings.get('az_limit_min', 0.0)}",
            f"Max Azimuth: {settings.get('az_limit_max', 360.0)}",
            f"Min Elevation: {settings.get('el_limit_min', 0.0)}",
            f"Max Elevation: {settings.get('el_limit_max', 90.0)}",
        ]
        return "\n".join(lines)
