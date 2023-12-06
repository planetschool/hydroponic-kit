
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

pump_address = 103
light_address = 0x29
bme_address = 0x77
soil_address = 0x48
co2_address = 0x62
lcd_address = 0x27

from AtlasI2C import AtlasI2C

pump = AtlasI2C()

pump.set_i2c_address(pump_address)
#pump.write("D,5") 		#the command D stands for "Dispense" followed by an amount in Ml


### LCD Instructions

import I2C_LCD_driver
from time import *

mylcd = I2C_LCD_driver.lcd()
#mylcd.lcd_display_string("Hello World", 1, 0)


### Color Sensor TCS34725

import board
import adafruit_tcs34725


i2c = board.I2C()
light_sensor = adafruit_tcs34725.TCS34725(i2c)
print(light_sensor.color_rgb_bytes)

### BME280 Temp, Pressure, Humidity
'''

import bme280
import smbus2

port = 1
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)
bme280_data = bme280.sample(bus,address)
humidity = bme280_data.humidity
pressure = bme280_data.pressure
temp = bme280_data.temperature

print(humidity, pressure, temp)
'''

### Soil Sensor

#In the terminal, run 'sudo pip3 install adafruit-circuitpython-ads1x15 --break-system-packages'

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
ads = ADS.ADS1115(i2c)
soil_sensor = AnalogIn(ads, ADS.P0)
print(soil_sensor.value)

#Wet soil value = 13866


### CO2 Sensor

#In the terminal, run 'sudo pip3 install adafruit-circuitpython-scd4x --break-system-packages'

import adafruit_scd4x as CO2
CO2_sensor = CO2.SCD4X(i2c)
print("Serial number of the CO2 sensor: ", [hex(i) for i in CO2_sensor.serial_number])

CO2_sensor.start_periodic_measurement()
print("Waiting for first measurement...")
'''
while True:
	if CO2_sensor.data_ready:
		print("C02: %d ppm" % CO2_sensor.CO2)
		print("Temperature: %0.1f *C" % CO2_sensor.temperature)
		print("Humidity: %0.1f %%" % CO2_sensor.relative_humidity)
		sleep(1)
'''
### The code itself!

print(board.I2C())

while True:
	mylcd.lcd_clear()
	red = light_sensor.color_rgb_bytes[0]
	green = light_sensor.color_rgb_bytes[1]
	blue = light_sensor.color_rgb_bytes[2]
	print("Red: " + str(red) + ", Green: " + str(green) + ", Blue: " + str(blue))
	mylcd.lcd_display_string("R:" + str(red) + " G:" + str(green) + " B:" + str(blue), 1, 0)
	sleep(15)


