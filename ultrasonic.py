
# Drive a set distance from a wall!
# Left motor on port B, Right motor on port C.
# Ultrasonic port is auto-detected.
# Ultrasonic must be placed in front of the wheels, *not behind them*.
# If your ultrasonic is behind your wheels, like mine, you can just have
# the robot drive backwards.

import pyev3

left_motor = pyev3.Motor(pyev3.OUTPUT_B)
right_motor = pyev3.Motor(pyev3.OUTPUT_C)

left_motor.reset()
right_motor.reset()

ultrasonic = pyev3.Sensor(type='ev3-uart-30')
ultrasonic.mode = 'US-DIST-IN'

left_motor.run_mode = 'forever'
left_motor.regulation_mode = 'on'

right_motor.run_mode = 'forever'
right_motor.regulation_mode = 'on'

left_motor.run = 1
right_motor.run = 1

target_distance = 8

top_speed = 180

try:
	while True:
		distance = ultrasonic.get_value(0) / 10.0
		turn = top_speed * (distance - target_distance)
		turn = max(-top_speed, min(top_speed, turn))
		print distance, turn
		left_motor.pulses_per_second_sp = top_speed + turn
		right_motor.pulses_per_second_sp = top_speed - turn
finally:
	left_motor.run = 0
	right_motor.run = 0