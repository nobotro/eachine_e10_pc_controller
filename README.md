# drone_pc_remote
This project is about how to control jjrc h36 and eachine e010 drone using pc and esp32 with micropython.
This drones uses MJX protocol

# Instruction

Used hardware :  esp32 dev board ,nrf24l01 wireless module , eachine e010 drone , genesys bluethoot gamepad ,USB to TTL Adapter


- Flash micropython firmware on esp32 dev board
- Put "main.py", "nrf.py","mjx.py" and "server.py" from "esp32_micropython" directory to esp32 board with micropython firmware
- Connect nrf pins correctly(we use hardware spi(2)) 'miso': 19, 'mosi': 23, 'sck': 18, 'csn': 26, 'ce': 277
- Connect USB to TTL Adapter pins to esp32 pins tx=0, rx=4
- Turn on bluethoot gamepad and run remote.py


You can modify key bindings and values in remote.py


Used resources:

- https://github.com/goebish/nrf24_multipro



