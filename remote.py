import socket

import pyev3

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

motors = Motors(pyev3.OUTPUT_B, pyev3.OUTPUT_C)

motors.reset()
motors.regulation_mode = "on"
motors.pulses_per_second_sp = 0
motors.run = 1

arm = pyev3.Motor(pyev3.OUTPUT_A)
arm.reset()
arm.run_mode = "position"
arm.position_sp = 0
arm.duty_cycle_sp = 100
arm.stop_mode = 'hold'

HOST = '' # Symbolic name meaning all available interfaces
PORT = 50008 # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

try:
	while True:
		conn, addr = s.accept()
		print 'Connected by', addr
		while True:
			data = conn.recv(1024)
			# conn.sendall(data)
			if not data: break
			data = data.split(" ")
			print data
			try:
				if data[0] == 'motor':
					if data[1] == 'left':
						motors.left_motor.pulses_per_second_sp = data[2]
					elif data[1] == 'right':
						motors.right_motor.pulses_per_second_sp = data[2]
				if data[0] == 'arm':
					arm.run = 0
					arm.position_sp = data[1]
					arm.run = 1
			except: pass
finally:
	conn.close()
	s.close()
	motors.reset()
