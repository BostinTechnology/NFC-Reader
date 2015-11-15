#/!usr/bin/env python3

########################### NFC Reader python script ############################
# Program to read the commands from the Bostin Technology 125KHz RFID Tag Reader
# Available commands:
# U - Read Card UID                     # TODO: Ready To Test
# S - Card Status                       # TODO: Ready To Test
# P - Program EEPROM        # TODO: Modify routine
# K - Store Keys            # TODO: No Code written yet
# W - Write Card Block                  # TODO: Ready To Test
# R - Read Card Block                   # TODO: Ready To Test
# I - Inc Value                         # TODO: Ready To Test
# D - Dec Value                         # TODO: Ready To Test
# T - Transfer Value                    # TODO: Ready To Test
# x - Type Identification               # TODO: Ready To Test
# z - Product and Firmware Identifier   # TODO: Ready To Test
# F - Factory Reset                     # TODO: Ready To Test
# e - Exit program

########################### Outstanding Actions ##################################

import wiringpi2
import time
import sys

# set for GPIO Pin to use based on the jumper connection
# GPIO_PIN = 1 # Jumper 1, also known as GPIO18
GPIO_PIN = 0 # Jumper 2, also known as GPIO17
# GPIO_PIN = 2 # Jumper 3, also known as GPIO21 (Rv 1) or GPIO27 (Rv 2)
# GPIO_PIN = 3 # Jumper 4, also known as GPIO22

# define the different cards
UNKNOWN_CARD = 999
MIFARE_1K = 1001
MIFARE_4K = 1002
ULTRA_NTAG2 = 1003

# Generic family card type
MIFARE = 1
ULTRA = 2
NTAG2 = 3



################################## Routines for NFC Reader #######################################


########################################## Generic ###############################################


def NFCSetup():
    # setup up the serial port and the wiringpi software for use
    # call setup for the wiringpi2 software
    response = wiringpi2.wiringPiSetup()
    # set the GPIO pin for input
    wiringpi2.pinMode(GPIO_PIN, 0)
    # open the serial port and set the speed accordingly
    fd = wiringpi2.serialOpen('/dev/ttyAMA0', 9600)

    # clear the serial buffer of any left over data
    wiringpi2.serialFlush(fd)

    if response == 0 and fd >0:
        # if wiringpi is setup and the opened channel is greater than zero (zero = fail)
        print "PI setup complete on channel %d " % fd
    else:
        print "Unable to Setup communications"
        sys.exit()
        
    return fd

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
        return False

    # no error detected, all ok.
    return True
    
def WaitForCard(fd):
    # wait in a loop for a card to be present and then validate it.
    # Uses the Read Card Status to determine if a card is present
    
    print "Waiting for a card ...."

    nocard = True
    while nocard:
        WaitForCommandStobe()
        # print "Sending Read Card Status command" #Added for Debug purposes
        # send an ASCII 's' 0x53
        wiringpi2.serialPutchar(fd, 0x53)
        time.sleep(0.1)
        ans = ReadInt(fd)
        # print "Tag Status: %s" % hex(ans) #Added for Debug purposes

        if DecodeAcknowledgeByte(ans):
            # Card present and read
            nocard = False
            return True
    return False


def GetBlockAddress():
    # captures, validates and returns the block address
    getblockaddrress = ""
    while getblockaddrress = "":
        getblockaddrress = raw_input("Enter Block Address (0 - 255):")
        if getblockaddrress < 0 or getblockaddrress > 255:
            print "Invalid Block entered"
            getblockaddrress = ""
    return getblockaddrress
    
def GetKeyType():
    # gets and returns the key type, 0 or 1
    getkeytype = ""
    while getkeytype = "":
        getkeytype = int(raw_input("Select Key Type 0 = KeyA, 1 = KeyB"))
        if getkeytype != 0 or getkeytype != 1:
            print "Invalid Key Type Entered"
            getkeytype = ""
    return getkeytype

def GetKeyCode():
    # gets and returns the key code
    getkeycode = ""
    while getkeycode = "":
        getkeycode = raw_input("Select Key Code Number (0 - 31)")
        if getkeycode < 0 or getkeycode > 31:
            print "Invalid Key Type Entered"
            getkeycode = ""
    return getkeycode

def GetPageAddress(page_min,page_max):
    # get and validate the page address
    getpageaddress = ""
        while getpageaddress = "":
        getpageaddress = raw_input("Enter Page Address (0 - 15):")
        if getpageaddress < page_min or getpageaddress > page_max:
            print "Invalid Page Address entered"
            getpageaddress = ""
    return getpageaddress
    
########################################## Specific ##############################################


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

    nocard = True
    while nocard:
        WaitForCommandStobe()
        # print "Sending Read Card Status and UID command" #Added for Debug purposes
        # send an ASCII 'S' 0x53
        wiringpi2.serialPutchar(fd, 0x53)
        time.sleep(0.1)
        ans = ReadInt(fd)
        # print "Tag Status: %s" % hex(ans) #Added for Debug purposes

        if DecodeAcknowledgeByte(ans):
            # Card present and read
            nocard = False
            # print "Tag Present" #Added for Debug purposes
            print "Card Status"
            print "-->%s<--" % ans
            
            card_type = UNKNOWN_CARD
            # decode the ackowledge byte for card type
            # Identify the card type from bits 5 & 6
            if int(ans,2) >> 6 & 0b1) == 1:
                #if the UL Type = 1, it is a Ultralight / NTAG2 card
               card_type = ULTRA_NTAG2
                print "Ultralight / NTAG2 Card"
            elif int(ans,2) >> 5 & 0b1) == 1:
                #MiFare Type 4k byte card" 
                card_type = MIFARE_4K
                print "MiFare 4k byte card"
            else:
                # MiFare Card 1k byte card"
                card_type = MIFARE_1K
                print "MiFare 1k byte card"
   return

def ReadCardUID(fd):
    # Read the Card Status and all data blocks from within the UID
    # Note: Mifare 1k and 4k cards have a 4 byte serial number so the last 3 bytes contain dummy (0x00) data,
    #       Ultralight / NTAG2 cards have a 7 byte serial number

    print "Reading Card UID ......."

    print "Waiting for a card ...."

    nocard = True
    while nocard:
        WaitForCommandStobe()
        # print "Sending Read Card Status command" #Added for Debug purposes
        # send an ASCII 'U' 0x55
        wiringpi2.serialPutchar(fd, 0x55)
        time.sleep(0.1)
        ans = ReadInt(fd)
        # print "Tag Status: %s" % hex(ans) #Added for Debug purposes

        if DecodeAcknowledgeByte(ans):
            # Card present and read
            nocard = False
            ans = ReadText(fd)
            print "Card UID"
            print "-->%s<--" % ans
    return

def FactoryReset(fd):
    # send the factory reset command to reload default values
    WaitForCommandStobe()
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

    card_type = ""
    block_addr = ""
    key_type = ""
    key_code = ""
    page_addr = ""
    qty_data = 16
    choice = ""

    # user selection of card type
    print "**************************************************************************\n"
    print "Select Card Type: -"
    print " 1 - Mifare 1k / 4k card"
    print " 2 - Ultralight card"
    print " 3 - NTAG2 card"
    print " e - Return to main menu"
    print ""
    while choice = "":
        choice= raw_input ("Select Card Type:")
        if card_type == "1":
            # MiFare 1k or 4k card selected
            # Capture and validate data to be written - MiFare
            # Block address 0 - 255
            # Key Type 0 = KeyA, 1 = KeyB
            # Key Code Number 0 - 31
            # 16 bytes of data, each byte 0 - 255
            card_type = MIFARE
            print "Enter MiFare 1k / 4k details"
            block_addr = GetBlockAddress()
            key_type = GetKeyType()
            key_code = GetKeyCode()
            qty_data = 16
        elif choice == "2":
            # Ultra Card Type
            # Capture and validate data to be written - Ultra
            # Page Address 0 - 15
            card_type = ULTRA
            print "Enter Ultra Card details"
            page_addr = GetPageAddress(0,15)
            qty_data = 4
        elif choice == "3":
            # NTAG2 Card Type
            # Capture and validate data to be written - NTAG2
            # Page Address 0 - 63
            card_type = NTAG2
            print "Enter NTAG2 Card details"
            page_addr = GetPageAddress(0,63)
            qty_data = 4
        elif card_type = "e" or card_type == "E":
            return
    
    # Capture data based on qty_data above
    bytes_read = 0
    # create an empty list of 16 bytes to store the values in
    data = [0] * 16
    print "Enter bytes, starting with LSB"
    while bytes_read < qty_data:
        print "Enter byte %d:" % data_read
        value_input = int(raw_input("Enter byte %d:" % data_read))
        if value_input >= 0 AND value_input <=255:
            data [bytes_read] = value_input
            bytes_read = bytes_read + 1
    
    print "Data Entered is %s" % data


    # Wait for a card to be present, capture type
    # check status and if ok continue
    if WaitForCard(fd):
        # Write Block / Page of data
        # send the write block command ASCII 'W' 0x57
        wiringpi2.serialPutchar(fd, 0x55)
        
        if card_type = MIFARE:
            wiringpi2.serialPutchar(fd, block_addr)
            # move key_type into the highest bit
            key_type = key_type << 7
            # key_code is already a number 0 - 31
            wiringpi2.serialPutchar(fd, (key_type + key_code)
        elif card_type = ULTRA or card_type = NTAG2:
            # send the card page address
            wiringpi2.serialPutchar(fd, page_addr)
            # send a dummy byte
            wiringpi2.serialPutchar(fd, 0x00)

        # now send the data arguments, always 16 bytes
        bytes_sent = 0
        while bytes_sent < 16:
            #print "Data to send %d, byte number %d" % (data[bytes_sent], bytes_sent)       #added for debug
            wiringpi2.serialPutchar(fd, data[bytes_sent])
            bytes_sent = byes_sent + 1
    # Check Status for error
    ans = ReadInt(fd)
    # print "Write Status: %s" % hex(ans) #Added for Debug purposes
    if DecodeAcknowledgeByte(ans):
        # Card present and read
        nocard = False
        print "Card Write successful"
    return

def ReadTypeIdent(fd):
    # Read the ATQA and SAK codes from the card to identify the exact type
    # Sends a 0x78, 'x' and receives an acknowldge response, then 3 bytes containing
    #   ATQA - MSB
    #   ATQA - LSB
    #   SAK
    # See the spec for the meaning of each of the codes.
    
    atqa_msb = ""
    atqa_lsb = ""
    sak = ""

    print "Reading Card Type ......."

    print "Waiting for a card ...."
    
    nocard = True
    while nocard:
        WaitForCommandStobe()
        # print "Sending Type Identification command" #Added for Debug purposes
        # send an ASCII 'x' 0x78
        wiringpi2.serialPutchar(fd, 0x78)
        time.sleep(0.1)
        ans = ReadInt(fd)
        # print "Tag Status: %s" % hex(ans) #Added for Debug purposes

        if DecodeAcknowledgeByte(ans):
            # Card present and read
            nocard = False
            # print "Tag Present" #Added for Debug purposes
            
            #read the 3 bytes opf infomation
            atqa_msb = ReadInt(fd)
            atqa_lsb = ReadInt(fd)
            sak = ReadInt(fd)
            print "Card Type "
            print "ATQA (msb / lsb) : %s / %s" % atqa_msb, atqa_lsb
            print "SAK              : %s" % sak
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
    # Read 16 bytes of data from the specified block
    # A block is made up of 16 bytes, with 4 (16 on upper) blocks in a sector
    # Blocks 3, 7, 11, 15 etc contain Security data and Access bits

    card_type = ""
    block_addr = ""
    key_type = ""
    key_code = ""
    page_addr = ""
    choice = ""

    # user selection of card type
    print "**************************************************************************\n"
    print "Select Card Type: -"
    print " 1 - Mifare 1k / 4k card"
    print " 2 - Ultralight card"
    print " 3 - NTAG2 card"
    print " e - Return to main menu"
    print ""
    while choice = "":
        choice= raw_input ("Select Card Type:")
        if card_type == "1":
            # MiFare 1k or 4k card selected
            # Capture and validate data to be written - MiFare
            # Block address 0 - 255
            # Key Type 0 = KeyA, 1 = KeyB
            # Key Code Number 0 - 31
            # 16 bytes of data, each byte 0 - 255
            card_type = MIFARE
            print "Enter MiFare 1k / 4k details"
            block_addr = GetBlockAddress()
            key_type = GetKeyType()
            key_code = GetKeyCode()
        elif choice == "2":
            # Ultra Card Type
            # Capture and validate data to be written - Ultra
            # Page Address 0 - 15
            card_type = ULTRA
            print "Enter Ultra Card details"
            page_addr = GetPageAddress(0,15)
        elif choice == "3":
            # NTAG2 Card Type
            # Capture and validate data to be written - NTAG2
            # Page Address 0 - 63
            card_type = NTAG2
            print "Enter NTAG2 Card details"
            page_addr = GetPageAddress(0,63)
        elif card_type = "e" or card_type == "E":
            return
    
    # Wait for a card to be present, capture type
    # check status and if ok continue
    if WaitForCard(fd):
        # Write Block / Page of data
        # send the write block command ASCII 'R' 0x52
        wiringpi2.serialPutchar(fd, 0x52)
        
        if card_type = MIFARE:
            wiringpi2.serialPutchar(fd, block_addr)
            # move key_type into the highest bit
            key_type = key_type << 7
            # key_code is already a number 0 - 31
            wiringpi2.serialPutchar(fd, (key_type + key_code)
        elif card_type = ULTRA or card_type = NTAG2:
            # send the card page address
            wiringpi2.serialPutchar(fd, page_addr)
            # send a dummy byte
            wiringpi2.serialPutchar(fd, 0x00)

        # Check Acknowledge Status for error
        ans = ReadInt(fd)
        # print "Read Status: %s" % hex(ans) #Added for Debug purposes
        if DecodeAcknowledgeByte(ans):
            # Card present and read
            nocard = False
            data_read = ReadText(fd)
            print "Card Read successful"
            print "-->%s<--" % data_read
    
    return

def IncValue(fd):
    # Command to increment integer within a MiFare Value Data Structure
    src_block_addr = ""
    key_type = ""
    key_code = ""
    dest_block_addr = ""
    qty_data = 4
    
    print ""
    print "Only works with Mifare 1k / 4k cards"
    # MiFare 1k or 4k card selected
    # Capture and validate data to be written - MiFare
    # Block address 0 - 255
    # Key Type 0 = KeyA, 1 = KeyB
    # Key Code Number 0 - 31
    # 16 bytes of data, each byte 0 - 255
    print "***** Enter Source details *****"
    src_block_addr = GetBlockAddress()
    key_type = GetKeyType()
    key_code = GetKeyCode()
    print "***** Enter Destination details *****"
    dest_block_addr = GetBlockAddress()
    
    # Capture data based on 4 bytes
    bytes_read = 0
    # create an empty list of 4 bytes to store the values in
    data = [0] * qty_data
    print "Enter bytes, starting with LSB"
    while bytes_read < qty_data:
        print "Enter byte %d:" % data_read
        value_input = int(raw_input("Enter byte %d:" % data_read))
        if value_input >= 0 AND value_input <=255:
            data [bytes_read] = value_input
            bytes_read = bytes_read + 1
    
    print "Data Entered is %s" % data

    # Wait for a card to be present, capture type
    # check status and if ok continue
    if WaitForCard(fd):
        # Write Block / Page of data
        # send the write block command ASCII 'I' 0x49
        wiringpi2.serialPutchar(fd, 0x49)
        
        wiringpi2.serialPutchar(fd, src_block_addr)

        # move key_type into the highest bit
        key_type = key_type << 7
        # key_code is already a number 0 - 31
        wiringpi2.serialPutchar(fd, (key_type + key_code)

        wiringpi2.serialPutchar(fd, dest_block_addr)

        # now send the data arguments, always 4 bytes
        bytes_sent = 0
        while bytes_sent < qty_data:
            #print "Data to send %d, byte number %d" % (data[bytes_sent], bytes_sent)       #added for debug
            wiringpi2.serialPutchar(fd, data[bytes_sent])
            bytes_sent = byes_sent + 1
            
    # Check Status for error
    ans = ReadInt(fd)
    # print "Write Status: %s" % hex(ans) #Added for Debug purposes
    if DecodeAcknowledgeByte(ans):
        # Card present and read
        nocard = False
        print "Card Increment Value successful"
    return

def DecValue(fd):
    # Command to decrement integer within a MiFare Value Data Structure
    src_block_addr = ""
    key_type = ""
    key_code = ""
    dest_block_addr = ""
    qty_data = 4
    
    print ""
    print "Only works with Mifare 1k / 4k cards"
    # MiFare 1k or 4k card selected
    # Capture and validate data to be written - MiFare
    # Block address 0 - 255
    # Key Type 0 = KeyA, 1 = KeyB
    # Key Code Number 0 - 31
    # 16 bytes of data, each byte 0 - 255
    print "***** Enter Source details *****"
    src_block_addr = GetBlockAddress()
    key_type = GetKeyType()
    key_code = GetKeyCode()
    print "***** Enter Destination details *****"
    dest_block_addr = GetBlockAddress()
    
    # Capture data based on 4 bytes
    bytes_read = 0
    # create an empty list of 4 bytes to store the values in
    data = [0] * qty_data
    print "Enter bytes, starting with LSB"
    while bytes_read < qty_data:
        print "Enter byte %d:" % data_read
        value_input = int(raw_input("Enter byte %d:" % data_read))
        if value_input >= 0 AND value_input <=255:
            data [bytes_read] = value_input
            bytes_read = bytes_read + 1
    
    print "Data Entered is %s" % data

    # Wait for a card to be present, capture type
    # check status and if ok continue
    if WaitForCard(fd):
        # Write Block / Page of data
        # send the write block command ASCII 'D' 0x44
        wiringpi2.serialPutchar(fd, 0x44)
        
        wiringpi2.serialPutchar(fd, src_block_addr)

        # move key_type into the highest bit
        key_type = key_type << 7
        # key_code is already a number 0 - 31
        wiringpi2.serialPutchar(fd, (key_type + key_code)

        wiringpi2.serialPutchar(fd, dest_block_addr)

        # now send the data arguments, always 4 bytes
        bytes_sent = 0
        while bytes_sent < qty_data:
            #print "Data to send %d, byte number %d" % (data[bytes_sent], bytes_sent)       #added for debug
            wiringpi2.serialPutchar(fd, data[bytes_sent])
            bytes_sent = byes_sent + 1
            
    # Check Status for error
    ans = ReadInt(fd)
    # print "Write Status: %s" % hex(ans) #Added for Debug purposes
    if DecodeAcknowledgeByte(ans):
        # Card present and read
        nocard = False
        print "Card Decrement Value successful"
    return


def TransferValue(fd):
    # Command to transfer integer within a MiFare Value Data Structure
    src_block_addr = ""
    key_type = ""
    key_code = ""
    dest_block_addr = ""
    qty_data = 4
    
    print ""
    print "Only works with Mifare 1k / 4k cards"
    # MiFare 1k or 4k card selected
    # Capture and validate data to be written - MiFare
    # Block address 0 - 255
    # Key Type 0 = KeyA, 1 = KeyB
    # Key Code Number 0 - 31
    # 16 bytes of data, each byte 0 - 255
    print "***** Enter Source details *****"
    src_block_addr = GetBlockAddress()
    key_type = GetKeyType()
    key_code = GetKeyCode()
    print "***** Enter Destination details *****"
    dest_block_addr = GetBlockAddress()
    
    # Wait for a card to be present, capture type
    # check status and if ok continue
    if WaitForCard(fd):
        # Write Block / Page of data
        # send the write block command ASCII 'T' 0x54
        wiringpi2.serialPutchar(fd, 0x54)
        
        wiringpi2.serialPutchar(fd, src_block_addr)

        # move key_type into the highest bit
        key_type = key_type << 7
        # key_code is already a number 0 - 31
        wiringpi2.serialPutchar(fd, (key_type + key_code)

        wiringpi2.serialPutchar(fd, dest_block_addr)

    # Check Status for error
    ans = ReadInt(fd)
    # print "Write Status: %s" % hex(ans) #Added for Debug purposes
    if DecodeAcknowledgeByte(ans):
        # Card present and read
        nocard = False
        print "Card Transfer Value successful"
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

#Initiate Communications
comms = NFCSetup()

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


