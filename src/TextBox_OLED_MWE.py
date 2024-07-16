from machine import Pin, I2C
import ssd1306
from TextBox import TextBox, TextBoxOLED
import time


"""
Minimal working example initializing a TextBox
on a SSD1306 128 * 64 OLED Display



OLED Display
VCC --> VBUS Pin 36 (3.3V)
GND --> Pin Nr. 3
"""

DISPLAY_SDA_PIN = const(26)
DISPLAY_SCL_PIN = const(27)
DISPLAY_I2C_INSTANCE = const(1)

class OLED:
    def __init__(self, scl_pin, sda_pin):
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        
        self.width  = 128
        self.height = 64
        
        # Make sure to use the correct I2C instance (0 or 1)
        # according to pin map
        self.i2c = I2C(DISPLAY_I2C_INSTANCE,scl=Pin(self.scl_pin),
                       sda=Pin(self.sda_pin), freq = 2000000)
        
        self.display = ssd1306.SSD1306_I2C(self.width, self.height, self.i2c)
        self.clear()
    
    def display_object(self):
        return self.display
    
    def clear(self):
        self.display.fill(0)
        self.display.show()




try:
    # Initialize OLED display.
    OLED = OLED(DISPLAY_SCL_PIN, DISPLAY_SDA_PIN)
    
    # Initialize first TextBox and pass display handle.
    BOX_1 = TextBoxOLED(OLED.display_object(), caption = 'Box 1', pos = 0)
    
    # Add lines and call show() before any manipulation.
    line_1 = BOX_1.add_line('A')
    BOX_1.show()
    

    
    while True:
        time.sleep(1)
        
        
except KeyboardInterrupt:
    print('Programm terminated by Thonny.')
finally:
    # Clear display on exit
    OLED.clear()