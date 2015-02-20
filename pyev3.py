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
	def __init__(self, attributes, which=0, **kwargs):
		devices = list(pyudev.Context().list_devices(**kwargs))
		if not devices:
			raise IndexError('No devices found')
		try:
			device = devices[which]
		except IndexError:
			raise IndexError('Device index out of range')
		
		object.__setattr__(self, 'path', devices[which].sys_path)
		object.__setattr__(self, 'attributes', attributes)
		object.__setattr__(self, 'files', {})
		
		# Open attribute files
		for attribute_name in self.attributes:
			attribute = self.attributes[attribute_name]
			try:
				file_name = attribute[2]
			except IndexError:
				file_name = attribute_name
			file_path = os.path.join(self.path, file_name)
			self.files[attribute_name] = open(file_path, attribute[1])
	
	def __getattr__(self, attr):
		if attr not in self.attributes:
			raise AttributeError('Unkown attribute: {0}'.format(attr))
		if attr not in self.files:
			raise AttributeError('Attribute file not open: {0}'.format(attr))
		
		attr_file = self.files[attr]
		attr_file.seek(0)
		value = attr_file.read().strip()
		return self.attributes[attr][0](value)
	
	def __setattr__(self, attr, value):
		if attr not in self.attributes:
			raise AttributeError('Unkown attribute: {0}'.format(attr))
		if attr not in self.files:
			raise AttributeError('Attribute file not open: {0}'.format(attr))
		# if 'w' not in self.items[attr][1]:
			# raise TypeError('Attribute is read only: {0}'.format(attr))
		self.files[attr].write(str(value))
		self.files[attr].flush()

class Motor(Device):
	def __init__(self, port=None, type=None, which=0):
		attributes = {
			'duty_cycle': [int, 'r'],
			'duty_cycle_sp': [int, 'r+'],
			'encoder_mode': [str, 'r+'],
			'encoder_modes': [str.split, 'r'],
			'estop': [str, 'r+'],
			'debug_log': [str, 'r', 'log'],
			'polarity_mode': [str, 'r+'],
			'polarity_modes': [str.split, 'r'],
			'port_name': [str, 'r'],
			'position': [int, 'r+'],
			'position_mode': [str, 'r+'],
			'position_modes': [str.split, 'r'],
			'position_sp': [int, 'r+'],
			'pulses_per_second': [int, 'r'],
			'pulses_per_second_sp': [int, 'r+'],
			'ramp_down_sp': [int, 'r+'],
			'ramp_up_sp': [int, 'r+'],
			'regulation_mode': [str, 'r+'],
			'regulation_modes': [str.split, 'r'],
			'run': [int, 'r+'],
			'run_mode': [str, 'r+'],
			'run_modes': [str.split, 'r'],
			'speed_regulation_p': [int, 'r+', 'speed_regulation_P'],
			'speed_regulation_i': [int, 'r+', 'speed_regulation_I'],
			'speed_regulation_d': [int, 'r+', 'speed_regulation_D'],
			'speed_regulation_k': [int, 'r+', 'speed_regulation_K'],
			'state': [str, 'r'],
			'stop_mode': [str, 'r+'],
			'stop_modes': [str.split, 'r'],
			'time_sp': [int, 'r+'],
			'type': [str, 'r']
		}
		
		super(Motor, self).__init__(
			attributes,
			which,
			subsystem='tacho-motor',
			LEGO_PORT_NAME=port or '*' #,
			# LEGO_DRIVER_NAME=type or '*' # Doesn't work with the current driver version
		)
		
		self.files['reset'] = open(os.path.join(self.path, 'reset'), 'w')
	
	def reset(self):
		self.files['reset'].write('1')

class LED(Device):
	def __init__(self, device, which=0):
		attributes = {
			'max_brightness': [int, 'r'],
			'brightness': [int, 'r+'],
			'trigger': [str, 'r+']
		}
		
		super(LED, self).__init__(
			attributes,
			which,
			sys_name=device or '*'
		)

class Sensor(Device):
	def __init__(self, port=None, type=None, which=0):
		attributes = {
			'decimals': [int, 'r'],
			'mode': [str, 'r+'],
			'modes': [str.split, 'r'],
			'command': [str, 'w'],
			'commands': [str.split, 'r'],
			'num_values': [int, 'r'],
			'port_name': [str, 'r'],
			'units': [str, 'r'],
			'driver_name': [str, 'r']
		}
		
		super(Sensor, self).__init__(
			attributes,
			which,
			subsystem='lego-sensor',
			LEGO_PORT_NAME=port or '*',
			LEGO_DRIVER_NAME=type or '*'
		)
		
		for i in range(8):
			file_name = 'value' + str(i)
			self.files[file_name] = open(os.path.join(self.path, file_name), 'r')
	
	def get_value(self, index):
		file_name = 'value' + str(index)
		if file_name not in self.files:
			raise IndexError('Unkown value index: {0}'.format(index))
		value_file = self.files[file_name]
		value_file.seek(0)
		return int(value_file.read())
	
	def get_float_value(self, index):
		return self.get_value(index) / float(10 ** self.decimals)