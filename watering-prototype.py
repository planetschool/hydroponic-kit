### Updates and Changes

'''
Instead of using --break-system-packages, I decided to fully investigate the use
of a virtual environment. I followed the tutorial here: https://docs.python.org/3/tutorial/venv.html

Once up and running within "tutorial-env", I now run "python -m pip install [name of adafruit package]"

We will see how this goes...

Ran into a bunch of errors using the above, then found Adafruit's tutorial addressing the 'pip' issue
here: https://learn.adafruit.com/python-virtual-environment-usage-on-raspberry-pi

Using this tutorial, I am trying to create the venv using the command 'python3 -m venv --system-site-packages venv-plant-watering'

We will see how this goes...

Ran the following:
pip3 install adafruit-circuitpython-ads1x15
pip3 install adafruit-circuitpython-scd4x
pip3 install adafruit-circuitpython-tsl2591



'''






### Overview

'''
This document contains working code for testing all the sensors, the pump, and LCD screen
in our plant watering project. You will need to go through each section and run some 
commands in the terminal to get each sensor's library installed. For sensors you do not wish
to use, simply comment out their section of the code.
'''



### Needed for all hardware

#Listed below are the default I2C addresses for each hardware element in this document

import board
import time
import csv
from time import sleep

i2c_port = 1
pump_address = 0x67
color_address = 0x29
bme_address = 0x77
soil_address = 0x48
co2_address = 0x62
lcd_address = 0x27
light_address = 0x29
i2c = board.I2C()

Sensor_Interval = 5		# Number of seconds between polling the sensor array
data_header = ["Month", "Day", "Year", "Hour", "Minute", "Second"]


### Atlas Pump

'''
1) run "cd ~" and then "git clone https://github.com/AtlasScientific/Raspberry-Pi-sample-code.git"
We learned that this git repostory contains essential code in addition to the sample.

2) Refer to "Raspberry Pi sample code: I2C Mode" instructions that are provided by 
Atlas Scientific, which these steps reference

3) python-smbus and i2c-tools are already bundled with RPiOS

4) I2C mode can be enabled via the RPi dropdown menu 
Preferences > Raspberry Pi Configuration > Interfaces

5) No need to reboot.

6) When you run "sudo i2cdetect -y 1" you should see "67" if your pump is properly connected.
This is a hex value that corresponds to an I2C address of 103.

7) Go into the folder "Raspberry-Pi-sample-code" that was created in Step 1
and copy AtlasI2C.py into the same folder as whatever folder this python file is in.
When you "import AtlasI2C" below, the program will look in the same folder (directory) as 
itself (i.e. the Python file being run) for a Python file named "AtlasI2C.py" 
or it will error and tell you "There is no module named "AtlasI2C"

8) Refer to the EZO-PMP Datas
heet on the Atlas Scientific website for a full list of commands

'''

from AtlasI2C import AtlasI2C

Active_Watering = True
Watering_Interval = 3 	#number of minutes between watering doses to allow time for the soil sensor to react.
Watering_Threshold = 15000	#soil sensor value that decides when the pump activates.
dosing_amount = 10 	#amount of water in milliliters to dispense on each watering dose.


pump = AtlasI2C()
pump.set_i2c_address(int(pump_address))
#pump.write("D,5") 		#the command D stands for "Dispense" followed by an amount in Ml



### LCD Instructions

#The library for the LCD should have downloaded from the 'git clone' command
LCD_On = False

if LCD_On:
	import I2C_LCD_driver

	mylcd = I2C_LCD_driver.lcd()
	mylcd.lcd_display_string("Hello World", 1, 0)



### Color Sensor TCS34725

#In the terminal, run 'sudo pip3 install adafruit-circuitpython-tcs34725 --break-system-packages'
Color_Sensor_On = False

if Color_Sensor_On:
	import adafruit_tcs34725
	light_sensor = adafruit_tcs34725.TCS34725(i2c, int(color_address))
	#print(light_sensor.color_rgb_bytes)
	data_header.extend(["Red Light", "Green Light", "Blue Light"])



### Soil Sensor

#In the terminal, run 'sudo pip3 install adafruit-circuitpython-ads1x15 --break-system-packages'
'''
The soil sensor is our only sensor that is not I2C compatible. Its data is analogue.
Therefore, it has to be run through an ADC (Analogue Digital Converter) since the RPi
does not have a GPIO pin that receives analogue data (as an aside, Arduinos do have an analogue pin).
The ADC boards I got have four channels (A0-A3) and you can connect the data wire from the soil
sensor to any of them, you just need to indicate which port you use in the code. In my code below, "P0"
would change to "P1" if I used A1 instead of A0. With four ports, we could even attache multiple soil sensors
if our planting area gets too big.

The code below is for talking to the ADC. Part of what you need to do is calibrate your soil sensor
so that we know what these values mean. I have some examples of readings I took below.
'''
Soil_Sensor_On = True

if Soil_Sensor_On:
	import adafruit_ads1x15.ads1115 as ADS
	from adafruit_ads1x15.analog_in import AnalogIn
	ads = ADS.ADS1115(i2c)
	soil_sensor = AnalogIn(ads, ADS.P0)
	data_header.append("Soil Moisture")
	#print(soil_sensor.value)

	#Wet soil value = 13866
	#Water value = 8290, 8197, 8205
	#Bone-dry soil value = 17964, 17922, 17907




### BME280 Temp, Pressure, Humidity

#In the terminal run 'sudo pip3 install adafruit-circuitpython-bme280 --break-system-packages'
BME_Sensor_On = False

if BME_Sensor_On:
	from adafruit_bme280 import basic as adafruit_bme280
	import smbus2
	bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, int(bme_address))
	BME_humidity = bme280.humidity
	BME_pressure = bme280.pressure
	BME_temp = bme280.temperature
	data_header.extend(["BME Temperature (*F)", "BME Humidity (%)", "BME Pressure (hPa)"])
	#print("Temp: {}, Pressure: {}, Humidity: {}".format(BME_temp, BME_pressure, BME_humidity))




### CO2 Sensor

#In the terminal, run 'sudo pip3 install adafruit-circuitpython-scd4x --break-system-packages'
#If using a venv (virtual environment), run 'pip3 install adafruit-circuitpython-scd4x'
CO2_Sensor_On = True

if CO2_Sensor_On:
	import adafruit_scd4x as CO2
	CO2_sensor = CO2.SCD4X(i2c, int(co2_address))
	CO2_sensor.start_periodic_measurement()
	print("Waiting for first measurement...")
	data_header.extend(["CO2 Temperature (*F)", "CO2 Humidity (%)", "CO2 PPM"])




### Light Sensor

#In the terminal, run 'sudo pip3 install adafruit-circuitpython-tsl2591 --break-system-packages'
import adafruit_tsl2591 as Light
Light_Sensor_On = True

if Light_Sensor_On:
	Light_sensor = Light.TSL2591(i2c, int(light_address))
	lux = Light_sensor.lux
	visible = Light_sensor.visible		
	IR = Light_sensor.infrared
	data_header.extend(["Brightness (lux)", "Visible Light", "Infrared Light"])
	#print("Brightness: {}, Visible Light: {}, Infrared Light: {}".format(lux, visible, IR))
	
	
if Active_Watering:
	data_header.extend(["Dosed (Boolean)", "Amount Dosed (mL)"])

### The code itself!

#Here I initialize the CO2 sensor and take the first reading
while True:
	
	if CO2_sensor.data_ready:
		print("C02: %d ppm" % CO2_sensor.CO2)
		print("CO2_Temperature: %0.1f *C" % CO2_sensor.temperature)
		print("CO2_Humidity: %0.1f %%" % CO2_sensor.relative_humidity)
		CO2_temp_C = round(CO2_sensor.temperature, 1)
		CO2_humidity = round(CO2_sensor.relative_humidity, 1)
		CO2_CO2 = CO2_sensor.CO2
		break
		
#Once the CO2 sensor is ready, we get things going.

counter = 0
Watering_Interval = Watering_Interval * 60
start_time = "{}-{}-{}_{}:{}".format(time.localtime().tm_mon, time.localtime().tm_mday, time.localtime().tm_year, time.localtime().tm_hour, time.localtime().tm_min)
print("Starting to measure at {}".format(start_time))
with open("data_logger_{}.csv".format(start_time), "w") as data_file:
	datawriter = csv.writer(data_file, delimiter = ",")
	datawriter.writerow(data_header)

while True:
	
	water_dispensed = 0
	data = [time.localtime().tm_mon, time.localtime().tm_mday, time.localtime().tm_year, time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec]
	
	if Color_Sensor_On:
		red = light_sensor.color_rgb_bytes[0]
		green = light_sensor.color_rgb_bytes[1]
		blue = light_sensor.color_rgb_bytes[2]
		print("R:" + str(red) + " G:" + str(green) + " B:" + str(blue))
		data.append([red, green, blue])
	
	if Soil_Sensor_On:
		soil_value = soil_sensor.value
		print("Soil Moist:%d" % soil_value)
		data.append(soil_value)
		
	if BME_Sensor_On:
		BME_humidity = round(bme280.humidity, 1)
		BME_pressure = round(bme280.pressure, 1)
		BME_temp = round(bme280.temperature, 1)
		print("BME_Temp: {}, BME_Pressure: {}, BME_Humidity: {}".format(BME_temp, BME_pressure, BME_humidity))
		data.append([BME_temp, BME_humidity, BME_pressure])
		
	if CO2_Sensor_On:
		if CO2_sensor.data_ready:
			CO2_temp_C = round(CO2_sensor.temperature, 1)
			CO2_humidity = round(CO2_sensor.relative_humidity, 1)
			CO2_CO2 = CO2_sensor.CO2
		CO2_temp_F = round(CO2_temp_C * (9/5) + 32, 1) 
		print("CO2_Temp: {} *F".format(CO2_temp_F))
		print("CO2: {} ppm".format(CO2_CO2))
		print("CO2_Humid: {} %".format(CO2_humidity))
		data.extend([CO2_temp_F, CO2_humidity, CO2_CO2])
		
	if Light_Sensor_On:
		lux = round(Light_sensor.lux, 1)
		visible = Light_sensor.visible
		IR = Light_sensor.infrared
		print("Brightness: {}, Visible Light: {}, Infrared Light: {}".format(lux, visible, IR))
		data.extend([lux, visible, IR])
	
	if Active_Watering:
		if soil_value > Watering_Threshold and counter % Watering_Interval == 0:
			pump.write("D,{}".format(dosing_amount)) 
			water_dispensed = 1
			print("Soil is dry, watered {} mL.".format(dosing_amount))
			
		counter = counter + Sensor_Interval
		data.append(water_dispensed)
		
		if water_dispensed == 0:
			data.append(0)
		
		elif water_dispensed == 1:
			data.append(dosing_amount)

	
	with open("data_logger_{}.csv".format(start_time), "a") as data_file:
		datawriter = csv.writer(data_file, delimiter = ",")
		datawriter.writerow(data)
	
	print(counter)
		
	if LCD_On:
		mylcd.lcd_clear()
		if Light_Sensor_On:
			mylcd.lcd_clear()
			mylcd.lcd_display_string("Bright: {} Lux".format(lux), 1, 0)
			mylcd.lcd_display_string("IR: {} , Vis: {}".format(IR, visible), 2, 0)
			sleep(2)
		if BME_Sensor_On:
			mylcd.lcd_clear()
			mylcd.lcd_display_string("Press: {} hPa".format(BME_pressure), 1, 0)
			mylcd.lcd_display_string("Humid: {} %".format(BME_humidity), 2, 0)
			sleep(2)
		if CO2_Sensor_On:
			mylcd.lcd_clear()
			mylcd.lcd_display_string("Temp: {} *F".format(CO2_temp_F), 1, 0)
			mylcd.lcd_display_string("CO2: {} ppm".format(CO2_CO2), 2, 0) 
			sleep(2)
			mylcd.lcd_clear()
			mylcd.lcd_display_string("Humid: {} %".format(CO2_humidity), 1, 0)
			sleep(2)
		if Soil_Sensor_On:
			mylcd.lcd_clear()
			mylcd.lcd_display_string("Soil Moist:{}".format(soil_value), 1, 0)
			sleep(2)
		if Color_Sensor_On:
			mylcd.lcd_clear()
			mylcd.lcd_display_string("R:" + str(red) + " G:" + str(green) + " B:" + str(blue), 1, 0)
			sleep(2)
			
	sleep(Sensor_Interval)
