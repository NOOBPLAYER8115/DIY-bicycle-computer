import time
import math
import digitalio
import board
import busio
import displayio
import i2cdisplaybus
import terminalio
from adafruit_display_text import label
import adafruit_displayio_sh1106
import adafruit_bmp280

#definitions
rotations_per_sec_scr = ''
rotation_count = 0
time_since_true1 = 0
time_since_true2 = 0
wheel_diameter_cm = 60

rotations_per_min = 0
rotations_per_sec = 0
timing_since_rotation_sec = 0
timing_since_rotation_ms = 0
timing_since_rotation_ns = 9999000000000
stand_still_value = 0
sleep_value = 0
#circumference calc
wheel_circumference_cm = wheel_diameter_cm * math.pi
wheel_circumference_m = wheel_circumference_cm / 100
print(wheel_circumference_m)

#reed switch pin
reed = digitalio.DigitalInOut(board.GP12)
reed.direction = digitalio.Direction.INPUT

# Release any existing display resources
displayio.release_displays()

# Initialize I2C at 1MHZ
i2c = busio.I2C(scl=board.GP5, sda=board.GP4, frequency=1000000)

#bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
# Set up the I2C bus
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
bmp280.sea_level_pressure = 1007.0
# Display dimensions
WIDTH = 130
HEIGHT = 64

# Initialize the SH1106 display
display = adafruit_displayio_sh1106.SH1106(
    display_bus, width=WIDTH, height=HEIGHT
)
#display group
splash = displayio.Group()
display.root_group = splash

#ui elements
stripe = label.Label(terminalio.FONT, text="___________", color=0xFFFFFF, x=0, y=34, scale=2)
stripe2 = label.Label(terminalio.FONT, text="________/", color=0xFFFFFF, x=0, y=7, scale=1)
stripe3 = label.Label(terminalio.FONT, text="____________________", color=0xFFFFFF, x=0, y=48, scale=1)
stripe4 = label.Label(terminalio.FONT, text="\\", color=0xFFFFFF, x=59, y=59, scale=1)
stripe5 = label.Label(terminalio.FONT, text="|", color=0xFFFFFF, x=116, y=59, scale=1)
#telemetry
alt = label.Label(terminalio.FONT, text="0 M", color=0xFFFFFF, x=5, y=60)
temp = label.Label(terminalio.FONT, text="0 C", color=0xFFFFFF, x=5, y=5)
rpm = label.Label(terminalio.FONT, text="0 RPM", color=0xFFFFFF, x=85, y=60)
km_h =  label.Label(terminalio.FONT, text="0km/h", color=0xFFFFFF, x=5, y=28, scale=2)

splash.append(rpm)
splash.append(km_h)
splash.append(temp)
splash.append(alt)
splash.append(stripe)
splash.append(stripe2)
splash.append(stripe3)
splash.append(stripe4)
splash.append(stripe5)
#screen refresh function and rotation calc
def screen_refresh_and_calc():
    
    #rotation calculation
    timing_since_rotation_ms = timing_since_rotation_ns / 1000000
    timing_since_rotation_sec = timing_since_rotation_ms / 1000
    rotations_per_sec = 1 / timing_since_rotation_sec
    rotations_per_min = rotations_per_sec * 60
    meters_per_sec = wheel_circumference_m * rotations_per_sec
    kilometers_an_hour = meters_per_sec * 3.6
    kilometers_an_hour_round = round(kilometers_an_hour, 2)
    #print(f'{meters_per_sec} m/s')
    
    timing_since_rotation_ms_round = round(timing_since_rotation_ms)
    rotations_per_min_round = round(rotations_per_min)
    
    #display group
    #splash = displayio.Group()
    #display.root_group = splash
    
    #text
    timing_since_rotation_ms_scr = (f'{timing_since_rotation_ms_round} ms')
    rotations_per_min_scr = (f'{rotations_per_min_round} rpm')
    
    
    #draw text
    #stripe for speed
    stripe.text = f"___________"
    #stripe for temperature
    stripe2.text = f"________/"
    #stripe for alt and rpm
    stripe3.text = f"____________________"
    stripe4.text = f"\\"
    stripe5.text = f"|"
    #telemetry
    altitude = round(bmp280.altitude, 2)
    alt.text = f"{altitude} M"
    temperature = round(bmp280.temperature, 2)
    temp.text = f"{temperature} C"
    rpm.text = f"{rotations_per_min_round} RPM"
    km_h.text = f"{kilometers_an_hour_round}km/h"

# Create a root display group
#splash = displayio.Group()
#display.root_group = splash

# Draw a simple text label on the screen
#textttr = "Pico + SH1106\nCircuitPython 10"
#text_area = label.Label(terminalio.FONT, text=textttr, color=0xFFFFFF, x=14, y=24)
#splash.append(text_area)


screen_refresh_and_calc()
#loop
while True:
    sleep_value_used = sleep_value
    stand_still_value_used = stand_still_value
    if rotation_count == 0:
        if reed.value == True:
            time_since_true1 = time.monotonic_ns()
            rotation_count = 1
            if time_since_true2 == 0:
                pass
            else:
                timing_since_rotation_ns = time_since_true1 - time_since_true2
                screen_refresh_and_calc()
                #print(1)
                #print(timing_since_rotation_ms)
            while reed.value == True:
                time.sleep(0.05)
                if stand_still_value_used > 50:
                    timing_since_rotation_ns = 9999000000000
                    screen_refresh_and_calc()
                    stand_still_value_used = 0
                else:
                    stand_still_value_used += 1
                    pass
            stand_still_value_used = 0
        
    if rotation_count == 1:
        if reed.value == True:
            time_since_true2 = time.monotonic_ns()
            rotation_count = 0
            timing_since_rotation_ns = time_since_true2 - time_since_true1
            #print(2)
            #print(timing_since_rotation_ms)
            screen_refresh_and_calc()
            while reed.value == True:
                time.sleep(0.05)
                if stand_still_value_used > 50:
                    timing_since_rotation_ns = 9999000000000
                    screen_refresh_and_calc()
                    stand_still_value_used = 0
                else:
                    stand_still_value_used += 1
                    pass
            stand_still_value_used = 0
            
            
    while reed.value == False:
        time.sleep(0.05)
        if stand_still_value_used > 50:
            timing_since_rotation_ns = 9999000000000
            screen_refresh_and_calc()
            stand_still_value_used = 0
        else:
            stand_still_value_used += 1
            pass
        
    