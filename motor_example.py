import pyev3

my_motor = pyev3.Motor(pyev3.OUTPUT_B)
my_motor.position = 0
my_motor.run_mode = 'position'
my_motor.stop_mode = 'hold'
my_motor.regulation_mode = 'on'
my_motor.pulses_per_second_sp = 360
my_motor.position_sp = 360
my_motor.run = 1

while True:
	print my_motor.position