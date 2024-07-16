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
**The other files in the `/src` directory are complete examples demonstrating the use of TextBox on OLED / TFT displays.**

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

Initialize display and pass the display object to TextBox.
Initialization is slightly different for OLED and TFT.


```python
    """ Use with OLED display:
    Initialize OLED display, then initialize first TextBox and pass display handle. """
    OLED = OLED(DISPLAY_SCL_PIN, DISPLAY_SDA_PIN)
    BOX_1 = TextBoxOLED(OLED.display_object(), caption = 'Box 1', pos = 0)


    """ Use with TFT display:
    Initialize TFT display, then initialize first TextBox and pass display handle. """
    TFT = TFT(clk = TFT_CLK_PIN, mosi = TFT_MOSI_PIN, miso = TFT_MISO_PIN,
                     cs = TFT_CS_PIN, dc = TFT_DC_PIN, rst = TFT_RST_PIN,
                     blk = TFT_BLK_PIN)

    BOX_1 = TextBoxTFT(TFT.display_object(), caption = 'Ambient Data', pos = 5,
                        fg_color = (0, 255, 0), bg_color = ((0,) * 3))
```

After initialization, the same commands apply to the OLED and the TFT version.


### Add lines

When creating lines, a handle is returned representing each line.
The handle can be used to address individual lines for later updates or deletion.
After all lines are added, call the `show()` command to draw the box.
The dimensions of the box are calculated automatically.

```python
    """ Same commands for use with OLED and TFT displays """
    line_1 = BOX_1.add_line('A')
    line_2 = BOX_1.add_line('B')
    BOX_1.show()
```

### Update lines

Call `TextBox.update_line(line_handle, 'New Text')` to update the content of a line or `TextBox.update_caption('New Caption')`.
Only the FrameBuffer of the line is updated to enhance performance. An update of the whole screen is not neccessary.

```python
    """ Same commands for use with OLED and TFT displays """
    BOX_1.update_line(line_1, 'New Text')
    BOX_1.update_caption('New Caption')
```

### Delete lines

Call `TextBox.delete_line(line_handle)` to delete a line. 
The size of the TextBox is adjusted automatically and the order of the remaining lines is preserved.
This causes the whole TextBox to be redrawn.

```python
    """ Same commands for use with OLED and TFT displays """
    BOX_1.delete_line(line_1)
```

### Invert lines

Call `TextBox.invert_color(line_handle)` to swap the foreground and the background color of a text line. 
This can be used to highlight a line.
 
```python
    """ Same commands for use with OLED and TFT displays """
    BOX_1.invert_line(line_1)
```

### Box position and height

The vertical position and the height of a TextBox can be obtained via `TextBox.box_y` and `TextBox.box_h `.
This can be used to position a second box underneath an existing box.
 
```python
    """ Same commands for use with OLED and TFT displays """
    # Calculate position of second box.
    # Place it five pixel below first box.
    pos_2 = BOX_1.box_y + BOX_1.box_h + 5
```

## Examples

<img align="left"  src="doc/TFT_OLED_Overview.jpg" width="300" height="auto" />
