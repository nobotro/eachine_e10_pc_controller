import utime
from nrf import *

MJX_PACKET_SIZE = 16
MJX_RF_NUM_CHANNELS = 4
MJX_ADDRESS_LENGTH = 5
MJX_BIND_COUNT = 150
MJX_PACKET_PERIOD = 4000

mjx_counter = 0
mjx_rf_chan = 0
mjx_txid = [0] * 3
mjx_rf_channels = [0] * MJX_RF_NUM_CHANNELS
bufff = memoryview(bytearray(32))
cache = {}
e010_tx_rf_map  = [[[0x4F, 0x1C], [0x3A, 0x35, 0x4A, 0x45]],
                   [[0x90, 0x1C], [0x2E, 0x36, 0x3E, 0x46]], 
                   [[0x24, 0x36], [0x32, 0x3E, 0x42, 0x4E]],
                   [[0x7A, 0x40], [0x2E, 0x3C, 0x3E, 0x4C]],
                   [[0x61, 0x31], [0x2F, 0x3B, 0x3F, 0x4B]],
                   [[0x5D, 0x37], [0x33, 0x3B, 0x43, 0x4B]],
                   [[0xFD, 0x4F], [0x33, 0x3B, 0x43, 0x4B]], 
                   [[0x86, 0x3C], [0x34, 0x3E, 0x44, 0x4E]]]



xn297_scramble = [
    0xe3, 0xb1, 0x4b, 0xea, 0x85, 0xbc, 0xe5, 0x66,
    0x0d, 0xae, 0x8c, 0x88, 0x12, 0x69, 0xee, 0x1f,
    0xc7, 0x62, 0x97, 0xd5, 0x0b, 0x79, 0xca, 0xcc,
    0x1b, 0x5d, 0x19, 0x10, 0x24, 0xd3, 0xdc, 0x3f,
    0x8e, 0xc5, 0x2f]

xn297_crc_xorout = [
    0x0000, 0x3448, 0x9BA7, 0x8BBB, 0x85E1, 0x3E8C, 
    0x451E, 0x18E6, 0x6B24, 0xE7AB, 0x3828, 0x814B,
    0xD461, 0xF494, 0x2503, 0x691D, 0xFE8B, 0x9BA7,
    0x8B17, 0x2920, 0x8B5F, 0x61B1, 0xD391, 0x7401, 
    0x2138, 0x129F, 0xB3A0, 0x2988]
max=0

packet = memoryview(bytearray(16))
transmitterID = [14,48,60,127]
rf_setup = 0
buf = bytearray(1)
xn297_tx_addr= [0]*5
PPM_MIN = 1000
PPM_SAFE_THROTTLE = 1050 
PPM_MID = 1500
PPM_MAX = 2000
PPM_MIN_COMMAND = 1300
PPM_MAX_COMMAND = 1700
MJX_CHANNEL_HEADLESS = 8
MJX_CHANNEL_RTH =9
THROTTLE=0
AILERON =1
ELEVATOR=2
RUDDER=3



ppm = [PPM_MIN,PPM_MIN,PPM_MIN,PPM_MIN,PPM_MID,PPM_MID,
                           PPM_MID,PPM_MID,PPM_MID,PPM_MID,PPM_MID,PPM_MID]



xn297_crc = 0
xn297_addr_len = 5



def _BV(bit):

  return (1 << (bit))

def _map(x, in_min, in_max, out_min, out_max):
    
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
  

def mjx_convert_channel(num):

    val = map(ppm[num], PPM_MIN, PPM_MAX, 0, 255)
    if val < 128 :
      return 127-val

    return val
    


@micropython.viper
def GET_FLAG(ch:uint, mask:uint) -> uint:

  if ppm[ch] > PPM_MAX_COMMAND:
    return mask
  return uint(0)
  
@micropython.viper
def GET_FLAG_INV(ch:uint, mask:uint) -> uint:

  if ppm[ch] < PPM_MAX_COMMAND:
    return mask
  return uint(0)


def XN297_Configure(flags):
  
    global xn297_crc

    xn297_crc = not not(flags & _BV(3))
    flags &= ~(_BV(3) | _BV(2))
    NRF24L01_WriteReg(CONFIG, flags)
    
 



def initialize_mjx_txid():

  global mjx_txid
        
  mjx_txid[0:2] = e010_tx_rf_map[transmitterID[0] % 8][0]
  mjx_txid[2] = 0x00

def XN297_SetTXAddr(addr):

  global xn297_tx_addr,xn297_addr_len

  buff = [0x55, 0x0F, 0x71, 0x0C, 0x00]
  xn297_addr_len = 5
  NRF24L01_WriteReg(SETUP_AW,3)
  NRF24L01_WriteRegisterMulti(TX_ADDR, buff)
  xn297_tx_addr = addr
  
  
@micropython.viper
def bit_reverse(b_in:int)->int:
    b_out = int(0)
    for i in range(8):
        b_out = (b_out << int(1)) | (int(b_in) & int(1))
        b_in >>= 1
    
    return b_out;


def MJX_init():

  global mjx_rf_channels

  rx_tx_addr = [0] * MJX_ADDRESS_LENGTH
  initialize_mjx_txid()
  rx_tx_addr = bytearray(b'\x6d\x6a\x77\x77\x77')
  mjx_rf_channels = bytearray(b'\x36\x3e\x46\x2e')
  NRF24L01_Initialize()
  NRF24L01_SetTxMode()
  XN297_SetTXAddr(rx_tx_addr)
  NRF24L01_FlushTx()
  NRF24L01_FlushRx()
  NRF24L01_WriteReg(STATUS, 0x70) 
  NRF24L01_WriteReg(EN_AA, 0x00) 
  NRF24L01_WriteReg(EN_RXADDR, 0x01) 
  NRF24L01_WriteReg(SETUP_RETR, 0x00) 
  NRF24L01_WriteReg(RX_PW_P0, MJX_PACKET_SIZE)
  NRF24L01_SetBitrate(2)
  NRF24L01_SetPower(2)
  NRF24L01_Activate(0x73)
  NRF24L01_WriteReg(DYNPD, 0x00)
  NRF24L01_WriteReg(FEATURE, 0x00)
  NRF24L01_Activate(0x73)

@micropython.viper
def mjx_checksum()->uint:
 
  sum = packet[0]
  for i in range(uint(1),uint(15)):
    sum += packet[i]
  return uint(sum) & uint(255)

@micropython.viper
def crc16_update(crc:int, a:int) ->int:
    
    crc ^= a << 8;
    for i in range(8,0,-1):
      if crc & 0x8000:
            crc = (crc << 1) ^ 0x1021
      else:
            crc = crc << 1
    return crc


@micropython.viper
def XN297_WritePayload(data):


  global bufff
  res = uint(0)
  last = uint(0)
  for i in range(int(xn297_addr_len)):
   
        bufff[last] = int(xn297_tx_addr[int(4)-int(i)]) ^ int(xn297_scramble[i])
        last+=uint(1)
        
  for i in range(int(16)):
    b_out  = uint(bit_reverse(data[i]))
    bufff[last] = b_out ^ uint(xn297_scramble[uint(5)+uint(i)])
    last+=1
 
  if xn297_crc:
    offset = uint( 0)
    crc=uint(0xb5d2)
    for i in range(int(offset),int(last)):
       crc = uint(crc16_update(crc, bufff[i]))
    
    crc ^= uint(xn297_crc_xorout[18])
    bufff[last] = crc >> 8
    last+=1
    bufff[last] = crc & 0xff
    last+=1

  res = uint(NRF24L01_WritePayload(bufff))
    


def mjx_send_packet(bind):

  global packet,mjx_rf_chan,mjx_rf_channels
  packet[4] = 0x40
  packet[5] = 0x40  
  packet[6] = 0x40 
  packet[7] = mjx_txid[0]
  packet[8] = mjx_txid[1]
  packet[9] = mjx_txid[2]
  packet[10] = 0
  packet[11] = 0   
  packet[12] = 0
  packet[13] = 0
  packet[14] = 0xc0
  packet[10] += GET_FLAG(MJX_CHANNEL_RTH, 0x02) | GET_FLAG(MJX_CHANNEL_HEADLESS, 0x01)

  if not bind:

    packet[14] = 36

  else:
    
      XN297_Configure(_BV(EN_CRC) | _BV(CRCO) | _BV(PWR_UP))

  packet[15] = int(mjx_checksum())
  NRF24L01_WriteReg(RF_CH, mjx_rf_channels[int(mjx_rf_chan / 2)])
  mjx_rf_chan+=1
  mjx_rf_chan %= 2 * 4
  XN297_WritePayload(packet)
 


def mjx_init2():

          global mjx_rf_channels
          mjx_rf_channels=e010_tx_rf_map[transmitterID[0] % 8][1]

def MJX_bind():

  for i in range(150):
    mjx_send_packet(1)
    utime.sleep_us(4300)
  mjx_init2()


def process_MJX(throt,round,forback,rightleft):

  
  global packet
  
  packet[0] = throt
  packet[1] = round
  packet[2] = forback
  packet[3] = rightleft
  
  st=utime.ticks_us()
  mjx_send_packet(0)
  end=utime.ticks_us()
 
  dif=end-st
  if dif<4000:
      utime.sleep_us(4000-(end-st))
  
  





