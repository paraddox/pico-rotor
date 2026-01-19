# Position Sensor Module
# ======================

from machine import ADC, Pin
from settings import settings

class PositionSensor:
    """Reads potentiometer position via ADC and converts to degrees."""
    
    def __init__(self, adc_pin: int, v_min_key: str, v_max_key: str,
                 deg_min_key: str, deg_max_key: str, name: str = "sensor"):
        self.name = name
        self.adc = ADC(Pin(adc_pin))
        
        # Store setting keys for dynamic lookup
        self.v_min_key = v_min_key
        self.v_max_key = v_max_key
        self.deg_min_key = deg_min_key
        self.deg_max_key = deg_max_key
        
        # Averaging samples for noise reduction
        self.samples = 8
        
    @property
    def v_min(self):
        return settings.get(self.v_min_key, 0.0)
        
    @property
    def v_max(self):
        return settings.get(self.v_max_key, 3.3)
        
    @property
    def deg_min(self):
        return settings.get(self.deg_min_key, 0.0)
        
    @property
    def deg_max(self):
        return settings.get(self.deg_max_key, 360.0)
        
    def read_raw(self) -> int:
        """Read raw ADC value (0-65535)."""
        return self.adc.read_u16()
    
    def read_voltage(self) -> float:
        """Read voltage from ADC."""
        raw = self.read_raw()
        vref = settings.get("adc_vref", 3.3)
        return (raw / 65535.0) * vref
    
    def read_averaged_voltage(self) -> float:
        """Read averaged voltage for noise reduction."""
        total = 0
        for _ in range(self.samples):
            total += self.read_raw()
        avg_raw = total / self.samples
        vref = settings.get("adc_vref", 3.3)
        return (avg_raw / 65535.0) * vref
    
    def read_degrees(self) -> float:
        """Read position in degrees with averaging."""
        voltage = self.read_averaged_voltage()
        
        v_min = self.v_min
        v_max = self.v_max
        deg_min = self.deg_min
        deg_max = self.deg_max
        
        # Clamp voltage to calibrated range
        voltage = max(v_min, min(v_max, voltage))
        
        # Linear interpolation to degrees
        v_range = v_max - v_min
        if v_range == 0:
            return deg_min
            
        ratio = (voltage - v_min) / v_range
        deg_range = deg_max - deg_min
        degrees = deg_min + (ratio * deg_range)
        
        return round(degrees, 1)


class RotorPosition:
    """Manages both azimuth and elevation position sensors."""
    
    def __init__(self):
        az_pin = settings.get("az_adc_pin", 26)
        el_pin = settings.get("el_adc_pin", 27)
        
        self.azimuth = PositionSensor(
            az_pin,
            "az_v_min", "az_v_max",
            "az_deg_min", "az_deg_max",
            "azimuth"
        )
        self.elevation = PositionSensor(
            el_pin,
            "el_v_min", "el_v_max",
            "el_deg_min", "el_deg_max",
            "elevation"
        )
        
    def get_position(self) -> tuple:
        """Get current azimuth and elevation in degrees."""
        az = self.azimuth.read_degrees()
        el = self.elevation.read_degrees()
        return (az, el)
    
    def get_az(self) -> float:
        """Get current azimuth in degrees."""
        return self.azimuth.read_degrees()
    
    def get_el(self) -> float:
        """Get current elevation in degrees."""
        return self.elevation.read_degrees()
    
    def get_voltages(self) -> tuple:
        """Get raw voltage readings (useful for calibration)."""
        az_v = self.azimuth.read_averaged_voltage()
        el_v = self.elevation.read_averaged_voltage()
        return (az_v, el_v)
