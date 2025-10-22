import spidev
import time
import math
from gpiozero import Button

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1_000_000

NUM_LEDS = 300
BRIGHTNESS = 1

def set_all_to_color(r, g, b, brightness):
    data = []
    # Start frame
    data += [0x00, 0x00, 0x00, 0x00]
    # Per LED frame 
    for _ in range(NUM_LEDS):
        data += [0xE0 | brightness, b, g, r]

    # End frame
    # data += [0xFF]
    # data += [0x00] * int(5 + NUM_LEDS / 165 + NUM_LEDS / 5)
    # data += [0xFF, 0xFF, 0xFF, 0xFF]
    data += [0xFF] * ((NUM_LEDS + 15) // 16)

    spi.xfer2(data)

def send_data(led_data):
    data = []
    data += [0x00, 0x00, 0x00, 0x00]
    data += led_data
    data += [0xFF] * ((NUM_LEDS + 15) // 16)
    spi.xfer2(data)

def set_led(index, color, brightness, dataframe):
    dataframe[index*4:index*4+4] = [0xE0 | brightness, color[2], color[1], color[0]]

def crawl_led(color=(255, 0, 0), delay=0.05, brightness=BRIGHTNESS):
    led_data = [(0, 0, 0)] * NUM_LEDS
    for i in range(NUM_LEDS):
        led_data = [(0, 0, 0)] * NUM_LEDS
        led_data[i] = color
        # Build SPI frame
        data = [0x00, 0x00, 0x00, 0x00]
        for r, g, b in led_data:
            data += [0xE0 | brightness, b, g, r]
        data += [0xFF] * ((NUM_LEDS + 15) // 16)
        spi.xfer2(data)
        time.sleep(delay)

def clear_all_leds():
    set_all_to_color(0, 0, 0, 1)


def rainbow_cycle(delay=0.01, brightness=BRIGHTNESS):
    for j in range(0, 256 * 10, 10):  # 256 cycles of all colors on the wheel
        print(j)
        data = [0x00] * 4 * NUM_LEDS
        for i in range(NUM_LEDS):
            # Calculate the color for each LED
            idx = ((i+j) * 256 // NUM_LEDS)
            r = int((math.sin(idx * 6.28318 / 256) + 1) * 127.5)
            g = int((math.sin(idx * 6.28318 / 256 + 2) + 1) * 127.5)
            b = int((math.sin(idx * 6.28318 / 256 + 4) + 1) * 127.5)

            set_led(i, (r, g, b), brightness, data)

        send_data(data)
        time.sleep(delay)


# Setup GPIO
BUTTON_PIN = 3
button = Button(BUTTON_PIN)

def button_callback():
    print("microphone activated")
    # Reactive effect: flash white for a short duration
    set_all_to_color(255, 0, 0, BRIGHTNESS)
    time.sleep(0.02)
    clear_all_leds()

# Attach the callback to the button press
# button.when_pressed = button_callback

# try:
#     while True:
#         time.sleep(1)  # Keep the program running
# except KeyboardInterrupt:
#     pass

rainbow_cycle(delay=0.01, brightness=BRIGHTNESS)

input()
clear_all_leds()
spi.close()

# class SPILEDStrip:
#     def __init__(self, num_leds, spi_bus=0, spi_device=0, max_speed_hz=8000000):
#         self.num_leds = num_leds
#         self.spi = spidev.SpiDev()
#         self.spi.open(spi_bus, spi_device)
#         self.spi.max_speed_hz = max_speed_hz

#     def send_led_data(self, led_data):
#         """
#         led_data: list of (R, G, B) tuples, one per LED
#         For SK9822/APA102: send start frame, LED frames, end frame
#         """
#         start_frame = [0x00, 0x00, 0x00, 0x00]
#         end_frame = [0xFF] * ((self.num_leds + 15) // 16)
#         led_frames = []
#         for r, g, b in led_data:
#             # Brightness byte: 0b11100000 | brightness (0-31)
#             led_frames += [0xE0 | 31, b, g, r]
#         spi_data = start_frame + led_frames + end_frame
#         self.spi.xfer2(spi_data)

#     def clear(self):
#         self.send_led_data([(0, 0, 0)] * self.num_leds)

#     def close(self):
#         self.spi.close()

# if __name__ == "__main__":
#     strip = SPILEDStrip(num_leds=10)
#     try:
#         # Simple color wipe
#         for i in range(10):
#             leds = [(0, 0, 0)] * 10
#             leds[i] = (255, 0, 0)  # Red
#             strip.send_led_data(leds)
#             time.sleep(0.1)
#         strip.clear()
#     finally:
#         strip.close()