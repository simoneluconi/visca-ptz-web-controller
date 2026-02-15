import socket
import serial
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_ptz_key'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')

class ViscaController:
    def __init__(self):
        self.connection_type = None 
        self.ser = None
        self.sock = None
        self.address = 1 
        self.pan_speed = 0x0C 
        self.tilt_speed = 0x0A 
        self.zoom_speed = 0x04 

    def _to_nibbles(self, val):
        hex_str = f"{int(val):04x}" 
        return bytes([int(c, 16) for c in hex_str])

    def connect_serial(self, port, baudrate=9600):
        try:
            if self.sock: self.sock.close()
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            self.connection_type = 'serial'
            self.if_clear()
            return True, f"Connected Serial: {port} @ {baudrate}"
        except Exception as e:
            return False, str(e)

    def connect_tcp(self, ip, port=5678):
        try:
            if self.ser: self.ser.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(0.5)
            self.sock.connect((ip, int(port)))
            self.connection_type = 'tcp'
            return True, f"Connected TCP: {ip}:{port}"
        except Exception as e:
            return False, str(e)

    def send_visca(self, payload):
        header = bytes([0x80 + self.address])
        terminator = b'\xFF'
        full_packet = header + payload + terminator
        try:
            if self.connection_type == 'serial' and self.ser:
                self.ser.write(full_packet)
            elif self.connection_type == 'tcp' and self.sock:
                self.sock.send(full_packet)
        except Exception as e:
            print(f"TX Error: {e}")

    # --- CORE COMMANDS ---
    def set_speed(self, p_speed, t_speed, z_speed):
        self.pan_speed = max(1, min(24, int(p_speed)))
        self.tilt_speed = max(1, min(20, int(t_speed)))
        self.zoom_speed = max(0, min(7, int(z_speed)))

    def move(self, direction, p_override=None, t_override=None):
        # Existing API kept for UI buttons
        p = int(p_override) if p_override is not None else self.pan_speed
        t = int(t_override) if t_override is not None else self.tilt_speed
        
        p = max(1, min(24, p))
        t = max(1, min(20, t))

        if direction == 'stop':       self.send_visca(b'\x01\x06\x01\x00\x00\x03\x03')
        elif direction == 'up':       self.send_visca(b'\x01\x06\x01' + bytes([p, t]) + b'\x03\x01')
        elif direction == 'down':     self.send_visca(b'\x01\x06\x01' + bytes([p, t]) + b'\x03\x02')
        elif direction == 'left':     self.send_visca(b'\x01\x06\x01' + bytes([p, t]) + b'\x01\x03')
        elif direction == 'right':    self.send_visca(b'\x01\x06\x01' + bytes([p, t]) + b'\x02\x03')
        elif direction == 'upleft':   self.send_visca(b'\x01\x06\x01' + bytes([p, t]) + b'\x01\x01')
        elif direction == 'upright':  self.send_visca(b'\x01\x06\x01' + bytes([p, t]) + b'\x02\x01')
        elif direction == 'downleft': self.send_visca(b'\x01\x06\x01' + bytes([p, t]) + b'\x01\x02')
        elif direction == 'downright':self.send_visca(b'\x01\x06\x01' + bytes([p, t]) + b'\x02\x02')

    def move_raw(self, pan_dir, tilt_dir, p_override=None, t_override=None):
        """
        pan_dir, tilt_dir: numeric -1 (negative / left/up), 0 (stop), 1 (positive / right/down)
        p_override, t_override: speeds (integers) optional
        """
        p = int(p_override) if p_override is not None else self.pan_speed
        t = int(t_override) if t_override is not None else self.tilt_speed

        p = max(1, min(24, p))
        t = max(1, min(20, t))

        def dir_byte(val, axis='pan'):
            if val < 0: return 0x01
            elif val > 0: return 0x02
            else: return 0x03

        p_b = dir_byte(pan_dir, 'pan')
        t_b = dir_byte(tilt_dir, 'tilt')

        # Build and send raw pan/tilt command
        self.send_visca(b'\x01\x06\x01' + bytes([p, t, p_b, t_b]))

    def zoom(self, action, z_override=None):
        z = int(z_override) if z_override is not None else self.zoom_speed
        z = max(0, min(7, z))

        if action == 'tele':   self.send_visca(b'\x01\x04\x07' + bytes([0x20 + z]))
        elif action == 'wide': self.send_visca(b'\x01\x04\x07' + bytes([0x30 + z]))
        elif action == 'stop': self.send_visca(b'\x01\x04\x07\x00')

    def focus(self, action):
        if action == 'far':      self.send_visca(b'\x01\x04\x08\x20')
        elif action == 'near':   self.send_visca(b'\x01\x04\x08\x30')
        elif action == 'stop':   self.send_visca(b'\x01\x04\x08\x00')
        elif action == 'auto':   self.send_visca(b'\x01\x04\x38\x02')
        elif action == 'manual': self.send_visca(b'\x01\x04\x38\x03')

    # --- AUX COMMANDS ---
    def set_iris(self, mode, val=0):
        if mode == 'auto':   self.send_visca(b'\x01\x04\x39\x00')
        elif mode == 'manual': self.send_visca(b'\x01\x04\x39\x03')
        elif mode == 'direct': self.send_visca(b'\x01\x04\x4B' + self._to_nibbles(val))

    def set_gain(self, mode, val=0):
        if mode == 'direct': self.send_visca(b'\x01\x04\x4C' + self._to_nibbles(val))

    def set_wb(self, mode):
        if mode == 'auto':   self.send_visca(b'\x01\x04\x35\x00')
        elif mode == 'manual': self.send_visca(b'\x01\x04\x35\x06')

    def call_led(self, state):
        if state == 'on':     self.send_visca(b'\x01\x33\x01\x01')
        elif state == 'off':  self.send_visca(b'\x01\x33\x01\x00')
        elif state == 'blink':self.send_visca(b'\x01\x33\x01\x02')

    def ir_control(self, disable):
        if disable: self.send_visca(b'\x01\x06\x09\x03')
        else:       self.send_visca(b'\x01\x06\x09\x02')

    def if_clear(self):
        cmd = b'\x88\x01\x00\x01\xFF'
        try:
            if self.connection_type == 'serial' and self.ser: self.ser.write(cmd)
            elif self.connection_type == 'tcp' and self.sock: self.sock.send(cmd)
        except: pass

ptz = ViscaController()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect_camera')
def handle_connect(data):
    if data['mode'] == 'tcp':
        success, msg = ptz.connect_tcp(data['ip'], data['port'])
    else:
        success, msg = ptz.connect_serial(data['port'], int(data['baud']))
    emit('connection_status', {'success': success, 'msg': msg})

@socketio.on('ptz_command')
def handle_ptz(data):
    cmd = data['cmd']
    val = data.get('val', 0)
    
    p_spd = data.get('p_spd')
    t_spd = data.get('t_spd')
    z_spd = data.get('z_spd')
    
    if cmd == 'move_raw':
        # expects p_dir (-1/0/1), t_dir (-1/0/1), optional p_spd/t_spd overrides
        p_dir = int(data.get('p_dir', 0))
        t_dir = int(data.get('t_dir', 0))
        ptz.move_raw(p_dir, t_dir, p_spd, t_spd)
    elif cmd.startswith('move_'): 
        ptz.move(cmd.split('_')[1], p_spd, t_spd)
    elif cmd == 'stop': 
        ptz.move('stop')
    elif cmd.startswith('zoom_'): 
        ptz.zoom(cmd.split('_')[1], z_spd)
    elif cmd.startswith('focus_'): 
        ptz.focus(cmd.split('_')[1])
    
    elif cmd == 'iris_auto': ptz.set_iris('auto')
    elif cmd == 'iris_manual': ptz.set_iris('manual')
    elif cmd == 'iris_set': ptz.set_iris('direct', int(val))
    elif cmd == 'gain_set': ptz.set_gain('direct', int(val))
    elif cmd == 'wb_auto': ptz.set_wb('auto')
    elif cmd == 'wb_manual': ptz.set_wb('manual')
    elif cmd.startswith('led_'): ptz.call_led(cmd.split('_')[1])

@socketio.on('config_change')
def handle_config(data):
    if 'pan_speed' in data:
        ptz.set_speed(data['pan_speed'], data['tilt_speed'], data['zoom_speed'])
    if 'ir_disable' in data:
        ptz.ir_control(data['ir_disable'])

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
