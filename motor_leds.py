import pyev3

led_green_left = pyev3.LED('ev3:green:left')
led_green_right = pyev3.LED('ev3:green:right')
led_red_left = pyev3.LED('ev3:red:left')
led_red_right = pyev3.LED('ev3:red:right')

led_green_left.brightness = 100
led_green_right.brightness = 100

tacho = pyev3.Motor(pyev3.OUTPUT_B)
tacho.reset()

tacho.position = 90

while True:
	position = tacho.position
	adjusted = max(0, min(position, 180))
	if adjusted != position:
		tacho.position = adjusted
	brightness = 100 * adjusted / 180
	print adjusted, brightness
	led_red_left.brightness = brightness
	led_red_right.brightness = brightness