'''
Lora Reyax RYLR998_EN module with Raspberry Pi model B (no Wifi or Bluetooth module).
    References:
        https://reyax.com//products/RYLR998
        https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#more
        https://elinux.org/RPi_Serial_Connection#Connection_to_a_microcontroller_or_other_peripheral
        https://github.com/flengyel/RYLR998-LoRa/tree/main
        https://forums.raspberrypi.com/viewtopic.php?t=341815

Connections:
    The module has 5 pins.  GND (Ground), RXD (Recieve), TXD (Transmit), RST (Reset), VDD (Power). I connect
    GND to any Ground pin. RXD to a 2.2k ohm resistor, to GPIO14 (Tx), and TXD to a 2.2k ohm resistor, to GPIO15 
    (Rx), because the Lora module should recieve data from the transmit pin on the Pi, and transmit data back 
    to the Pi from its transmit pin to the recieve pin on the Pi.  I connect RST to GPIO4 (I believe you pull this 
    low to physically reset the lora module).  Finally VDD is connected to 3.3v (NOT 5v).


To start, you have to make a couple config changes to the Pi.  Start with 'sudo raspi-config'.  In the GUI,
navigate to Interfacing Options -> Serial.  Answer <No> to login shell question, and <Yes> to serial port enabled.

Disable Bluetooth in /boot/config.txt by appending 'disable-bt=1' and 'enable-uart=1' 
Disable the bluetooth service with 'sudo systemctl disable hciuart.service'
Enable uart1 with the device tree overlay facility with 'sudo dtoverlay uart1'
'''

import RPi.GPIO as GPIO
import time
import asyncio
import subprocess
from time import sleep
import serial
import envSecrets

lora = serial.Serial("/dev/ttyS0", 115200)

def testLora():
        sendMsg = lora.write('AT\r\n'.encode())
        while(sendMsg<=2):
            pass
        sleep(0.5)
        reply = lora.readline()
        return reply.decode().strip('\r\n')

def cmdLora(lora_cmd, retrn=False):
    if lora_cmd[len(lora_cmd)-1] == '?':
        retrn=True
    while True:
        try:
            sendMsg = lora.write('{}\r\n'.format(lora_cmd).encode())
            while(sendMsg==0):
                pass
            sleep(1)
            reply = lora.read_all()
            sleep(0.2)
            if retrn:
                return reply.decode().strip('\r\n')
            print(reply.decode().strip('\r\n'))
            break
        except UnicodeError:
            pass

parameters = '8,7,1,12'
#Reset Lora Module, and configure parameters
if testLora() == '+OK':
    cmdLora('AT+FACTORY')
    cmdLora('AT+RESET')
    cmdLora(f'AT+PARAMETER={parameters}')
    cmdLora(f'AT+NETWORKID={envSecrets.lora_nid}')
    cmdLora(f'AT+ADDRESS={envSecrets.clientAddr}')
    sleep(1)
    if hasattr(envSecrets, 'lora_pswd'):
        cmdLora(f"AT+CPIN={envSecrets.lora_pswd}")

whatsTheNetworkId = cmdLora(f'AT+NETWORKID?')
print(whatsTheNetworkId)
