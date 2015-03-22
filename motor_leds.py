import pyev3

led_green_left = pyev3.LED('ev3:green:left')
led_green_right = pyev3.LED('ev3:green:right')
led_red_left = pyev3.LED('ev3:red:left')
led_red_right = pyev3.LED('ev3:red:right')

max_brightness = led_green_left.max_brightness

led_green_left.brightness = max_brightness
led_green_right.brightness = max_brightness

tacho = pyev3.Motor()
print "Using motor {}".format(tacho.port_name)

tacho.reset()

tacho.position = 90
adjusted = tacho.position
last_position = adjusted

while True:
	while adjusted == last_position:
		position = tacho.position
		adjusted = max(0, min(position, 180))
		if adjusted != position:
			tacho.position = adjusted
	brightness = max_brightness * adjusted / 180
	print adjusted, brightness
	led_red_left.brightness = brightness
	led_red_right.brightness = brightness
	last_position = adjusted