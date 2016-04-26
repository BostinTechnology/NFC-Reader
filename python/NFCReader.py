#/!usr/bin/env python3

########################### NFC Reader python script ############################
# Program to read the commands from the Bostin Technology 125KHz RFID Tag Reader
# Available commands:
# U - Read Card UID
# S - Card Status
# z - Product and Firmware Identifier
# e - Exit program

########################### Outstanding Actions ##################################

import wiringpi
import time
import sys

# set for GPIO Pin to use based on the jumper connection
GPIO_PIN = 1 # Jumper 1, also known as GPIO18
# GPIO_PIN = 0 # Jumper 2, also known as GPIO17
# GPIO_PIN = 2 # Jumper 3, also known as GPIO21 (Rv 1) or GPIO27 (Rv 2)
# GPIO_PIN = 3 # Jumper 4, also known as GPIO22



################################## Routines for NFC Reader #######################################


########################################## Generic ###############################################


def NFCSetup():
    # setup up the serial port and the wiringpi software for use
    # call setup for the wiringpi software
    response = wiringpi.wiringPiSetup()
    # set the GPIO pin for input
    wiringpi.pinMode(GPIO_PIN, 0)
    # open the serial port and set the speed accordingly
    fd = wiringpi.serialOpen('/dev/ttyAMA0', 9600)

    # clear the serial buffer of any left over data
    wiringpi.serialFlush(fd)

    if response == 0 and fd >0:
        # if wiringpi is setup and the opened channel is greater than zero (zero = fail)
        print ("PI setup complete on channel %d " % fd)
    else:
        print ("Unable to Setup communications")
        sys.exit()
        
    return fd

def WaitForCommandStobe():
    # continually monitor the selected GPIO pin and wait for the line to go low
    # print ("Waiting for Command Strobe") # Added for debug purposes
    while wiringpi.digitalRead(GPIO_PIN):
        # do nothing
        # print (".") # Added for debug purposes
        time.sleep(0.001) 
    return

def ReadText(fd):
    # read the data back from the serial line and return it as a string to the calling function
    qtydata = wiringpi.serialDataAvail(fd)
    # print ("Amount of data: %d bytes" % qtydata) # Added for debug purposes
    response = ""
    while qtydata > 0:
        # while there is data to be read, read it back
        ans = chr(wiringpi.serialGetchar(fd))
        # print ("Reading data back %d:%s" % (qtydata, ans)) #Added for Debug purposes
        response = response + ans
        qtydata = qtydata - 1
    return response

def ReadInt(fd):
    # read a single character back from the serial line
    qtydata = wiringpi.serialDataAvail(fd)
    # print ("Amount of data: %s bytes" % qtydata)  # Added for debug purposes
    response = 0
    if qtydata > 0:
        # print ("Reading data back %d" % qtydata) #Added for Debug purposes
        response = wiringpi.serialGetchar(fd)
    return response


def DecodeAcknowledgeByte(ackbyte):
    # Takes the given string acknowledge byte and checks for errors in the response
    # b7 b6 b5 b4 b3 b2 b1 b0
    # 1  x  x  x  x  x  x  x
    #    |  |  |  |  |  |  EEPROM Error = 1
    #    |  |  |  |  |  Card OK = 1
    #    |  |  |  |  Rx OK = 1
    #    |  |  |  RS232 Error = 1
    #    |  |  Card type = ignore
    #    |  Card Type = ignore
    #    MFRC Error = 1
    # A good response would be 10xx0110 (binary)
    #
    # returns card type (see above) if no error, False if an error detected or no card is present
    #
    # Takes the response and AND's it with a binary mask for each bit will return just the bit I'm interested. 
    # Shifting (>>) this bit to bit0, enables me to check for True / False
    
    # print ("Acknowledge byte: %s" % bin(ackbyte)) # Added for debug purposes

    if ackbyte == 0x80:
        # No card present
        # print("No Card Present")  #Added for Debug Purposes
        return False
    elif (ackbyte & 0b00000001) == True:
        # EEPROM Error if True
        print ("EEPROM Error")
        return False
    elif ((ackbyte & 0b00000010) >> 1) == False:
        # Card Not OK if 0
        print ("Card Not OK")
        return False
    elif ((ackbyte & 0b00000100) >> 2) == False:
        # Receive Error = 0
        print ("Receive Error")
        return False
    elif ((ackbyte & 0b00001000) >> 3) == True:
        # RS232 Error = 1
        print ("RS232 Error")
        return False
    elif ((ackbyte & 0b01000000) >> 6) == True:
        # MFRC Error = 1
        print ("MFRC Error")
        return False

    # no error detected, all ok.
    return True


########################################## Specific ##############################################


def ReadVersion(fd):
    # read the version from the NFC board 'z' 0x7A

    print ("Reading NFC Board Version Information .......")

    wiringpi.serialFlush(fd)
    WaitForCommandStobe()
    # print ("Sending Reading Version command")  # Added for Debug purposes
    wiringpi.serialPutchar(fd, 0x7A)
    time.sleep(0.2)
    ans = ReadText(fd)
    print ("Response: %s" % ans)
    return
    
def ReadStatus(fd):
    # Read the Card Status from the NFC Board
    # The acknowledge byte flags indicate card status

    # b7 b6 b5 b4 b3 b2 b1 b0
    # 1  x  x  x  x  x  x  x
    #    |  |  |  |  |  |  ignore
    #    |  |  |  |  |  ignore
    #    |  |  |  |  ignore
    #    |  |  |  ignore
    #    |  |  |
    #    |  |  MF Type (0 = MF 1k byte card, 1 = MF 4k byte card)
    #    |  UL Type (0 = MF standard 1k/4k card, SINGLE UID, 1 = MF Ultralight / NTAG2 card DOUBLE UID)
    #    |
    #    ignore
    #
    # A good response would be xx01xxxx (binary) which is then shited to the LSB

    print ("Reading Card Status .......")

    print ("Waiting for a card ....")

    nocard = True
    while nocard:
        WaitForCommandStobe()
        # print ("Sending Read Card Status and UID command") #Added for Debug purposes
        # send an ASCII 'S' 0x53
        wiringpi.serialPutchar(fd, 0x53)
        time.sleep(0.2)
        ans = ReadInt(fd)
        # print ("Tag Status: %s" % hex(ans)) #Added for Debug purposes

        # 0x80 received if no card present
        if DecodeAcknowledgeByte(ans):
            # Card present and read
            nocard = False
            # print ("Tag Present") #Added for Debug purposes
            print ("Card Status")
            print ("-->%s<--" % hex(ans))
            
            # decode the ackowledge byte for card type
            # Identify the card type from bits 5 & 6
            if ((ans & 0b00100000) >> 5) == True:
                #if the UL Type = 1, it is a Ultralight / NTAG2 card
                print ("Ultralight / NTAG2 Card")
            elif ((ans & 0b00010000) >> 4) == True:
                #MiFare Type 4k byte card" 
                print ("MiFare 4k byte card")
            else:
                # MiFare Card 1k byte card"
                print ("MiFare 1k byte card")
    return
    
def ReadCardUID(fd):
    # Read the Card Status and all data blocks from within the UID
    # Note: Mifare 1k and 4k cards have a 4 byte serial number so the last 3 bytes contain dummy (0x00) data,
    #       Ultralight / NTAG2 cards have a 7 byte serial number

    print ("Reading Card UID .......")

    print ("Waiting for a card ....")

    nocard = True
    while nocard:
        WaitForCommandStobe()
        # print ("Sending Read Card Status command") #Added for Debug purposes
        # send an ASCII 'U' 0x55
        wiringpi.serialPutchar(fd, 0x55)
        time.sleep(0.2)
        ans = ReadInt(fd)
        # print ("Tag Status: %s" % hex(ans)) #Added for Debug purposes

        if DecodeAcknowledgeByte(ans):
            # Card present and read
            nocard = False
            ans = ReadText(fd)
            print ("Card UID")
            print ("-->%s<--" % ans)
    return

def HelpText():
    # show the help text
    print ("**************************************************************************\n")
    print ("Available commands: -")
    print ("z - Display product and firmware version information")
    print ("S - Read the Card Status")
    print ("U - Read Card UID")
    print ("e - Exit program")


# main code loop

print ("Bostin Technology Ltd")
print ("Cogniot Products")
print ("PinFln\n")
print ("Press h for help\n")

#Initiate Communications
comms = NFCSetup()

while True:
    choice = input ("Select Menu Option:")

    if choice == "H" or choice == "h":
        HelpText()
    elif choice == "z":
        ReadVersion(comms)
    elif choice == "S":
        ReadStatus(comms)
    elif choice == "U":
        ReadCardUID(comms)
    elif choice == "E" or choice == "e":
        sys.exit()


