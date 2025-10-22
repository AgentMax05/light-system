import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1_000_000

NUM_LEDS = 300

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

def clear_all_leds():
    set_all_to_color(0, 0, 0, 1)

set_all_to_color(255, 0, 0, 1)
input()
print("clearing all LEDs")
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