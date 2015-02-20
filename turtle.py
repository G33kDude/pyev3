import pyev3

class Motors(object):
	def __init__(self, left_motor_port, right_motor_port):
		object.__setattr__(self, 'left_motor', pyev3.Motor(left_motor_port))
		object.__setattr__(self, 'right_motor', pyev3.Motor(right_motor_port))
		object.__setattr__(self, 'flip_flop', False)
	
	def __getattr__(self, attr):
		return self.left_motor.__getattr__(attr)
	
	def __setattr__(self, attr, value):
		self.left_motor.__setattr__(attr, value)
		self.right_motor.__setattr__(attr, value)
	
	def even_run(self):
		object.__setattr__(self, 'flip_flop', not self.flip_flop)
		if self.flip_flop:
			self.left_motor.__setattr__('run', 1)
			self.right_motor.__setattr__('run', 1)
		else:
			self.right_motor.__setattr__('run', 1)
			self.left_motor.__setattr__('run', 1)

class Turtle(object):
	def __init__(self, left_motor_port, right_motor_port, gyro_port):
		self.motors = Motors(left_motor_port, right_motor_port)
		self.motors.regulation_mode = 'on'
		self.gyro = pyev3.Sensor(gyro_port)
		self.gyro_target = self.gyro.get_value(0)
	
	def move(self, distance, speed=200):
		self.motors.run_mode = 'position'
		self.motors.position = 0
		self.motors.position_sp = distance
		self.motors.pulses_per_second_sp = speed
		self.motors.run = 1
		while self.motors.run == 1:
			pass
	
	def pivot_degrees(self, degrees, speed=200):
		self.motors.run_mode = 'forever'
		self.gyro_target += degrees
		while True:
			gyro_pos = self.gyro.get_value(0)
			# The speed is proportional to distance from target gyro position.
			# It never drops below 1/4 of target_speed
			# speed = target_speed * (1 - float(delta*3)/(degrees*4))
			if gyro_pos > self.gyro_target:
				self.motors.left_motor.pulses_per_second_sp = -speed
				self.motors.right_motor.pulses_per_second_sp = speed
			elif gyro_pos < self.gyro_target:
				self.motors.left_motor.pulses_per_second_sp = speed
				self.motors.right_motor.pulses_per_second_sp = -speed
			else:
				break
			self.motors.run = 1
			# self.motors.even_run()
		self.motors.run = 0

def main(turtle, instructions):
	print turtle.gyro.get_value(0)
	for instruction in instructions:
		print instruction
		if instruction == 'S':
			turtle.move(360)
		elif instruction == 'L':
			turtle.pivot_degrees(-90)
		elif instruction == 'R':
			turtle.pivot_degrees(90)
	print turtle.gyro.get_value(0)

if __name__ == '__main__':
	myturtle = Turtle(pyev3.OUTPUT_B, pyev3.OUTPUT_C, pyev3.INPUT_1)
	try:
		main(myturtle, 'SLLLRLSLSLSRLSLLLLS')
	finally:
		myturtle.motors.left_motor.reset()
		myturtle.motors.right_motor.reset()

