import time

import cwiid
import pyev3

WAIT_TIME = 0.008 # Seconds 0.008

WHEEL_RATIO_NXT1 = 1.0
WHEEL_RATIO_NXT2 = 0.8
WHEEL_RATIO_RCX = 1.4

KGYROANGLE = 7.5
KGYROSPEED = 1.15
KPOS = 0.07
KSPEED = 0.1

KDRIVE = 0.000
KSTEER = 1.0

EMAOFFSET = 0.0001

TIME_FALL_LIMIT = 1 # Seconds

def clamp(value, lower, upper):
	return min(upper, max(value, lower))

class Gyro:
	def __init__(self):
		self.device = pyev3.Sensor(type='ev3-uart-32')
		self.calibrate()
	
	def calibrate(self):
		self.device.mode = 'GYRO-G&A'
		self.offset = self.device.get_value(0)
		self.get_data(0)
	
	def get_data(self, interval):
		self.speed = self.device.get_value(1)
		self.angle = self.device.get_value(0) - self.offset
		
		return self.speed, self.angle

class Motors:
	def __init__(self, left, right):
		self.left = left
		self.right = right
		left.reset()
		right.reset()
		left.run = 1
		right.run = 1
		
		self.prev_sum = 0
		self.sum = 0
		self.diff = 0
		self.position = 0.0
		self.speed = 0.0
		self.deltas = [0, 0, 0]
		
		self.diff_target = 0
	
	def get_data(self, interval):
		left_position = self.left.position
		right_position = self.right.position
		
		pos_sum = left_position + right_position
		self.diff = left_position - right_position
		
		delta = pos_sum - self.prev_sum
		self.position += delta
		
		self.deltas.append(delta)
		
		self.speed = sum(self.deltas) / (4 * interval)
		
		self.prev_sum = pos_sum
		self.deltas.pop(0)
		
		return self.speed, self.position
	
	def run(self, interval, power, steer_control):
		self.diff_target += steer_control * interval
		
		power_steer = KSTEER * (self.diff_target - self.diff)
		
		left_power = clamp(power + power_steer, -100, 100)
		right_power = clamp(power - power_steer, -100, 100)
		
		self.left.duty_cycle_sp = left_power
		self.right.duty_cycle_sp = right_power

def main(wheel_ratio, left_motor, right_motor):
	print 'press 1+2 on the wiimote now'
	w = cwiid.Wiimote()
	print 'connected'
	w.led = 6
	w.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_BTN
	last_btn_state = 0
	
	gyro = Gyro()
	
	motors = Motors(left_motor, right_motor)
	
	iteration = 0
	avg_interval = 0.01
	start_time = time.time()
	
	motor_pos_ok = start_time
	control_drive = 360
	control_steer = 0
	move = 0
	
	while True:
		gyro.get_data(avg_interval)
		motors.get_data(avg_interval)
		
		motors.position += control_drive * avg_interval * move
		
		power = (KGYROSPEED * gyro.speed \
			+ KGYROANGLE * gyro.angle) \
			/ wheel_ratio \
			+ KPOS * motors.position \
			+ KDRIVE * control_drive * move \
			+ KSPEED * motors.speed
		
		motors.run(avg_interval, power, control_steer)
		
		time.sleep(WAIT_TIME)
		
		now_time = time.time()
		
		iteration += 1
		avg_interval = (now_time - start_time) / iteration
		
		if abs(power) < 100:
			motor_pos_ok = now_time
		elif (now_time - motor_pos_ok) > TIME_FALL_LIMIT:
			raise Exception('fallen')
		
		if not iteration % 100: # execute in 1 of 100 loops
			state = w.state
			
			buttons = state['buttons']
			if buttons != last_btn_state:
				if buttons & cwiid.BTN_2:
					move = 1
				elif buttons & cwiid.BTN_1:
					move = -1
				else:
					move = 0
				last_btn_state = buttons
			
			acc = state['acc']
			tilt = (clamp(acc[1], 95, 145) - 120)/ 25.0 # roughly between -1 and 1
			
			control_steer = -tilt * 180

if __name__ == '__main__':
	left_motor = pyev3.Motor(pyev3.OUTPUT_B)
	right_motor = pyev3.Motor(pyev3.OUTPUT_C)
	
	try:
		main(WHEEL_RATIO_NXT2, left_motor, right_motor)
	finally:
		left_motor.run = 0
		right_motor.run = 0