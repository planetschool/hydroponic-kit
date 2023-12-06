
### Pump Instructions

'''
1) run "cd ~" and then "git clone https://github.com/AtlasScientific/Raspberry-Pi-sample-code.git"
We learned that this git repostory contains essential code in addition to the sample.

2) Refer tp "Raspberry Pi sample code: I2C Mode" instructions that are provided by 
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


### Needed for all sensors

import board
from time import *

i2c_port = 1
pump_address = 0x63
light_address = 0x29
bme_address = 0x77
soil_address = 0x48
co2_address = 0x62
lcd_address = 0x27
i2c = board.I2C()



### Atlas Pump

from AtlasI2C import AtlasI2C

pump = AtlasI2C()

pump.set_i2c_address(int(pump_address))
#pump.write("D,5") 		#the command D stands for "Dispense" followed by an amount in Ml



### LCD Instructions

import I2C_LCD_driver

mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_display_string("Hello World", 1, 0)



### Color Sensor TCS34725

import adafruit_tcs34725

light_sensor = adafruit_tcs34725.TCS34725(i2c, int(light_address))
#print(light_sensor.color_rgb_bytes)



### BME280 Temp, Pressure, Humidity

#In the terminal run 'pip3 install adafruit-circuitpython-bme280'

from adafruit_bme280 import basic as adafruit_bme280
import smbus2

bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, int(bme_address))

BME_humidity = bme280.humidity
BME_pressure = bme280.pressure
BME_temp = bme280.temperature
#print("Temp: {}, Pressure: {}, Humidity: {}".format(BME_temp, BME_pressure, BME_humidity))



### Soil Sensor
'''
In the terminal, run 'sudo pip3 install adafruit-circuitpython-ads1x15 --break-system-packages'

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

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
ads = ADS.ADS1115(i2c)
soil_sensor = AnalogIn(ads, ADS.P0)
#print(soil_sensor.value)

#Wet soil value = 13866
#Water value = 8290, 8197, 8205
#Bone-dry soil value = 17964, 17922, 17907



### CO2 Sensor

#In the terminal, run 'sudo pip3 install adafruit-circuitpython-scd4x --break-system-packages'

import adafruit_scd4x as CO2
CO2_sensor = CO2.SCD4X(i2c, int(co2_address))
CO2_sensor.start_periodic_measurement()
print("Waiting for first measurement...")



### The code itself!

#Here I initialize the CO2 sensor and take the first reading
while True:
	
	if CO2_sensor.data_ready:
		print("C02: %d ppm" % CO2_sensor.CO2)
		print("CO2_Temperature: %0.1f *C" % CO2_sensor.temperature)
		print("CO2_Humidity: %0.1f %%" % CO2_sensor.relative_humidity)
		CO2_temp = CO2_sensor.temperature
		CO2_humidity = CO2_sensor.relative_humidity
		CO2_CO2 = CO2_sensor.CO2
		break
		
while True:
	mylcd.lcd_clear()
	

	red = light_sensor.color_rgb_bytes[0]
	green = light_sensor.color_rgb_bytes[1]
	blue = light_sensor.color_rgb_bytes[2]
	soil_value = soil_sensor.value
	
	print("R:" + str(red) + " G:" + str(green) + " B:" + str(blue))
	print("Soil Moist:%d" % soil_value)
	mylcd.lcd_display_string("R:" + str(red) + " G:" + str(green) + " B:" + str(blue), 1, 0)
	mylcd.lcd_display_string("Soil Moist:{}".format(soil_value), 2, 0)
	sleep(2)
	
	if CO2_sensor.data_ready:
		CO2_temp = CO2_sensor.temperature
		CO2_humidity = CO2_sensor.relative_humidity
		CO2_CO2 = CO2_sensor.CO2
	
	print("CO2_Temp: {} *C".format(CO2_temp))
	print("CO2: {} ppm".format(CO2_CO2))
	mylcd.lcd_clear()
	mylcd.lcd_display_string("Temp: {} *C".format(CO2_temp), 1, 0)
	mylcd.lcd_display_string("CO2: {} ppm".format(CO2_CO2), 2, 0) 
	sleep(2)
	
	print("CO2_Humid: {} %".format(CO2_humidity))
	mylcd.lcd_clear()
	mylcd.lcd_display_string("Humid: {} %".format(CO2_humidity), 2, 0)
	sleep(2)
	
	BME_humidity = bme280.humidity
	BME_pressure = bme280.pressure
	BME_temp = bme280.temperature
	print("BME_Temp: {}, BME_Pressure: {}, BME_Humidity: {}".format(BME_temp, BME_pressure, BME_humidity))
	sleep(2)
