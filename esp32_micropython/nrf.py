
from micropython import const
import utime
from machine import Pin,  SPI

# nRF24L01+ registers
CONFIG = const(0x00)
EN_RXADDR = const(0x02)
SETUP_AW = const(0x03)
SETUP_RETR = const(0x04)
RF_CH = const(0x05)
RF_SETUP = const(0x06)
STATUS = const(0x07)
RX_ADDR_P0 = const(0x0A)
TX_ADDR = const(0x10)
RX_PW_P0 = const(0x11)
FIFO_STATUS = const(0x17)
DYNPD = const(0x1C)

# CONFIG register
EN_CRC = const(3)  # enable CRC
CRCO = const(2)  # CRC encoding scheme; 0=1 byte, 1=2 bytes
PWR_UP = const(1)  # 1=power up, 0=power down
 
# RF_SETUP register
POWER_0 = const(0x00)  # -18 dBm
POWER_1 = const(0x02)  # -12 dBm
POWER_2 = const(0x04)  # -6 dBm
POWER_3 = const(0x06)  # 0 dBm
SPEED_1M = const(0x00)
SPEED_2M = const(0x08)
SPEED_250K = const(0x20)

# STATUS register
RX_DR = const(0x40)  # RX data ready; write 1 to clear
TX_DS = const(0x20)  # TX data sent; write 1 to clear
MAX_RT = const(0x10)  # max retransmits reached; write 1 to clear

# FIFO_STATUS register
RX_EMPTY = const(0x01)  # 1 if RX FIFO is empty

# constants for instructions
R_RX_PL_WID = const(0x60)  # read RX payload width
R_RX_PAYLOAD = const(0x61)  # read RX payload
W_TX_PAYLOAD = const(0xA0)  # write TX payload
FLUSH_TX = const(0xE1)  # flush TX FIFO
FLUSH_RX = const(0xE2)  # flush RX FIFO
NOP = const(0xFF)  # use to read STATUS register
EN_AA       =const(0x01)
FEATURE     =const(0x1D)



rf_setup = 0
buf = bytearray(1)
spi,ce,cs = None,None,None 
cfg = {'spi': -1, 'miso': 19, 'mosi': 23, 'sck': 18, 'csn': 26, 'ce': 27}


def NRF24L01_Initialize():
    
  global rf_setup,spi,ce,cs

  rf_setup = 0x0F
  spi = SPI(2, baudrate=80000000, polarity=0, phase=0, bits=8, firstbit=0,sck=Pin(cfg['sck']), mosi=Pin(cfg['mosi']), miso=Pin(cfg['miso']))
  cs = Pin(cfg['csn'], mode=Pin.OUT, value=1)
  ce = Pin(cfg['ce'], mode=Pin.OUT, value=0)
   
def NRF24L01_WriteReg(reg, value):
    

    cs.value(0)
    spi.readinto(buf, 0x20 | reg)
    spi.readinto(buf, value)
    cs.value(1)


def NRF24L01_WriteRegisterMulti(reg, data):
        
    cs.value(0)
    spi.readinto(buf, 0x20 | reg)
    spi.write(bytearray(data))
    cs.value(1)
       

def NRF24L01_FlushRx():
        
    cs.value(0)
    spi.readinto(buf, FLUSH_RX)
    cs.value(1)

def NRF24L01_FlushTx():
     
    cs.value(0)
    spi.readinto(buf, FLUSH_TX)
    cs.value(1)
 

@micropython.viper
def NRF24L01_WritePayload(data):
    
     
    ce.value(0)
    cs.value(0)
    spi.readinto(buf, W_TX_PAYLOAD)
    spi.write(bytearray(data))
    cs.value(1)
    ce.value(1)

    return buf[0]

def NRF24L01_Activate(code):

    cs.value(0)
    spi.write(bytearray(0x50))
    spi.write(bytearray(code))
    cs.value(1)
    return 1;


def NRF24L01_SetPower(power):

    global rf_setup
    rf_setup = (rf_setup & 0xF9) | ((power & 0x03) << 1)
    NRF24L01_WriteReg(RF_SETUP, rf_setup)

def NRF24L01_SetBitrate(bitrate):
 

    global rf_setup

    rf_setup = (rf_setup & 0xD7) | ((bitrate & 0x02) << 4) | ((bitrate & 0x01) << 3)
    NRF24L01_WriteReg(RF_SETUP, rf_setup)
 
def NRF24L01_SetTxMode():

   

    ce.value(0)
    NRF24L01_WriteReg(0x07, (1 << 6)| (1 << 5) | (1 << 4))
    NRF24L01_WriteReg(0x00, (1 << 3)   | (1 << 2) | (1 << 1))
    utime.sleep_us(130)
    ce.value(1)





