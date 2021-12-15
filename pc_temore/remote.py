import socket
import time
import json
from inputs import get_gamepad
import serial

state_json = {'throt':'000','round':'000','forback':'000','rightleft':'000'}
ser = serial.Serial('/dev/ttyUSB1',115200, bytesize=8, parity=serial.PARITY_EVEN, stopbits=1,timeout=0)
def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    

def main():

    while 1:
        events = get_gamepad()
        for event in events:
            if event.code == 'ABS_RZ':
                 

                    if event.state!=0  and event.state!=255 and abs(int(state_json['throt'])-event.state)<3:continue

                    state_json['throt'] = f'{event.state:03}'
                    data=ser.write(('<'+state_json['throt']+state_json['round']+state_json['forback']+state_json['rightleft']+'>\n').encode())
                    ser.flush()
                    print(state_json)
               
            elif event.code == 'ABS_X':

                if event.state!=0 and event.state!=127 and event.state!=255 and abs(int(state_json['round'])-event.state)<3:continue
                if event.state<0:
                        value_x =_map(abs(event.state),0,32767,0,127)
                else:
                        value_x =_map(abs(event.state),0,32767,128,255) 

                state_json['round'] = f'{value_x:03}'
                data=ser.write(('<'+state_json['throt']+state_json['round']+state_json['forback']+state_json['rightleft']+'>\n').encode())
                ser.flush()
                 
                print(state_json)


            elif event.code == 'ABS_RY':

                if event.state!=0 and event.state!=127 and event.state!=255 and abs(int(state_json['forback'])-event.state)<3:continue
                if event.state < 0:
                    value_y =_map(abs(event.state),255,32767,128,255) 
                else:
                    value_y =_map(abs(event.state),255,32767,0,127)


                state_json['forback'] = f'{value_y:03}'
                data=ser.write(('<'+state_json['throt']+state_json['round']+state_json['forback']+state_json['rightleft']+'>\n').encode())
                ser.flush()
                print(state_json)

            elif event.code == 'ABS_RX':

                if event.state!=0 and event.state!=127 and event.state!=255 and abs(int(state_json['rightleft'])-event.state)<3:continue
                if event.state < 0:
                    value_y =_map(abs(event.state),0,32767,0,127) 
                else:
                    value_y =_map(abs(event.state),0,32767,128,255)

                state_json['rightleft'] =f'{value_y:03}'
                data=ser.write(('<'+state_json['throt']+state_json['round']+state_json['forback']+state_json['rightleft']+'>\n').encode())
                ser.flush()
                print(state_json)


if __name__ == "__main__":
    main()

