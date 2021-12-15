import machine
import mjx
from machine import UART
import _thread
import utime

throt,round,forback,rightleft,done=0,0,0,0,0



  
def driver():
  global throt,round,forback,rightleft,done
  
  
  machine.freq(240000000)
  mjx.MJX_init()
  mjx.MJX_bind()  
  uart = UART(1, baudrate=115200, tx=0, rx=4, bits=8, parity=0, stop=1,timeout=0)
  while True:
  
      
     
      mjx.process_MJX(throt,round,forback,rightleft)
      
      try:
        
        data=uart.readline()
        if not data:continue
        data=data.decode()
        
        if data.startswith('<') and data.endswith('>\n') and len(data) == 15:
            
            throt = int(data[1:4])
            round = int(data[4:7])
            forback = int(data[7:10])
            rightleft = int(data[10:13])

          
      except Exception as e:
        pass
      
      
      
         

      








