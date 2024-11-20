from machine import Pin
from gpio_lcd import GpioLcd

class BatteryMonitor:
    CW = 1  # Clockwise rotation
    CCW = -1  # Counter-clockwise rotation
    
    def __init__(self, rs_pin, enable_pin, d4_pin, d5_pin, d6_pin, d7_pin, pin_enc_a, pin_enc_b, lines=4, columns=20):
        # LCD initialization
        self.lcd = GpioLcd(rs_pin=Pin(rs_pin), enable_pin=Pin(enable_pin),
                           d4_pin=Pin(d4_pin), d5_pin=Pin(d5_pin),
                           d6_pin=Pin(d6_pin), d7_pin=Pin(d7_pin),
                           num_lines=lines, num_columns=columns)
        
        # Rotary encoder pins and states
        self.rotenc_A = Pin(pin_enc_a, Pin.IN, Pin.PULL_UP)
        self.rotenc_B = Pin(pin_enc_b, Pin.IN, Pin.PULL_UP)
        self.enc_state = 0
        self.counter = 0
        
    def re_full_step(self):
        enc_table_full_step = [
            [0x00, 0x02, 0x04, 0x00],
            [0x03, 0x00, 0x01, 0x10],
            [0x03, 0x02, 0x00, 0x00],
            [0x03, 0x02, 0x01, 0x00],
            [0x06, 0x00, 0x04, 0x00],
            [0x06, 0x05, 0x00, 0x20],
            [0x06, 0x05, 0x04, 0x00]
        ]
        
        self.enc_state = enc_table_full_step[self.enc_state & 0x0F][(self.rotenc_B.value() << 1) | self.rotenc_A.value()]
        
        result = self.enc_state & 0x30
        if (result == 0x10):
            return self.CW
        elif (result == 0x20):
            return self.CCW
        else:
            return 0
    
    def update_lcd(self):
        self.lcd.clear()
        self.lcd.move_to(1, 0)  # Move cursor to the 2nd column, 1st row
        self.lcd.putstr(f"{self.counter}% Battery")
        print(f"{self.counter}% Battery")
    
    def adjust_battery_percentage(self):
        res = self.re_full_step()
        if res == self.CW:
            self.counter = min(self.counter - 1, 0)
        elif res == self.CCW:
            self.counter = max(self.counter + 1, 100)
        
        self.update_lcd()
    
    def run(self):
        while True:
            self.adjust_battery_percentage()