/*
 * NFCReader.c
 *
 * Copyright 2016  <pi@R-Pi-01>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 *
 */


#include <stdio.h>
#include <string.h>
#include <errno.h>


#include <wiringPi.h>
#include <wiringSerial.h>

#define GPIO17 0		// This defines the GPIO reference for wiringPi
#define GPIO18 1		// This defines the GPIO reference for wiringPi

#define GPIO GPIO18

// Define global variables

int fd;	// File handle for connection to the serial port.


// Helper functions

void WaitForCTS()
{
	// Generic call to wait for the CTS going high
	// CTS is implemented via the use of the GPIO as the UART on the
	// Pi doen't have any control lines.
	serialFlush(fd);

	while (digitalRead(GPIO) == HIGH)
	{
		// Do Nothing
		//printf(".");
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



int GetAntennaStatus()
{
	// Perform a firmware read to check the status of the antenna

	WaitForCTS();
    serialPutchar(fd, 0x53);  // Send card status command
	delay(100);

	if ((serialGetchar(fd) & 0x40) == 0x40 )  // Checking bit 6.  If set, indicates antenna fault
	{
		printf("ERROR : ANTENNA or Eprom fault. Please check the antenna is correctly installed.\n\n");
		return 1;  // return value set to indicate error
	}
	else
	{
		printf("PirFIX : ANTENNA and Eprom Confirmed as Working\n");
		return 0;
	}

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

// The PirFix can use one of the following GPIO pins configured as an input
//
// GPIO17
// GPIO18
// GPIO21
// GPIO22
//

  pinMode(GPIO,INPUT);	// We are using GPIO as the pin to identify the "CTS" function



  if ((fd = serialOpen ("/dev/ttyAMA0", 9600)) < 0)  // Try to open a connection to the serial port
  {
   fprintf (stderr, "Unable to open serial device: %s\n", strerror (errno)) ;
    return 1 ;
  }
  else
  {
  	// We have opened communications with the onboard Serial device
	int antennaOK = 0;

	printf("Opened communications with PirFix.\n");  // Communications opened successfully

	antennaOK = GetAntennaStatus();  // Check status of the antenna.

	if (antennaOK ==1)
	{
	return 1; // if there is an antenna fault, exit with a non-zero return code
	 }
  }




char option, tagOption;
int noTag;


do {
	printf(" \n\n");
	printf("**************************************************************************\n");
	printf("Available commands: -\n\n");
	printf("z - Display firmware version information\n");
	printf("x - Identify Tag type\n");
	printf("S - Acknowledge presence of Tag\n");
	printf("F - Perform a Factory Reset \n");
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


		case 'x': // Identify the tag type
			noTag = 1;

			printf("\nWaiting to identify  a tag ....\n");

			while (noTag == 1)
			{
				WaitForCTS();

				serialPutchar(fd, 0x78); // Send 'x' to the PirFix

				delay(100); // ??? Need to wait otherwise the command does not work

				while ( serialDataAvail(fd))  // Whilst data is being sent back from the device
				{
					char result;
					result = serialGetchar(fd);	// Get the result/ack character

					switch (result )
					{
						case 0xa6:
							{
								printf("Tag Type MF UL 4kB (ATQAmsb - ATQAlsb - SAK)\n");
								while (serialDataAvail(fd))
								{
									int data;
									data = serialGetchar(fd);
									printf("%#.2x:", data);
								}
								printf("\n");
								noTag = 0;

							}
							break;

						case 0x86:
							{
								printf("Tag Type MF UL 1kB (ATQAmsb - ATQAlsb - SAK)\n");
								while (serialDataAvail(fd))
								{
									int data;
									data = serialGetchar(fd);
									printf("%#.2x:", data);
								}
								printf("\n");
								noTag = 0;

							}
							break;


						default :
								printf("Tag Type %#.2x (ATQAmsb - ATQAlsb - SAK)\n", result);
								while (serialDataAvail(fd))
								{
									int data;
									data = serialGetchar(fd);
									printf("%#.2x:", data);
								}
								printf("\n");
								noTag = 1;
							break;



					}

				}

			}
			break;



		case 'S': // Read the status of the RFID device

			noTag = 1;

			printf("\nWaiting for a tag ....\n");

			while (noTag == 1)
			{
				WaitForCTS();

				serialPutchar(fd, 0x55); // Send 'U' to the PirFix

				delay(100); // ??? Need to wait otherwise the command does not work

				while ( serialDataAvail(fd))  // Whilst data is being sent back from the device
				{
					char result;
					result = serialGetchar(fd);	// Get the result/ack character

					switch (result & 0xf0)
					{
						case 0xa6:
							{
								printf("Ack = %#.2x\n",result);
								printf("Tag identified - MF Standard 1k Type\n");
								printf("Serial Number = ");
								while (serialDataAvail(fd))
								{
									int data;
									data = serialGetchar(fd);
									printf("%2x:", data);
								}
								printf("\n");
								noTag = 0;

							}
							break;

						case 0x86:
							{
								printf("Ack = %#.2x\n", result);
								printf("Tag identified - MF Standard 1k Type\n");
								printf("Serial Number = ");
								while (serialDataAvail(fd))
								{
									int data;
									data = serialGetchar(fd);
									printf("%2x:", data);
								}
								printf("\n");
								noTag = 0;

							}
							break;

						case 0xb0:
							{
								printf("Ack = %#.2x\n", result);
								printf("Tag identified - MF Standard 1k Type\n");
								printf("Serial Number = ");
								while (serialDataAvail(fd))
								{
									int data;
									data = serialGetchar(fd);
									printf("%2x:", data);
								}
								printf("\n");
								noTag = 0;

							}
							break;


						default :
							printf("result = %#.2x\n", result);
							break;



					}




				}



			}
			break;


        case 'F': // Perform a factory reset

			printf("\nPerforming a factory reset ....\n");

			serialPutchar(fd, 0x46);	// this command sequence is
			serialPutchar(fd, 0x55);	//
			serialPutchar(fd, 0xAA);	// required to force a factory reset.

			delay(100);

			printf("\n\nFACTORY RESET COMPLETE \n\n");


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



