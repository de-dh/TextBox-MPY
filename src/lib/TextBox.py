from framebuf import FrameBuffer, MONO_VLSB, RGB565
import gc

"""
V2 - 23.05.2025

Creates a full-width TextBox on a FrameBuffer-driven display.
The TextBox has a caption and it can have multiple lines containing text.
The height of the TextBox is adjusted to fit the lines of text.
Each text line is drawn in its own FrameBuffer which enables fast
updating of the text without flickering of the display.
I have tested this on a SSD1306 OLED Display and a ST7735R-driven
TFT display. Use subclasses acording to the display:

    TextBoxTFT - ST7735R-driven RGB 128 * 160 TFT display
    TextBoxOLED - SSD1306 128 * 64 OLED Display
        --> Display width and height can be adjusted in class definition
        
    Initialization:
    
        MyBox = TextBoxTFT(display, caption = '', pos = 0,
                 fg_color = (255, 255, 255), bg_color = (0, 0, 0)
                 
        MyBox = TextBoxOLED(display, caption = '', pos = 0)
        
        Parameters: display:    Display object obtained from SSD1306
                                driver / ST7735R driver: object
                                
                                e. g.:
                                
                                display = ST7735R(spi, cs, dc, rst,
                                   height = num, width = num)
                                   
                                display = ssd1306.SSD1306_I2C(width, height, i2c)
                                
                    caption: Caption of the TextBox: string
                    pos: Vertical position of the TextBox: int
                    fg_color : Foreground color, RGB tuple: tuple
                    bg_color : Background color, RGB tuple: tuple
    
    Methods:
    
         line = MyBox.          content: Text content of the line: str
            add_line(content):  line: line-id for later updates: var
                                -> Must be called before show()
            
        MyBox.show(): Calculate the box size and line positions
                      and draw the box. Must be called after add_line()
                      or if redraw is neccessary
                                    
        MyBox.clear(): Clear / Hide the box.
        
        MyBox.set_pos(pos): pos: vertical position of the Box: int
                                    
        MyBox.update_caption(txt): txt: Text to update the caption with: str
        
        MyBox.update_line(line, txt): line: line-id: var
                                        txt: Text to update the line with: str
                                        
        MyBox.invert_color(line): line: line-id: var
                                    -> switches fg and bg color of line
                                    e. g. for marking line as 'selected'
                                    
        MyBox.delete_line(line): line: line-id: var
                                    -> Delete line
    
    Properties:        
        MyBox.box_y: Vertical position of the box
        MyBox.box_h: Height of the box
                                    
        
        
        
"""
class TextBox:    
    def __init__(self, display, caption = '', pos = 0):
        # Save parameters
        self.display = display
        self.caption = caption
        self.pos = pos
        
        self.font_height= 8 # MPY standard monospace font
        self.font_width = 8 # MPY standard monospace font

        # Configuration
        self.border = 2
        self.caption_padding = 1
        self.line_padding = 1
        
        # Calculate values
        self.line_height = self.font_height + 2 * self.line_padding
        self.clip_x = self.display_width - 2 * self.border
        self.content_skip = self.line_height + 2 * self.caption_padding
        
        # Declare variables
        # Framebuffers
        self.window_buffer = None
        self.caption_buffer = None
        
        # Line objects
        self.cap = None
        self.lines = {}
        
        # Others
        self.height = 0
        self.line_num = 0
        self.lines_total = 0
        

    # Clear whole display    
    def clear(self):
        self.window_buffer.fill(self.black)
        self.display.blit(self.window_buffer, 0, self.pos)
        self.display.show()
    
    # Add text line. Returns line id which may be used for updating 
    def add_line(self, content):
        self.lines_total += 1 # sic!
        # Calculate max available space for text lines
        _max_line_space =  self.display_height - self.content_skip - self.border
        if self.lines_total > (_max_line_space // self.line_height):
            self.lines_total -= 1 # sic!
            print('Error: add_line: Too many lines.')
        else: 
            new_line = self.Line(self, self._trim_maxlen(str(content)),
                                 self.fg_color, self.bg_color, self.border)
            
            self.lines[str(new_line.num)] = new_line
            return str(new_line.num)
        
    # Update box position
    # Need to call show() afterwards
    def set_pos(self, pos):
        self.clear() # Call clear() first since it uses self.pos
        self.pos = pos
        self.show()
        
    # Draw the box with all lines and caption
    def show(self):
        # Clear old window buffer
        if not (self.window_buffer is None):
            self.clear()
        # calculate box height
        #             |        height of all lines        || caption + padding || border bottom |
        self.height = self.line_height * (self.lines_total) + self.content_skip + self.border
        
        # Create buffer for MSGBOX
        # Set color for caption background and border
        self.window_buffer = self.buffer(self.display_width, self.height)
        self.window_buffer.fill(self.fg_color)
        
        # Draw the (black) background of the textarea
        _x = self.border
        _y = self.content_skip - 1
        _w = self.display_width - 2 * (self.border)
        _h = self.line_height * (self.lines_total)
        self.window_buffer.rect(_x, _y, _w, _h, self.bg_color, 1)
        
        # Create Line object for caption and draw it to window buffer
        self.cap = self.Line(self, self._trim_maxlen(str(self.caption)),
                             self.bg_color, self.fg_color, int(self.border/2))
        
        self.cap.show_line(self.window_buffer, self.caption_padding)
        
        # Create Line objects for text lines and draw them to window buffer
        # in ascending order determined by their ids
        # This preserves order after deleting lines
        _pos = 0
        for key, value in sorted(self.lines.items()):
            value.show_line(self.window_buffer, self.content_skip + self.line_height * _pos)
            value.rel_pos = self.content_skip + self.line_height * _pos
            _pos += 1
            
        # Draw window buffer to display and show it
        self.display.blit(self.window_buffer, 0, self.pos)
        self.display.show()
    
    @property
    def box_h(self):
        return self.height
    
    @property
    def box_y(self):
        return self.pos
    
    # Trim strings to prevent text overflow in lines
    def _trim_maxlen(self, txt):
        if (len(txt) * self.font_width) > self.clip_x:
            maxlen = (self.clip_x // 8)
            return txt[0:maxlen]
        else:
            return txt

    def delete_line(self, lid):
        _lid = str(lid)
        if _lid in self.lines:
            self.lines_total -= 1
            self.lines.pop(_lid)
            self.clear()
            gc.collect()
            if self.lines_total > 0:
                self.show()
        else:
            print('Error: delete_line: Wrong line index.')
            return False
    
    def update_caption(self, caption):
        self.caption = self._trim_maxlen(caption)
        self.cap.set_text_line(self.caption)
        self.cap.show_line(self.display, self._abs_pos(self.cap))
        self.display.show()
    
    def invert_color(self, lid):
        _lid = str(lid)
        if _lid in self.lines:
            self.lines[_lid].invert_line()
            self.lines[_lid].clear_line()
            self.lines[_lid].set_text_line()
            self.lines[_lid].show_line(self.display, self._abs_pos(_lid))
            self.display.show()
        else:
            print('Error: invert: Wrong line index.')
            return False
        
    def _abs_pos(self, lid):
        lid = self.lines[lid] if lid in self.lines else lid
        return (lid.rel_pos + self.pos)
        
    def update_line(self, lid, content):
        _lid = str(lid)
        if _lid in self.lines:
            self.lines[_lid].clear_line()
            self.lines[_lid].set_text_line(str(content))
            self.lines[_lid].show_line(self.display, self._abs_pos(_lid))
            self.display.show()
        else:
            print('Error: update_line: Wrong line index.')
            return False
    
    # Line class creates individual FrameBuffers
    # and provides a static id for each line
    # This way lines can be updated individually without
    # redrawing the whole screen buffer
    class Line:
        def __init__(self, parent, content, fg_color, bg_color, posx = 0):
            # Preserve the 'self' scope of the MSGBOX class
            self.parent = parent
            self.posy = None # absolute position on screen
            self.posx = posx
            self.fg_color = fg_color
            self.bg_color = bg_color
            self.content = content
            self.rel_pos = 0 # relative position in box
                             # updated when parent.show() is called
            
            # Assign an ascending id to each line
            self.num = self.parent.line_num
            self.parent.line_num += 1
            
            # Create individual FB for each line
            self.line_buffer = self.parent.buffer(self.parent.display_width - 2 * self.posx,
                                                   self.parent.line_height)
            self.set_text_line(str(self.content))
        
        # Draw line to display or window buffer
        def show_line(self, buffer, posy):
            self.posy = posy
            
            buffer.blit(self.line_buffer, self.posx, self.posy)
            
        def clear_line(self):
            self.line_buffer.fill(self.bg_color)
        
        # Set the text content of the line
        # Either update text or
        # redraw previously set text
        # (neccessary for invert function)
        # when fg_ and bg_color have changed
        def set_text_line(self, content = None):
            
            self.content = ' ' if content is None else content
                
            self.clear_line()
            
            self.line_buffer.text(str(self.content), self.parent.line_padding,
                                  self.parent.line_padding, self.fg_color)
            
        # Sawp fg_ and bg_color
        def invert_line(self):
            self.fg_color, self.bg_color = self.bg_color, self.fg_color


'''
Creates a two-colored Textbox on a TFT Display using ST7735R driver

display = TFT display object
caption = caption of the Textbox
pos = vertical position of the Textbox
fg_color = foreground color, set as tuple (r, g, b)
bg_color = background color, set as tuple (r, g, b)
'''
class TextBoxTFT(TextBox):
    def __init__(self, display, caption = '', pos = 0,
                 fg_color = ((255,) * 3), bg_color = ((0,) * 3)):
        
        self.display = display

        self.display_width = 128
        self.display_height = 160
        self.white = self.rgb_color((255,) * 3)
        self.black = self.rgb_color((0,) * 3)
        
        self.fg_color = self.rgb_color(fg_color) # Pass Tuple
        self.bg_color = self.rgb_color(bg_color) # Pass Tuple
        
        super().__init__(self.display, caption, pos)
    
    # Create RGB color from TUPLE: (r, g, b)
    # r, g, b: int = 0 - 255
    def rgb_color(self, _rgb):
        _r, _g, _b = _rgb
        return self.display.rgb(_r, _g, _b)
    
    # Create RGB565-FrameBuffer for TFT
    def buffer(self, width, height):
        return FrameBuffer(bytearray(width * height * 2), width, height, RGB565)


'''
Creates a black-white text box on a SSD1306 OLED Display

display = OLED display object
caption = caption of the Textbox
pos = vertical position of the Textbox
'''
class TextBoxOLED(TextBox):
    def __init__(self, display, caption = '', pos = 0):
        
        self.display_width = 128
        self.display_height = 64
        
        self.white = 1
        self.black = 0
        
        self.fg_color = self.white
        self.bg_color = self.black
        
        super().__init__(display, caption, pos)
    
    # Create BW FrameBuffers for OLED   
    def buffer(self, width, height):
        return FrameBuffer(bytearray(width * height * 1), width, height, MONO_VLSB)
    
