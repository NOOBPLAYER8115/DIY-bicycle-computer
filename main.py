import time
import digitalio
import board
import busio
import displayio
import i2cdisplaybus
import terminalio
from adafruit_display_text import label
import adafruit_displayio_sh1106

rotations_per_sec_scr = ''
rotation_count = 0
#reed switch pin
reed = digitalio.DigitalInOut(board.GP12)
reed.direction = digitalio.Direction.INPUT

# Release any existing display resources
displayio.release_displays()

# Initialize I2C with a slower frequency (100kHz) for better stability
i2c = busio.I2C(scl=board.GP5, sda=board.GP4, frequency=1000000)

# Set up the I2C display bus
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)

# Display dimensions
WIDTH = 130
HEIGHT = 64

# Initialize the SH1106 display
display = adafruit_displayio_sh1106.SH1106(
    display_bus, width=WIDTH, height=HEIGHT
)

while True:
    if rotation_count == 0:
        if reed.value == True:
            time_since_true1 = time.monotonic_ns()
            rotation_count = 1
    time.sleep(0.05)
    if rotation_count == 1:
        if reed.value == True:
            time_since_true2 = time.monotonic_ns()
            rotation_count = 0
            timing_since_rotation_ns = time_since_true2 - time_since_true1
            timing_since_rotation_ms = timing_since_rotation_ns / 1000000
            timing_since_rotation_sec = timing_since_rotation_ms / 1000
            rotations_per_sec = 1 / timing_since_rotation_sec
            rotations_per_min = rotations_per_sec * 60
            print(timing_since_rotation_ms)
            rotations_per_sec_scr = (f'{rotations_per_sec} rps')
            print(rotations_per_sec_scr)
            
        else:
            pass
    while reed.value == False:
        pass
    
    # Create a root display group
    splash = displayio.Group()
    display.root_group = splash
    
    # Draw a simple text label on the screen
    rps = label.Label(terminalio.FONT, text=rotations_per_sec_scr, color=0xFFFFFF, x=14, y=10)
    splash.append(rps)

