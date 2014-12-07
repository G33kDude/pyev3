import os
import pyudev

INPUT_AUTO = None
INPUT_1 = "in1"
INPUT_2 = "in2"
INPUT_3 = "in3"
INPUT_4 = "in4"

OUTPUT_AUTO = None
OUTPUT_A = "outA"
OUTPUT_B = "outB"
OUTPUT_C = "outC"
OUTPUT_D = "outD"

class Device(object):
	def __init__(self, which=0, **kwargs):
		devices = list(pyudev.Context().list_devices(**kwargs))
		if not devices:
			raise IndexError('No devices found')
		try:
			device = devices[which]
		except IndexError:
			raise IndexError('Device index out of range')
		object.__setattr__(self, 'path', devices[which].sys_path)
		object.__setattr__(self, 'items', {})
	
	def __getattr__(self, attr):
		if attr not in self.items:
			raise AttributeError('Unkown attribute: {0}'.format(attr))
		file = attr if len(self.items[attr]) < 3 else self.items[attr][2]
		with open(os.path.join(self.path, file), 'r') as f:
			value = f.read().strip()
		return self.items[attr][0](value)
	
	def __setattr__(self, attr, value):
		if attr not in self.items:
			raise AttributeError('Unkown attribute: {0}'.format(attr))
		if 'w' not in self.items[attr][1]:
			raise TypeError('Attribute is read only: {0}'.format(attr))
		with open(os.path.join(self.path, attr), 'w') as f:
			f.write(str(value))

class Motor(Device):
	def __init__(self, port=None, type=None, which=0):
		if not type:
			type = '*'
		if not port:
			port = '*'
		
		super(Motor, self).__init__(
			which,
			subsystem='tacho-motor',
			PORT=port,
			TYPE=type
		)
		
		object.__setattr__(self, 'items', {
			'duty_cycle': (int, 'r'),
			'duty_cycle_sp': (int, 'rw'),
			'port_name': (str, 'r'),
			'position': (int, 'rw'),
			'position_mode': (str, 'rw'),
			'position_sp': (int, 'rw'),
			'pulses_per_second': (int, 'r'),
			'pulses_per_second_sp': (int, 'rw'),
			'ramp_down_sp': (int, 'rw'),
			'ramp_up_sp': (int, 'rw'),
			'regulation_mode': (str, 'rw'),
			'run': (int, 'rw'),
			'run_mode': (str, 'rw'),
			'speed_regulation_p': (int, 'rw', 'speed_regulation_P'),
			'speed_regulation_i': (int, 'rw', 'speed_regulation_I'),
			'speed_regulation_d': (int, 'rw', 'speed_regulation_D'),
			'speed_regulation_k': (int, 'rw', 'speed_regulation_K'),
			'state': (str, 'r'),
			'stop_mode': (str, 'rw'),
			'stop_modes': (str.split, 'r'),
			'time_sp': (int, 'rw'),
			'type': (str, 'r')
		})
	
	def reset(self):
		with open(os.path.join(self.path, 'reset'), 'w') as f:
			f.write('1')

class LED(Device):
	def __init__(self, Device, which=0):
		if not Device:
			Device = '*'
		
		super(LED, self).__init__(which, sys_name=Device)
		
		object.__setattr__(self, 'items', {
			'max_brightness': (int, 'r'),
			'brightness': (int, 'rw'),
			'trigger': (str, 'rw')
		})

class Sensor(Device):
	def __init__(self, port=None, type=None, which=0):
		if not port:
			port = '*'
		if not type:
			type = '*'
		
		super(Sensor, self).__init__(
			which,
			subsystem='msensor',
			PORT=port,
			TYPE=type
		)
		
		object.__setattr__(self, 'items', {
			'port_name': (str, 'r'),
			'num_values': (int, 'r'),
			'type_name': (str, 'r', 'name'),
			'mode': (str, 'rw'),
			'modes': (str.split, 'r')
		})
	
	def get_value(self, index):
		path = os.path.join(self.path, 'value{0}'.format(index))
		if not os.path.exists(path):
			raise IndexError('Unkown value index: {0}'.format(index))
		with open(path, 'r') as f:
			return int(f.read())
	
	def get_float_value(self, index):
		path = os.path.join(self.path, 'value{0}'.format(index))
		if not os.path.exists(path):
			raise IndexError('Unkown value index: {0}'.format(index))
		with open(path, 'r') as f:
			return float(f.read())