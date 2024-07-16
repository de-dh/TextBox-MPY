# TextBox-MPY

## Description
<img align="right"  src="doc/OLED.jpg" width="150" height="auto" />

TextBox is used to create simple **boxes with a caption and multiple lines of text** on SSD1306-OLED / ST7735R-TFT displays using FrameBuffer-derived drivers in micropython on Raspberry Pi Pico.
Each text line is rendered in an individual FrameBuffer. 
This enables **fast updating** of the screen without flickering.

Text lines can easily be added, updated and deleted. 
Multiple TextBoxes can be created on one screen.

I use this for all my projects where I need to display text on an OLED / TFT Display.
This way, I don't have to mess around with graphic functions again and again if I want to display text / data.

## Usage

### Installation

All neccessary files are located in the `/src` folder.
The `/src/lib` folder contains the TextBox class for import and a SSD1306-OLED-Driver and a ST7735R-TFT-Driver.
The `/lib` folder needs to be copied onto the RPI using Thonny. 
The other files in the `/src` directory are examples demonstrating the use of TextBox on OLED / TFT displays.

Import TextBox and drivers in your programm:
```python
import ssd1306 # OLED driver
from ST7735R import ST7735R # TFT driver
from TextBox import TextBox, TextBoxOLED, TextBoxTFT # TextBox
from machine import Pin, I2C, SPI # Needed to initialize the displays
```

### Initialization

First, the displays need to be initialized to obtain a display object.
I use a simple class for that.

<details>
<summary>Initialize OLED Display</summary>

```python
"""OLED Display
VCC --> VBUS Pin 36 (3.3V)
GND --> Pin Nr. 3"""
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

    # Returns display object. 
    def display_object(self):
        return self.display
    
    def clear(self):
        self.display.fill(0)
        self.display.show()
```

</details>


<details>
<summary>Initialize TFT Display</summary>

```python
"""TFT Display
VCC --> VBUS Pin 36 (3.3V)
GND --> Pin Nr. 3"""
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
```

</details>


## Examples

<img align="left"  src="doc/TFT_OLED_Overview.jpg" width="300" height="auto" />
