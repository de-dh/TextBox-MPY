from machine import SPI, Pin
from ST7735R import ST7735R
from TextBox import TextBox, TextBoxTFT
import time
import gc
import random




"""
TFT Display
VCC --> VBUS Pin 36 (3.3V)
GND --> Pin Nr. 3
"""
TFT_MISO_PIN = None # --> not needed
TFT_CLK_PIN = const(2)  # --> SCK
TFT_MOSI_PIN = const(3) # --> SDA
TFT_RST_PIN = const(4) # --> RES
TFT_DC_PIN = const(5) # --> DC
TFT_CS_PIN = const(6) # --> CS
TFT_BLK_PIN = const(7) # --> Backlight

class TFT():
    def __init__(self, clk, mosi, miso, cs, dc, rst, blk):
        self.width = 128
        self.height = 160
        
        self.dc = Pin(dc, Pin.OUT, Pin.PULL_DOWN)
        self.cs = Pin(cs, Pin.OUT, Pin.PULL_DOWN)
        self.rst = Pin(rst, Pin.OUT, Pin.PULL_DOWN)
        
        self.blk = Pin(blk, Pin.OUT, Pin.PULL_UP)
        
        # Turn on backlight.
        # Brightness may be controlled by PWM.
        self.blk(1)
        
        self.spi = SPI(0, baudrate = 15625000, polarity = 0, phase = 0, sck = Pin(clk),
                   mosi = Pin(mosi), miso = miso)
    
        self.display = ST7735R(self.spi, self.cs, self.dc, self.rst,
                   height = self.height, width = self.width)
        
    # Returns display object.    
    def display_object(self):
        return self.display
    
    def clear(self):
        self.display.fill(0)
        self.display.show()
        





try:
    # Initialize TFT display.
    TFT = TFT(clk = TFT_CLK_PIN, mosi = TFT_MOSI_PIN, miso = TFT_MISO_PIN,
                     cs = TFT_CS_PIN, dc = TFT_DC_PIN, rst = TFT_RST_PIN,
                     blk = TFT_BLK_PIN)
    
    # Initialize first TextBox and pass display handle.
    BOX_1 = TextBoxTFT(TFT.display_object(), caption = 'Ambient Data', pos = 5,
                        fg_color = (0, 255, 0), bg_color = ((0,) * 3))
    
    
    # Add lines and call show() before any manipulation.
    lines = [BOX_1.add_line('Line ' + str(i+1)) for i in range(5)]
    BOX_1.show()
    
    
    """ Start Demo """
    # Invert color of each line
    for line in lines:
        BOX_1.invert_color(line)
        time.sleep(0.1)
        BOX_1.invert_color(line)
        time.sleep(0.1)
    
    # Update lines with random values
    for line in lines:
        BOX_1.update_line(line, str(random.randint(1000, 99999)))
        time.sleep(0.1)
    
    # Delte lines
    for line in reversed(lines):
        BOX_1.delete_line(line)
        time.sleep(0.1)
    
    # prevent ram overload
    del lines
    gc.collect()
    
    # Add lines again    
    new_lines = []
    for i in range(5):
        new_line = BOX_1.add_line('New line: ' + str(i+1))
        new_lines.append(new_line)
        BOX_1.show()
        time.sleep(0.2)    
    
    
    # Calculate position of second box.
    # Place it five pixel below first box.
    pos_2 = BOX_1.box_y + BOX_1.box_h + 5
    
    # Initialize second TextBox.
    BOX_2 = TextBoxTFT(TFT.display_object(), caption = 'Box 2', pos = pos_2,
                        fg_color = (255, 255, 255), bg_color = (0, 0, 255))    
    
    # Add lines and call show() before any manipulation.
    lines = [BOX_2.add_line('Box 2, Line ' + str(i+1)) for i in range(5)]
    BOX_2.show()
    time.sleep(1)
    
    # Delete last line of Box1
    BOX_1.delete_line(new_lines[-1])
    time.sleep(1)
    
    # Adjust position of Box2
    BOX_2.set_pos(BOX_1.box_y + BOX_1.box_h + 5)
    time.sleep(1)
    
    # Add line again to Box1
    another_line = BOX_1.add_line('Another line')
    BOX_1.show() # Draws box and calculates height
                 # Box1 is covered partially by Box2
    time.sleep(1)
    
    # Adjust pos of Box2
    BOX_2.set_pos(BOX_1.box_y + BOX_1.box_h + 5)
    
    # Show Box1 again, now completely visible
    BOX_1.show()
    
    
   
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print('Programm terminated by Thonny.')
finally:
    # Clear display on exit
    TFT.clear()