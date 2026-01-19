# Web Server Module with Settings Page
# =====================================

import uasyncio as asyncio
import json
from settings import settings

# Control page HTML
HTML_CONTROL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rotor Controller</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 20px; color: #00d9ff; }
        .nav { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        .nav a {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            color: #00d9ff;
            text-decoration: none;
            border-radius: 8px;
        }
        .nav a:hover { background: rgba(255,255,255,0.2); }
        .nav a.active { background: #00d9ff; color: #000; }
        .status-panel {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .position-display { display: flex; justify-content: space-around; margin-bottom: 15px; }
        .position-box {
            text-align: center;
            padding: 15px 30px;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            min-width: 140px;
        }
        .position-label { font-size: 14px; color: #aaa; margin-bottom: 5px; }
        .position-value {
            font-size: 36px;
            font-weight: bold;
            color: #00ff88;
            font-family: 'Courier New', monospace;
        }
        .position-unit { font-size: 14px; color: #888; }
        .voltage-display { font-size: 11px; color: #666; margin-top: 4px; }
        .status-text {
            text-align: center;
            padding: 8px;
            background: rgba(0,0,0,0.2);
            border-radius: 4px;
            font-size: 14px;
        }
        .mode-selector { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        .mode-btn {
            padding: 10px 25px;
            border: 2px solid #444;
            background: rgba(0,0,0,0.3);
            color: #aaa;
            border-radius: 20px;
            cursor: pointer;
        }
        .mode-btn.active { border-color: #00d9ff; color: #00d9ff; background: rgba(0,217,255,0.1); }
        .control-panel {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .panel-title {
            font-size: 16px;
            color: #00d9ff;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .direction-controls {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            max-width: 300px;
            margin: 0 auto 20px;
        }
        .dir-btn {
            padding: 20px;
            font-size: 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            background: #2a2a4a;
            color: #fff;
        }
        .dir-btn:hover { background: #3a3a6a; }
        .dir-btn:active { transform: scale(0.95); }
        .dir-btn.up { grid-column: 2; }
        .dir-btn.left { grid-column: 1; grid-row: 2; }
        .dir-btn.stop { grid-column: 2; grid-row: 2; background: #ff4444; font-size: 14px; font-weight: bold; }
        .dir-btn.stop:hover { background: #ff6666; }
        .dir-btn.right { grid-column: 3; grid-row: 2; }
        .dir-btn.down { grid-column: 2; grid-row: 3; }
        .goto-controls { display: flex; flex-direction: column; gap: 15px; }
        .goto-row { display: flex; align-items: center; gap: 10px; }
        .goto-label { width: 80px; font-size: 14px; color: #aaa; }
        .goto-input-group { display: flex; align-items: center; flex: 1; }
        .goto-input {
            flex: 1;
            padding: 12px;
            font-size: 18px;
            background: rgba(0,0,0,0.3);
            border: 1px solid #444;
            border-radius: 4px;
            color: #fff;
            text-align: center;
        }
        .goto-input:focus { outline: none; border-color: #00d9ff; }
        .spin-btn {
            width: 40px;
            height: 44px;
            border: none;
            background: #2a2a4a;
            color: #fff;
            cursor: pointer;
            font-size: 18px;
        }
        .spin-btn:hover { background: #3a3a6a; }
        .spin-btns { display: flex; flex-direction: column; }
        .btn-row { display: flex; gap: 10px; margin-top: 15px; }
        .action-btn {
            flex: 1;
            padding: 15px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .btn-go { background: #00aa55; color: #fff; }
        .btn-go:hover { background: #00cc66; }
        .btn-park { background: #aa5500; color: #fff; }
        .btn-park:hover { background: #cc6600; }
        .btn-stop-main {
            background: #cc0000;
            color: #fff;
            padding: 20px;
            font-size: 20px;
            margin-top: 20px;
            width: 100%;
        }
        .btn-stop-main:hover { background: #ff0000; }
        .connection-status { text-align: center; padding: 10px; font-size: 12px; color: #666; }
        .connected { color: #00ff88; }
        .disconnected { color: #ff4444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛰️ Rotor Controller</h1>
        <div class="nav">
            <a href="/" class="active">Control</a>
            <a href="/settings">Settings</a>
        </div>
        <div class="status-panel">
            <div class="position-display">
                <div class="position-box">
                    <div class="position-label">AZIMUTH</div>
                    <div class="position-value" id="az-value">---</div>
                    <div class="position-unit">degrees</div>
                    <div class="voltage-display" id="az-voltage">--.---V</div>
                </div>
                <div class="position-box">
                    <div class="position-label">ELEVATION</div>
                    <div class="position-value" id="el-value">---</div>
                    <div class="position-unit">degrees</div>
                    <div class="voltage-display" id="el-voltage">--.---V</div>
                </div>
            </div>
            <div class="status-text">Status: <span id="status-text">Connecting...</span></div>
        </div>
        <div class="mode-selector">
            <button class="mode-btn active" id="mode-manual" onclick="setMode('manual')">Manual</button>
            <button class="mode-btn" id="mode-auto" onclick="setMode('auto')">Auto (GPredict)</button>
        </div>
        <div class="control-panel">
            <div class="panel-title">Direction Control</div>
            <div class="direction-controls">
                <button class="dir-btn up" onmousedown="move('el_up')" onmouseup="stopMove()" ontouchstart="move('el_up')" ontouchend="stopMove()">▲<br><small>EL+</small></button>
                <button class="dir-btn left" onmousedown="move('az_ccw')" onmouseup="stopMove()" ontouchstart="move('az_ccw')" ontouchend="stopMove()">◀<br><small>AZ-</small></button>
                <button class="dir-btn stop" onclick="stopAll()">STOP</button>
                <button class="dir-btn right" onmousedown="move('az_cw')" onmouseup="stopMove()" ontouchstart="move('az_cw')" ontouchend="stopMove()">▶<br><small>AZ+</small></button>
                <button class="dir-btn down" onmousedown="move('el_down')" onmouseup="stopMove()" ontouchstart="move('el_down')" ontouchend="stopMove()">▼<br><small>EL-</small></button>
            </div>
            <div class="panel-title">Go To Position</div>
            <div class="goto-controls">
                <div class="goto-row">
                    <span class="goto-label">Azimuth:</span>
                    <div class="goto-input-group">
                        <input type="number" id="goto-az" class="goto-input" min="0" max="360" step="1" value="0">
                        <div class="spin-btns">
                            <button class="spin-btn" onclick="spinValue('goto-az', 1, 0, 360)">+</button>
                            <button class="spin-btn" onclick="spinValue('goto-az', -1, 0, 360)">-</button>
                        </div>
                    </div>
                </div>
                <div class="goto-row">
                    <span class="goto-label">Elevation:</span>
                    <div class="goto-input-group">
                        <input type="number" id="goto-el" class="goto-input" min="0" max="90" step="1" value="0">
                        <div class="spin-btns">
                            <button class="spin-btn" onclick="spinValue('goto-el', 1, 0, 90)">+</button>
                            <button class="spin-btn" onclick="spinValue('goto-el', -1, 0, 90)">-</button>
                        </div>
                    </div>
                </div>
                <div class="btn-row">
                    <button class="action-btn btn-go" onclick="goToPosition()">GO</button>
                    <button class="action-btn btn-park" onclick="park()">PARK</button>
                </div>
            </div>
        </div>
        <button class="action-btn btn-stop-main" onclick="stopAll()">⛔ EMERGENCY STOP</button>
        <div class="connection-status"><span id="conn-status" class="disconnected">Disconnected</span></div>
    </div>
    <script>
        async function api(endpoint, method='GET', body=null) {
            try {
                const opts = { method };
                if (body) { opts.headers = { 'Content-Type': 'application/json' }; opts.body = JSON.stringify(body); }
                const res = await fetch('/api/' + endpoint, opts);
                return await res.json();
            } catch (e) { return null; }
        }
        async function updateStatus() {
            const data = await api('status');
            if (data) {
                document.getElementById('az-value').textContent = data.azimuth.toFixed(1);
                document.getElementById('el-value').textContent = data.elevation.toFixed(1);
                document.getElementById('az-voltage').textContent = data.az_voltage.toFixed(3) + 'V';
                document.getElementById('el-voltage').textContent = data.el_voltage.toFixed(3) + 'V';
                document.getElementById('status-text').textContent = data.state;
                document.getElementById('conn-status').textContent = 'Connected';
                document.getElementById('conn-status').className = 'connected';
                document.getElementById('mode-manual').classList.toggle('active', data.mode === 'manual');
                document.getElementById('mode-auto').classList.toggle('active', data.mode === 'auto');
            } else {
                document.getElementById('conn-status').textContent = 'Disconnected';
                document.getElementById('conn-status').className = 'disconnected';
            }
        }
        function setMode(mode) { api('mode', 'POST', { mode }); }
        function move(direction) { api('move', 'POST', { direction }); }
        function stopMove() { api('stop', 'POST'); }
        function stopAll() { api('stop', 'POST'); }
        function goToPosition() {
            const az = parseFloat(document.getElementById('goto-az').value);
            const el = parseFloat(document.getElementById('goto-el').value);
            if (isNaN(az) || az < 0 || az > 360) { alert('Azimuth must be 0-360'); return; }
            if (isNaN(el) || el < 0 || el > 90) { alert('Elevation must be 0-90'); return; }
            api('goto', 'POST', { azimuth: az, elevation: el });
        }
        function park() { api('park', 'POST'); }
        function spinValue(id, delta, min, max) {
            const input = document.getElementById(id);
            let val = parseFloat(input.value) || 0;
            val = Math.max(min, Math.min(max, val + delta));
            input.value = val;
        }
        updateStatus();
        setInterval(updateStatus, 500);
        document.addEventListener('contextmenu', e => e.preventDefault());
    </script>
</body>
</html>"""

# Settings page HTML
HTML_SETTINGS = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rotor Settings</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 700px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 20px; color: #00d9ff; }
        .nav { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        .nav a {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            color: #00d9ff;
            text-decoration: none;
            border-radius: 8px;
        }
        .nav a:hover { background: rgba(255,255,255,0.2); }
        .nav a.active { background: #00d9ff; color: #000; }
        .settings-panel {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .panel-title {
            font-size: 18px;
            color: #00d9ff;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .setting-group { margin-bottom: 20px; }
        .setting-row {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        .setting-label {
            width: 180px;
            font-size: 14px;
            color: #ccc;
        }
        .setting-input {
            flex: 1;
            min-width: 120px;
            padding: 10px;
            font-size: 14px;
            background: rgba(0,0,0,0.3);
            border: 1px solid #444;
            border-radius: 4px;
            color: #fff;
        }
        .setting-input:focus { outline: none; border-color: #00d9ff; }
        .setting-unit { margin-left: 8px; font-size: 12px; color: #888; min-width: 40px; }
        .setting-help { font-size: 11px; color: #666; margin-top: 4px; width: 100%; padding-left: 180px; }
        .btn-row { display: flex; gap: 10px; margin-top: 20px; justify-content: center; flex-wrap: wrap; }
        .btn {
            padding: 12px 30px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .btn-save { background: #00aa55; color: #fff; }
        .btn-save:hover { background: #00cc66; }
        .btn-reset { background: #aa5500; color: #fff; }
        .btn-reset:hover { background: #cc6600; }
        .btn-reboot { background: #aa0055; color: #fff; }
        .btn-reboot:hover { background: #cc0066; }
        .message {
            text-align: center;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 8px;
            display: none;
        }
        .message.success { display: block; background: rgba(0,170,85,0.3); color: #00ff88; }
        .message.error { display: block; background: rgba(170,0,0,0.3); color: #ff6666; }
        .calibration-help {
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 13px;
            line-height: 1.6;
        }
        .calibration-help h4 { color: #00d9ff; margin-bottom: 10px; }
        .live-voltage {
            font-family: 'Courier New', monospace;
            color: #00ff88;
            font-size: 16px;
            padding: 8px 15px;
            background: rgba(0,0,0,0.3);
            border-radius: 4px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ Settings</h1>
        <div class="nav">
            <a href="/">Control</a>
            <a href="/settings" class="active">Settings</a>
        </div>
        
        <div id="message" class="message"></div>
        
        <form id="settings-form">
            <div class="settings-panel">
                <div class="panel-title">🌐 Network</div>
                <div class="setting-row">
                    <label class="setting-label">WiFi SSID</label>
                    <input type="text" class="setting-input" name="wifi_ssid" id="wifi_ssid" value="YOUR_WIFI_SSID">
                </div>
                <div class="setting-row">
                    <label class="setting-label">WiFi Password</label>
                    <input type="password" class="setting-input" name="wifi_password" id="wifi_password" value="YOUR_WIFI_PASSWORD">
                </div>
                <div class="setting-row">
                    <label class="setting-label">Web Port</label>
                    <input type="number" class="setting-input" name="web_port" id="web_port" min="1" max="65535" value="80">
                </div>
                <div class="setting-row">
                    <label class="setting-label">Rotctld Port</label>
                    <input type="number" class="setting-input" name="rotctl_port" id="rotctl_port" min="1" max="65535" value="4533">
                    <span class="setting-unit">(default: 4533)</span>
                </div>
            </div>
            
            <div class="settings-panel">
                <div class="panel-title">🔌 GPIO Pins</div>
                <div class="setting-row">
                    <label class="setting-label">Azimuth Motor A</label>
                    <input type="number" class="setting-input" name="az_pin_a" id="az_pin_a" min="0" max="28" value="2">
                    <span class="setting-unit">GP</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Azimuth Motor B</label>
                    <input type="number" class="setting-input" name="az_pin_b" id="az_pin_b" min="0" max="28" value="3">
                    <span class="setting-unit">GP</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Elevation Motor A</label>
                    <input type="number" class="setting-input" name="el_pin_a" id="el_pin_a" min="0" max="28" value="4">
                    <span class="setting-unit">GP</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Elevation Motor B</label>
                    <input type="number" class="setting-input" name="el_pin_b" id="el_pin_b" min="0" max="28" value="5">
                    <span class="setting-unit">GP</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Azimuth ADC</label>
                    <input type="number" class="setting-input" name="az_adc_pin" id="az_adc_pin" min="26" max="28" value="26">
                    <span class="setting-unit">GP (26-28)</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Elevation ADC</label>
                    <input type="number" class="setting-input" name="el_adc_pin" id="el_adc_pin" min="26" max="28" value="27">
                    <span class="setting-unit">GP (26-28)</span>
                </div>
            </div>
            
            <div class="settings-panel">
                <div class="panel-title">📏 Calibration - Azimuth</div>
                <div class="setting-row">
                    <label class="setting-label">Current Voltage</label>
                    <span class="live-voltage" id="az-live-v">--</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Voltage at Min</label>
                    <input type="number" class="setting-input" name="az_v_min" id="az_v_min" step="0.01" min="0" max="3.3" value="0.54">
                    <span class="setting-unit">V</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Voltage at Max</label>
                    <input type="number" class="setting-input" name="az_v_max" id="az_v_max" step="0.01" min="0" max="3.3" value="2.32">
                    <span class="setting-unit">V</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Min Degrees</label>
                    <input type="number" class="setting-input" name="az_deg_min" id="az_deg_min" step="0.1" value="0">
                    <span class="setting-unit">°</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Max Degrees</label>
                    <input type="number" class="setting-input" name="az_deg_max" id="az_deg_max" step="0.1" value="360">
                    <span class="setting-unit">°</span>
                </div>
            </div>

            <div class="settings-panel">
                <div class="panel-title">📏 Calibration - Elevation</div>
                <div class="setting-row">
                    <label class="setting-label">Current Voltage</label>
                    <span class="live-voltage" id="el-live-v">--</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Voltage at Min</label>
                    <input type="number" class="setting-input" name="el_v_min" id="el_v_min" step="0.01" min="0" max="3.3" value="0.53">
                    <span class="setting-unit">V</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Voltage at Max</label>
                    <input type="number" class="setting-input" name="el_v_max" id="el_v_max" step="0.01" min="0" max="3.3" value="0.98">
                    <span class="setting-unit">V</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Min Degrees</label>
                    <input type="number" class="setting-input" name="el_deg_min" id="el_deg_min" step="0.1" value="0">
                    <span class="setting-unit">°</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Max Degrees</label>
                    <input type="number" class="setting-input" name="el_deg_max" id="el_deg_max" step="0.1" value="90">
                    <span class="setting-unit">°</span>
                </div>
                <div class="calibration-help">
                    <h4>Calibration Tips</h4>
                    1. Move rotor to minimum position (0°), note the voltage shown above<br>
                    2. Enter this value in "Voltage at Min"<br>
                    3. Move rotor to maximum position, note the voltage<br>
                    4. Enter this value in "Voltage at Max"<br>
                    5. Save and test positioning accuracy
                </div>
            </div>
            
            <div class="settings-panel">
                <div class="panel-title">⚡ Motor Control</div>
                <div class="setting-row">
                    <label class="setting-label">PWM Frequency</label>
                    <input type="number" class="setting-input" name="pwm_freq" id="pwm_freq" min="100" max="20000" value="1000">
                    <span class="setting-unit">Hz</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Fast Speed</label>
                    <input type="number" class="setting-input" name="pwm_fast" id="pwm_fast" min="0" max="65535" value="65535">
                    <span class="setting-unit">(0-65535)</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Slow Speed</label>
                    <input type="number" class="setting-input" name="pwm_slow" id="pwm_slow" min="0" max="65535" value="32768">
                    <span class="setting-unit">(precision)</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Minimum Speed</label>
                    <input type="number" class="setting-input" name="pwm_min" id="pwm_min" min="0" max="65535" value="19660">
                    <span class="setting-unit">(stall threshold)</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">ADC Reference</label>
                    <input type="number" class="setting-input" name="adc_vref" id="adc_vref" step="0.01" min="0" max="5" value="3.3">
                    <span class="setting-unit">V</span>
                </div>
            </div>
            
            <div class="settings-panel">
                <div class="panel-title">🎯 Positioning</div>
                <div class="setting-row">
                    <label class="setting-label">Tolerance</label>
                    <input type="number" class="setting-input" name="tolerance" id="tolerance" step="0.1" min="0.1" max="10" value="1.0">
                    <span class="setting-unit">° (stop accuracy)</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Slow Threshold</label>
                    <input type="number" class="setting-input" name="slow_threshold" id="slow_threshold" step="0.1" min="1" max="30" value="5.0">
                    <span class="setting-unit">° (switch to slow)</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Update Interval</label>
                    <input type="number" class="setting-input" name="position_update_ms" id="position_update_ms" min="10" max="500" value="50">
                    <span class="setting-unit">ms</span>
                </div>
            </div>
            
            <div class="settings-panel">
                <div class="panel-title">🔒 Limits & Park</div>
                <div class="setting-row">
                    <label class="setting-label">Az Min Limit</label>
                    <input type="number" class="setting-input" name="az_limit_min" id="az_limit_min" step="0.1" value="0">
                    <span class="setting-unit">°</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Az Max Limit</label>
                    <input type="number" class="setting-input" name="az_limit_max" id="az_limit_max" step="0.1" value="360">
                    <span class="setting-unit">°</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">El Min Limit</label>
                    <input type="number" class="setting-input" name="el_limit_min" id="el_limit_min" step="0.1" value="0">
                    <span class="setting-unit">°</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">El Max Limit</label>
                    <input type="number" class="setting-input" name="el_limit_max" id="el_limit_max" step="0.1" value="90">
                    <span class="setting-unit">°</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Park Azimuth</label>
                    <input type="number" class="setting-input" name="park_az" id="park_az" step="0.1" value="0">
                    <span class="setting-unit">°</span>
                </div>
                <div class="setting-row">
                    <label class="setting-label">Park Elevation</label>
                    <input type="number" class="setting-input" name="park_el" id="park_el" step="0.1" value="0">
                    <span class="setting-unit">°</span>
                </div>
            </div>
            
            <div class="btn-row">
                <button type="submit" class="btn btn-save">💾 Save Settings</button>
                <button type="button" class="btn btn-reset" onclick="resetDefaults()">↩️ Reset Defaults</button>
                <button type="button" class="btn btn-reboot" onclick="reboot()">🔄 Reboot</button>
            </div>
        </form>
    </div>
    <script>
        const fields = [
            'wifi_ssid', 'wifi_password', 'web_port', 'rotctl_port',
            'az_pin_a', 'az_pin_b', 'el_pin_a', 'el_pin_b', 'az_adc_pin', 'el_adc_pin',
            'az_v_min', 'az_v_max', 'az_deg_min', 'az_deg_max',
            'el_v_min', 'el_v_max', 'el_deg_min', 'el_deg_max',
            'pwm_freq', 'pwm_fast', 'pwm_slow', 'pwm_min', 'adc_vref',
            'tolerance', 'slow_threshold', 'position_update_ms',
            'az_limit_min', 'az_limit_max', 'el_limit_min', 'el_limit_max',
            'park_az', 'park_el'
        ];
        
        async function loadSettings() {
            try {
                const res = await fetch('/api/settings');
                const data = await res.json();
                fields.forEach(f => {
                    const el = document.getElementById(f);
                    if (el && data[f] !== undefined) el.value = data[f];
                });
            } catch (e) { showMessage('Failed to load settings', 'error'); }
        }
        
        async function updateVoltages() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('az-live-v').textContent = data.az_voltage.toFixed(3) + 'V';
                document.getElementById('el-live-v').textContent = data.el_voltage.toFixed(3) + 'V';
            } catch (e) {}
        }
        
        function showMessage(text, type) {
            const el = document.getElementById('message');
            el.textContent = text;
            el.className = 'message ' + type;
            setTimeout(() => { el.className = 'message'; }, 5000);
        }
        
        document.getElementById('settings-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {};
            fields.forEach(f => {
                const el = document.getElementById(f);
                if (el) data[f] = el.value;
            });
            try {
                const res = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                if (result.ok) {
                    showMessage('Settings saved! Some changes require reboot.', 'success');
                } else {
                    showMessage('Failed to save: ' + (result.error || 'Unknown error'), 'error');
                }
            } catch (e) { showMessage('Failed to save settings', 'error'); }
        });
        
        async function resetDefaults() {
            if (!confirm('Reset all settings to defaults?')) return;
            try {
                const res = await fetch('/api/settings/reset', { method: 'POST' });
                const result = await res.json();
                if (result.ok) {
                    showMessage('Settings reset to defaults', 'success');
                    loadSettings();
                }
            } catch (e) { showMessage('Failed to reset', 'error'); }
        }
        
        async function reboot() {
            if (!confirm('Reboot the controller?')) return;
            try {
                await fetch('/api/reboot', { method: 'POST' });
                showMessage('Rebooting... Please wait and refresh.', 'success');
            } catch (e) {}
        }
        
        loadSettings();
        setInterval(updateVoltages, 500);
    </script>
</body>
</html>"""


class WebServer:
    """HTTP server for web-based rotor control and settings."""
    
    def __init__(self, controller):
        self.controller = controller
        self.server = None
        
    async def start(self):
        """Start the web server."""
        port = settings.get("web_port", 80)
        self.server = await asyncio.start_server(
            self._handle_request,
            "0.0.0.0",
            port
        )
        print(f"[web] Server listening on port {port}")
        
    async def _handle_request(self, reader, writer):
        """Handle an HTTP request."""
        try:
            request_line = await reader.readline()
            request_line = request_line.decode().strip()
            
            if not request_line:
                writer.close()
                return
                
            parts = request_line.split()
            if len(parts) < 2:
                writer.close()
                return
                
            method = parts[0]
            path = parts[1]
            
            content_length = 0
            while True:
                header = await reader.readline()
                header = header.decode().strip()
                if not header:
                    break
                if header.lower().startswith('content-length:'):
                    content_length = int(header.split(':')[1].strip())
                    
            body = None
            if content_length > 0:
                body_data = await reader.read(content_length)
                try:
                    body = json.loads(body_data.decode())
                except:
                    body = {}
                    
            response = self._route(method, path, body)
            writer.write(response.encode())
            await writer.drain()
            
        except Exception as e:
            print(f"[web] Error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            
    def _route(self, method: str, path: str, body: dict) -> str:
        """Route request to handler."""
        
        # Pages
        if path == "/" and method == "GET":
            return self._http_response(200, HTML_CONTROL, "text/html")
            
        elif path == "/settings" and method == "GET":
            return self._http_response(200, HTML_SETTINGS, "text/html")
            
        # Control API
        elif path == "/api/status" and method == "GET":
            status = self.controller.get_status()
            return self._json_response(status)
            
        elif path == "/api/mode" and method == "POST":
            if body and "mode" in body:
                self.controller.set_mode(body["mode"])
            return self._json_response({"ok": True})
            
        elif path == "/api/move" and method == "POST":
            if body and "direction" in body:
                direction = body["direction"]
                if direction == "az_cw":
                    self.controller.manual_az_cw()
                elif direction == "az_ccw":
                    self.controller.manual_az_ccw()
                elif direction == "el_up":
                    self.controller.manual_el_up()
                elif direction == "el_down":
                    self.controller.manual_el_down()
            return self._json_response({"ok": True})
            
        elif path == "/api/stop" and method == "POST":
            self.controller.stop()
            return self._json_response({"ok": True})
            
        elif path == "/api/goto" and method == "POST":
            if body:
                az = body.get("azimuth")
                el = body.get("elevation")
                self.controller.set_target(az, el)
            return self._json_response({"ok": True})
            
        elif path == "/api/park" and method == "POST":
            self.controller.park()
            return self._json_response({"ok": True})
            
        # Settings API
        elif path == "/api/settings" and method == "GET":
            return self._json_response(settings.get_all())
            
        elif path == "/api/settings" and method == "POST":
            if body:
                settings.update(body)
                if settings.save():
                    return self._json_response({"ok": True})
                else:
                    return self._json_response({"ok": False, "error": "Save failed"})
            return self._json_response({"ok": False, "error": "No data"})
            
        elif path == "/api/settings/reset" and method == "POST":
            settings.reset_to_defaults()
            settings.save()
            return self._json_response({"ok": True})
            
        elif path == "/api/reboot" and method == "POST":
            import machine
            machine.reset()
            return self._json_response({"ok": True})
            
        else:
            return self._http_response(404, "Not Found")
            
    def _http_response(self, status: int, body: str, content_type: str = "text/plain") -> str:
        """Build HTTP response."""
        status_text = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}
        return (
            f"HTTP/1.1 {status} {status_text.get(status, 'Unknown')}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: close\r\n"
            f"Access-Control-Allow-Origin: *\r\n"
            f"\r\n"
            f"{body}"
        )
        
    def _json_response(self, data: dict) -> str:
        """Build JSON HTTP response."""
        body = json.dumps(data)
        return self._http_response(200, body, "application/json")
