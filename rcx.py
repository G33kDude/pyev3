
# Control an RCX using your EV3 and an USB IR tower!
# Left motor inversion toggle button on port 1.
# Enable motors toggle button on port 2.
# Right motor inversion toggle button on port 3.

# To use the USB IR tower as a non-root user:
# Add a file `/etc/udev/rules.d/90-legotower.rules` with the contents:
# `ATTRS{idVendor}=="0694",ATTRS{idProduct}=="0001",MODE="0666",GROUP="ev3dev"`
# then connect or re-connect the USB IR tower.

# Press button 1 to invert the direction of the left motor.
# Hold button 2 to provide power to the motors.
# Press button 3 to invert the direction of the right motor.

import pyev3

class Tower:
	def __init__(self, path):
		self.file = open(path, 'r+', 0)
		self.dupe_bit_toggle = True
	
	def send(self, hex, read=True, pad=0):
		"""Send an RCX opcode sequence through the IR tower"""
		buffer = '\x55\xff\x00' # header
		
		sum = 0
		for i in range(0, len(hex), 2):
			byte = int(hex[i:i+2], 16)
			if i == 0: # index of the opcode in a sequence
				byte = self.flip_dupe_bit(byte)
			buffer += self.check(byte)
			sum += byte
		buffer += self.check(sum % 0x100) # "checksum"
		
		self.write(buffer + '\x00'*pad)
		
		if read:
			try:
				return self.read()
			except IOError:
				return None
	
	def check(self, byte):
		"""Return the byte and its bitwise inversion as characters"""
		return chr(byte) + chr(byte^0xFF)
	
	def flip_dupe_bit(self, byte):
		"""Flip the opcode dupe bit every other call"""
		self.dupe_bit_toggle = not self.dupe_bit_toggle
		return byte^8 if self.dupe_bit_toggle else byte
	
	def write(self, value):
		"""Write to the IR tower"""
		self.file.write(value)
	
	def read(self):
		"""Read from the IR tower"""
		return self.file.read()

tower = Tower('/dev/usb/legousbtower0')

btn_left = pyev3.Sensor(pyev3.INPUT_1)
btn_right = pyev3.Sensor(pyev3.INPUT_3)
btn_go = pyev3.Sensor(pyev3.INPUT_2)

btn_left_prev_state = 0
btn_right_prev_state = 0
btn_go_prev_state = 0
try:
	while True:
		btn_left_state = btn_left.get_value(0)
		if btn_left_state != btn_left_prev_state:
			if btn_left_state:
				tower.send('e141') # Invert motor A
			btn_left_prev_state = btn_left_state
		
		btn_right_state = btn_right.get_value(0)
		if btn_right_state != btn_right_prev_state:
			if btn_right_state:
				tower.send('e144') # Invert motor C
			btn_right_prev_state = btn_right_state
		
		btn_go_state = btn_go.get_value(0)
		if btn_go_state != btn_go_prev_state:
			if btn_go_state:
				tower.send('2185') # Turn on A and C
			else:
				tower.send('2145') # Turn off A and C
			btn_go_prev_state = btn_go_state
finally:
	tower.send('2147') # Turn off A B and C
	tower.file.close()