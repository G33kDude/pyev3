#!/usr/bin/python
import struct
import threading
import time
import sys

import pyev3

# Multi-motor abstraction
class Motors(object):
	def __init__(self, left_motor_port, right_motor_port):
		object.__setattr__(self, 'left_motor', pyev3.Motor(left_motor_port))
		object.__setattr__(self, 'right_motor', pyev3.Motor(right_motor_port))
	
	def __getattr__(self, attr):
		return self.left_motor.__getattr__(attr)
	
	def __setattr__(self, attr, value):
		self.left_motor.__setattr__(attr, value)
		self.right_motor.__setattr__(attr, value)
	
	def reset(self):
		self.left_motor.reset()
		self.right_motor.reset()

# Mouse abstraction
class Mouse(object):
	def __init__(self, infile_path="/dev/input/event1"):
		self.FORMAT = 'llHHi'
		self.EVENT_SIZE = struct.calcsize(self.FORMAT)
		self.in_file = open(infile_path, "rb")
		self.xpos = 0
		self.ypos = 0
	
	def get_event(self):
		event = self.in_file.read(self.EVENT_SIZE)
		if event:
			tv_sec, tv_usec, type, code, value = struct.unpack(self.FORMAT, event)
			if type == 2:
				if code == 1:
					self.ypos += value
				else:
					self.xpos += value
			return True
		return False
	
	def __del__(self):
		self.in_file.close()

# Helper function for threading
def process_mouse(q, mouse):
	while mouse.get_event():
		pass

def clamp(val, upper, lower):
	return max(lower, min(val, upper))

# Set up motors
motors = Motors(pyev3.OUTPUT_B, pyev3.OUTPUT_C)
motors.reset()
motors.position = 0 # Does this not get reset?
motors.regulation_mode = "on"
motors.stop_mode = "brake"
motors.run = 1

# Set up mouse
mouse = Mouse()

# Handle mouse in a separate thread because it uses blocking file IO
t = threading.Thread(target=process_mouse, args = ("", mouse))
t.daemon = True
t.start()

delta_x = 0
last_x = mouse.xpos
try:
	while True:
		# Cache mouse position to prevent "race conditions"
		xpos, ypos = mouse.xpos, mouse.ypos
		
		# flip vertical axis, since up is negative in computing
		ypos = -ypos
		
		# Compute amount mouse has moved along x axis
		delta_x = xpos - last_x
		last_x = xpos
		
		# Compute turning
		motors.left_motor.position -= delta_x / 2
		motors.right_motor.position += delta_x / 2
		
		# Compute how far to turn to reach target
		delta_left_pos = ypos - motors.left_motor.position
		delta_right_pos = ypos - motors.right_motor.position
		
		# Compute speed as a function of target distance
		left_speed = clamp(delta_left_pos*2, 720, -720)
		right_speed = clamp(delta_right_pos*2, 720, -720)
		
		# Set motor speed (deg/s for large tachos)
		motors.left_motor.pulses_per_second_sp = left_speed
		motors.right_motor.pulses_per_second_sp = right_speed
finally:
	motors.run = 0
