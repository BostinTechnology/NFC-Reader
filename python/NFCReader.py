#!/usr/bin/env python

########################### NFC Reader python script ############################
# Program to read the commands from the Bostin Technology 125KHz RFID Tag Reader
# Available commands:
# U - Read Card UID         # TODO: Ready To Test
# S - Card Status           # TODO: Ready To Test
# P - Program EEPROM        # TODO: Modify routine
# K - Store Keys            # TODO: No Code written yet
# W - Write Card Block      # TODO: In Progress
# R - Read Card Block       # TODO: Modify routine
# I - Inc Value             # TODO: No Code written yet
# D - Dec Value             # TODO: No Code written yet
# T - Transfer Value        # TODO: No Code written yet
# x - Type Identification   # TODO: No Code written yet
# z - Product and Firmware Identifier   # TODO: Ready To Test
# F - Factory Reset         # TODO: Ready To Test
# e - Exit program

########################### Outstanding Actions ##################################
# TODO: Add a check for the response to the command - see Acknowledge Byte, pg 12

import wiringpi2
import time
import sys

# set for GPIO Pin to use based on the jumper connection
# GPIO_PIN = 1 # Jumper 1, also known as GPIO18
GPIO_PIN = 0 # Jumper 2, also known as GPIO17
# GPIO_PIN = 2 # Jumper 3, also known as GPIO21 (Rv 1) or GPIO27 (Rv 2)
# GPIO_PIN = 3 # Jumper 4, also known as GPIO22

# define the different card types
UNKNOWN_CARD = 999
MIFARE_1K = 1001
MIFARE_4K = 1002
ULTRA_NTAG2 = 1003



################################### Code below this line is directly from the RFID Reader  #####################



#def ReadInt(fd):
    ## read a single character back from the serial line
    #qtydata = wiringpi2.serialDataAvail(fd)
    ## print "Amount of data: %s bytes" % qtydata  # Added for debug purposes
    #response = 0
    #if qtydata > 0:
        ## print "Reading data back %d" % qtydata #Added for Debug purposes
        #response = wiringpi2.serialGetchar(fd)
    #return response

#def RFIDSetup():
    ## setup up the serial port and the wiringpi software for use
    ## call setup for the wiringpi2 software
    #response = wiringpi2.wiringPiSetup()
    ## set the GPIO pin for input
    #wiringpi2.pinMode(GPIO_PIN, 0)
    ## open the serial port and set the speed accordingly
    #fd = wiringpi2.serialOpen('/dev/ttyAMA0', 9600)

    ## clear the serial buffer of any left over data
    #wiringpi2.serialFlush(fd)
    
    #if response == 0 and fd >0:
        ## if wiringpi is setup and the opened channel is greater than zero (zero = fail)
        #print "PI setup complete on channel %d" %fd
    #else:
        #print "Unable to Setup communications"
        #sys.exit()
        
    #return fd

#def ReadTagStatus(fd):
    ## read the RFID reader until a tag is present
    #notag = True
    #while notag:
        #WaitForCTS()
        ## print "Sending Tag Status Command" #Added for Debug purposes
        #wiringpi2.serialPuts(fd,"S")
        #time.sleep(0.1)
        #ans = ReadInt(fd)
        ## print "Tag Status: %s" % hex(ans) # Added for Debug purposes
        #if ans == int("0xD6", 16):
            ## D6 is a positive response meaning tag present and read
            #notag = False
    #print "Tag Status: %s" % hex(ans)
    #return

#def SetPollingDalay(fd):
    ## set the polling delay for the reader
    #print "Setting Polling delay ......."
    #WaitForCTS()

    #wiringpi2.serialPutchar(fd, 0x50)
    #wiringpi2.serialPutchar(fd, 0x00)
    ## various polling delays possible, standard one uncommented
    ##wiringpi2.serialPutchar(fd, 0x00) # 0x00 is no delay
    ##wiringpi2.serialPutchar(fd, 0x20) # 0x20 is approx 20ms
    ##wiringpi2.serialPutchar(fd, 0x40) # 0x40 is approx 65ms
    #wiringpi2.serialPutchar(fd, 0x60) # 0x60 is approx 262ms
    ##wiringpi2.serialPutchar(fd, 0x80) # 0x60 is approx 1 Seconds
    ##wiringpi2.serialPutchar(fd, 0xA0) # 0x60 is approx 4 Seconds

    #time.sleep(0.1)
    #ans = ReadInt(fd)
    ## print "Tag Status: %s" % hex(ans) # Added for Debug Purposes 
    #if ans == int("0xC0", 16):
        ## C0 is a positive result
        #print "Polling delay changed ......"
    #else:
        #print "Unexpected response %s" % hex(ans)
        ## flush any remaining characters from the buffer
        #wiringpi2.serialFlush(fd)

#def ReadTagPageZero(fd):
    ## read the tag page 00 command
    #notag = True

    #print "Reading Tag Data Page 00......."

    #print "Waiting for a tag ...."

    #notag = True
    #while notag:
        #WaitForCTS()
        ## print "Sending Tag Read Page Command" #Added for Debug purposes
        #wiringpi2.serialPutchar(fd, 0x52)
        #wiringpi2.serialPutchar(fd, 0x00)
        #time.sleep(0.1)
        #ans = ReadInt(fd)
        ## print "Tag Status: %s" % hex(ans) #Added for Debug purposes
        #if ans == int("0xD6", 16):
            ## Tag present and read
            #notag = False
            ## print "Tag Present" #Added for Debug purposes
            #ans = ReadText(fd)
            #print "Page 00"
            #print "-->%s<--" %ans
    #return


#def ChangeReaderOpMode(fd):
    ## prvide an additional menu to choose the type of tag to be read and set the reader accordingly
    #print "Setting Reader Operating Tag Mode......."

    #desc = ""
    #choice = ""
    #while choice == "":
        #print "*********************************************"
        #print "a - Hitag H2"
        #print "b - Hitag H1/S (factory default)"
        #print "c - EM/MC2000"
        ## promt the user for a choice
        #choice = raw_input("Please select tag type .....:")
        ## print "choice: %s" %choice # Added for Debug purposes
        
        #if choice =="a" or choice == "A":
            #desc = "Hitag H2"
            #WaitForCTS()
            #wiringpi2.serialPutchar(fd, 0x76)
            #wiringpi2.serialPutchar(fd, 0x01) # 0x01 = H2
        #elif choice =="b" or choice == "B":
            #desc = "Hitag H1/S"
            #WaitForCTS()
            #wiringpi2.serialPutchar(fd, 0x76)
            #wiringpi2.serialPutchar(fd, 0x02) # 0x01 = H1/S
        #elif choice =="c" or choice == "C":
            #desc = "Em / MC2000"
            #WaitForCTS()
            #wiringpi2.serialPutchar(fd, 0x76)
            #wiringpi2.serialPutchar(fd, 0x03) # 0x03 = EM/MC2000
        #else:
            #print "Invalid option.  Please try again..."
            #choice = ""

    #time.sleep(0.1)
    #ans = ReadInt(fd)
    ## print "Tag Status: %s" % hex(ans) #Added for Debug purposes
    #if ans == int("0xC0", 16):
        ## Positive result
        #print "Reader Operating Mode %s ......" % desc
    #else:
        #print "Unexpected response %s" % hex(ans)
        ## clear the buffer
        #wiringpi2.serialFlush(fd)

################################## Routines for NFC Reader #######################################

def WaitForCommandStobe():
    # continually monitor the selected GPIO pin and wait for the line to go low
    # print "Waiting for Command Strobe" # Added for debug purposes
    while wiringpi2.digitalRead(GPIO_PIN):
        # do nothing
        time.sleep(0.001)
    return

def ReadText(fd):
    # read the data back from the serial line and return it as a string to the calling function
    qtydata = wiringpi2.serialDataAvail(fd)
    # print "Amount of data: %d bytes" % qtydata # Added for debug purposes
    response = ""
    while qtydata > 0:
        # while there is data to be read, read it back
        # print "Reading data back %d" % qtydata #Added for Debug purposes
        response = response + chr(wiringpi2.serialGetchar(fd))
        qtydata = qtydata - 1   
    return response

def ReadInt(fd):
    # read a single character back from the serial line
    qtydata = wiringpi2.serialDataAvail(fd)
    # print "Amount of data: %s bytes" % qtydata  # Added for debug purposes
    response = 0
    if qtydata > 0:
        # print "Reading data back %d" % qtydata #Added for Debug purposes
        response = wiringpi2.serialGetchar(fd)
    return response

    
def DecodeAcknowledgeByte(ackbyte):

#TODO: Validate this function with a test

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
    # returns card type (see above) if no error, False if an error detected
    
    # taking the response, shifting it to select the required bit and then ANDing it with 0b1 will return just the bit I'm 
    # interested in as 1 or 0. The number of shifts (>>) determines the bit number being examined
    if (int(ackbyte,2) >> 0 & 0b1)= True:
        # EEPROM Error if True
        print "EEPROM Error"
        return False
    elif (int(ackbyte,2) >> 1 & 0b1) = False:
        # Card Not OK if 0
        print "Card Not OK"
        return False
    elif (int(ackbyte,2) >> 2 & 0b1) = False:
        # Receive Error = 0
        print "Receive Error"
        return False
    elif (int(ackbyte,2) >> 3 & 0b1) = True:
        # RS232 Error = 1
        print "RS232 Error"
        return False
    elif (int(ackbyte,2) >> 6 & 0b1) = False:
        # MFRC Error = 1
        print "MFRC Error"
        return 
    
    # no error detected, all ok, now detect card type.
    card_type = UNKNOWN_CARD
    # decode the ackowledge byte for card type
    # Identify the card type from bits 5 & 6
    if int(ans,2) >> 6 & 0b1) == 1:
        #if the UL Type = 1, it is a Ultralight / NTAG2 card
        #print "UL Type = Single UID"       #Added for debug purposes
        card_type = ULTRA_NTAG2
    elif int(ans,2) >> 5 & 0b1) == 1:
        #print "MF Type = 4k byte card"     #Added for Debug purposes
        card_type = MIFARE_4K
    else:
        #print "MF Card = 1k byte card"     #Added for Debug purposes
        card_type = MIFARE_1K
    return card_type

def ReadVersion(fd):
    # read the version from the NFC board
    WaitForCommandStobe()
    #print "Sending Reading Version command"  # Added for Debug purposes
    wiringpi2.serialPuts(fd,"z")
    time.sleep(0.1)
    ans = ReadText(fd)
    print "Response: %s" % ans
    return
    
def ReadStatus(fd):
    # Read the Card Status from the NFC Board
    # The acknowledge byte flags indicate card status
    
    print "Reading Card Status ......."

    print "Waiting for a card ...."

    notag = True
    while notag:
        WaitForCommandStobe()
        # print "Sending Read Card Status and UID command" #Added for Debug purposes
        # send an ASCII 'S' 0x53
        wiringpi2.serialPutchar(fd, 0x53)
        time.sleep(0.1)
        ans = ReadInt(fd)
        # print "Tag Status: %s" % hex(ans) #Added for Debug purposes
        
        reply = DecodeAcknowledgeByte(ans)
        # reply will be either false or the card type value
        if reply:
            # Card present and read
            notag = False
            # print "Tag Present" #Added for Debug purposes
            print "Card Status"
            print "-->%s<--" % ans
            if reply == MIFARE_1K:
                print "MiFare 1k byte card"
            elif reply == MIFARE_4K:
                print "MiFare 4k byte card"
            elif reply == ULTRA_NTAG2:
                print "Ultralight / NTAG2 Card"
            else:
                print "Unknown Card type"
                
        #TODO: I think I might have to revert this to the old version as this doesn't tell us the type.
        # I think I can do this from git committed version.
    return
        
def ReadCardUID(fd):
    # Read the Card Status and all data blocks from within the UID
    # Note: Mifare 1k and 4k cards have a 4 byte serial number so the last 3 bytes contain dummy (0x00) data, 
    #       Ultralight / NTAG2 cards have a 7 byte serial number

    print "Reading Card UID ......."

    print "Waiting for a card ...."

    notag = True
    while notag:
        WaitForCommandStobe()
        # print "Sending Read Card Status and UID command" #Added for Debug purposes
        # send an ASCII 'U' 0x55
        wiringpi2.serialPutchar(fd, 0x55)
        time.sleep(0.1)
        ans = ReadInt(fd)
        # print "Tag Status: %s" % hex(ans) #Added for Debug purposes
       
        if DecodeAcknowledgeByte(ans):
            # Card present and read
            notag = False
            # print "Tag Present" #Added for Debug purposes
            ans = ReadText(fd)
            print "Card UID"
            print "-->%s<--" % ans
    return
 
def FactoryReset(fd):
    # send the factory reset command to reload default values
    WaitForCTS()
    # print "Performing a factory reset ...." #Added for Debug purposes
    wiringpi2.serialPutchar(fd, 0x46)
    wiringpi2.serialPutchar(fd, 0x55)
    wiringpi2.serialPutchar(fd, 0xAA)
    time.sleep(0.1)
    print "FACTORY RESET COMPLETE"
    print ""
    return
    
def WriteCardBlock(fd):
    # Write 16 bytes of data to the specified block
    # A block is made up of 16 bytes, with 4 (16 on upper) blocks in a sector
    # Blocks 3, 7, 11, 15 etc contain Security data and Access bits
    
    # user selection of card type
      
    # Capture and validate data to be written - MiFare
    # Block address 0 - 255
    # Key Type 0 = KeyA, 1 = KeyB
    # Key Code Number 0 - 31
    # 16 bytes of data, each byte 0 - 255
    
    # Capture and validate data to be written - Ultra
    # Page Address 0 - 15

    # Capture and validate data to be written - NTAG2
    # Page Address 0 - 63
    
    
    # Wait for a card to be present, capture type
    
    # check status and if ok continue
    
    # Write Block / Page of data

    # Check Status for error
    
    # send 'W'
    print "Not implemented yet"
    return

def ReadTypeIdent(fd):
    # send 'x'
    print "Not implemented yet"
    return

def ProgramEEPROM(fd):
    # send 'P'
    print "Not implemented yet"
    return
    
def StoreKeys(fd):
    #send 'K'
    print "Not implemented yet"
    return
    
def ReadCardBlock(fd):
    # send 'R'
    print "Not implemented yet"
    return
    
def IncValue(fd):
    # send 'I'
    print "Not implemented yet"
    return

def DecValue(fd):
    # send 'D'
    print "Not implemented yet"
    return
     
def TransferValue(fd):
    # send 'T'
    print "Not implemented yet"
    return
    
def HelpText():
    # show the help text
    print "**************************************************************************\n"
    print "Available commands: -"
    print "z - Display product and firmware version information"
    print "x - Type Identification"
    print "S - Read the Card Status"
    print "U - Read Card UID"
    print "F - Perform a Factory Reset"
    print "P - Program EEPROM"
    print "K - Store Keys"
    print "W - Write Card Block"
    print "R - Read Card Block"
    print "I - Inc Value"
    print "D - Dec Value"
    print "T - Transfer Value"
    print "e - Exit program"


# main code loop

print "Bostin Technology Ltd"
print "Cogniot Products"
print "PinFln"
print ""
print "Press h for help"
print ""

#TODO: Initiate Communications

while True:
    choice = raw_input ("Select Menu Option:")

    if choice == "H" or choice == "h":
        HelpText()
    elif choice == "z":
        ReadVersion(comms)
    elif choice == "x":
        ReadTypeIdent(comms)
    elif choice == "S":
        ReadStatus(comms)
    elif choice == "U":
        ReadCardUID(comms)
    elif choice == "F":
        FactoryReset(comms)
    elif choice == "P":
        ProgramEEPROM(comms)
    elif choice == "K":
        StoreKeys(comms)
    elif choice == "W":
        WriteCardBlock(comms)
    elif choice == "R":
        ReadCardBlock(comms)
    elif choice == "I":
        IncValue(comms)
    elif choice == "D":
        DecValue(comms)
    elif choice == "T":
        TransferValue(comms)
    elif choice == "E" or choice == "e":
        sys.exit()


