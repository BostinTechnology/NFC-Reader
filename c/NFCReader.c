
/*
 * NFCReader.c:
 *	Example code on accessing the NFC Reader and reading data from NFC Cards
 *
 *
 *
 * The code here is experimental, and is not intended to be used
 * in a production environment. It demonstrates the basics of what is
 * required to get the Raspberry Pi receiving NFCdata.
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation as version 2 of the License.
 *
 * BUG: Currently doesn't recognise the card correctly
 * TODO: Implement U command
 */

#include <stdio.h>
#include <string.h>
#include <errno.h>


#include <wiringPi.h>
#include <wiringSerial.h>


// set for GPIO Pin to use based on the jumper connection
#define GPIO_PIN 1       // Jumper 1, also known as GPIO18
// #define GPIO_PIN 0          // Jumper 2, also known as GPIO17
// #define GPIO_PIN 2       // Jumper 3, also known as GPIO21 (Rv 1) or GPIO27 (Rv 2)
// #define GPIO_PIN 3       // Jumper 4, also known as GPIO22

// Define global variables

int fd;	// File handle for connection to the serial port.


// Helper functions

void WaitForCTS()
{
	// Generic call to wait for the CTS going high
	// CTS is implemented via the use of the GPIO as the UART on the
	// Pi doen't have any control lines.
	serialFlush(fd);

	while (digitalRead(GPIO_PIN) == HIGH)
	{
		// Do Nothing
		// printf(".");
	}

}

void GetTextResult()
{
	// Generic routine to return text from the serial port.

	while (serialDataAvail (fd))
	{
		printf ("%c", serialGetchar (fd)) ;
		fflush (stdout) ;
	}
	printf("\n\n");
}

int DecodeAcknowledgeByte(ackbyte)
{
    // Generic routine to decode the response
    
    if (ackbyte == 0x80)
    {
        // No card present
        // printf("No Card Present");  //Added for Debug Purposes
        return 1;
    }
    else if ((ackbyte & 0b00000001) == 1)
    {
        // EEPROM Error if True
        printf ("EEPROM Error");
        return 1;
    }
    else if (((ackbyte & 0b00000010) >> 1) == 0)
    {
        // Card Not OK if 0
        printf ("Card Not OK");
        return 1;
    }
    else if (((ackbyte & 0b00000100) >> 2) == 0)
    {
        // Receive Error = 0
        printf ("Receive Error");
        return 1;
    }
    else if (((ackbyte & 0b00001000) >> 3) == 1)
    {
        // RS232 Error = 1
        printf ("RS232 Error");
        return 1;
    }
    else if (((ackbyte & 0b01000000) >> 6) == 1)
    {
        // MFRC Error = 1
        printf ("MFRC Error");
        return 1;
    }

    return 0;
}


int main ()
{
//


// Initialise WiringPi so we can use the GPIO on the Raspberry Pi

 if (wiringPiSetup () == -1)
  {
    fprintf (stdout, "Unable to start wiringPi: %s\n", strerror (errno)) ;
    return 1 ;
  }

  pinMode(GPIO_PIN,INPUT);	// We are using GPIO_PIN as the pin to identify the "CTS" function



  if ((fd = serialOpen ("/dev/ttyAMA0", 9600)) < 0)  // Try to open a connection to the serial port
  {
   fprintf (stderr, "Unable to open serial device: %s\n", strerror (errno)) ;
    return 1 ;
  }


char option;
int noCard;


do {
	printf(" \n\n");
	printf("**************************************************************************\n");
	printf("Available commands: -\n\n");
	printf("z - Display firmware version information\n");
	printf("S - Acknowledge presence of Card\n");
	printf("U - Read Card UID\n");
	printf("e - Exit program \n");
	printf(" \n");

	printf("Please select command -> ");

	option = getchar();
	getchar();  // have to press enter and this consumes the enter character


       switch (option)
       {

            case 'z': // Read the firmware version

			printf("\nRead Firmware Details - Reading device..>\n\n");

			WaitForCTS();

            serialPutchar(fd, 0x7A); // Send 'z' to the PirFix

			delay(100); // ??? Need to wait otherwise the command does not work

			GetTextResult();

			break;


		case 'S': // Read the status of the NFC device

			noCard = 1;

			printf("\nWaiting for a Card ....\n");

			while (noCard == 1)
			{
				WaitForCTS();

				serialPutchar(fd, 0x53); // Send 'S' to the PirFix

				delay(100); // ??? Need to wait otherwise the command does not work

				while ( serialDataAvail(fd))  // Whilst data is being sent back from the device
				{
					char result;
					result = serialGetchar(fd);	// Get character
					if ((DecodeAcknowledgeByte(result)) == 0)  // confirm that the Card is present, valid and no errors
					{
						noCard = 0;		// set this so the outer while loop can terminate
						printf ("\nCard present.\n\n");
					}
				}
			}
			break;




	    case 'e':
	    	printf("Exiting.......\n");
		option = 'e';
		break;

            default:
	    	printf("Unrecognised command!\n");


       }

       fflush (stdout) ;

     } while(option != 'e');

     serialClose(fd);

return(0);

}

