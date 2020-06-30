
#include <stdio.h>
#include "platform.h"
#include "xil_printf.h"
#include "xil_io.h"
#include "distancesensor.h"
#include "motor_driver_5_act.h"
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include "xstatus.h"
#include "xuartlite.h"

unsigned int *gmem2 = (unsigned int *)0x03000000;
float *gmem1 = (float *)0x02000000;
unsigned int *gmem0 = (unsigned int *)0x01000000;
int* dram_hls_control = (int*)0x43C00000;

unsigned int dcMotorPtr = unsigned int 0x43C10000;
unsigned int distancePtr = unsigned int 0x43C20000;

int dq_duration = 2000;
int dq_step_ms = 200;
unsigned int d[3];
unsigned int action, result;





/************************** Constant Definitions *****************************/

/*
 * The following constants map to the XPAR parameters created in the
 * xparameters.h file. They are defined here such that a user can easily
 * change all the needed parameters in one place.
 */
#define UARTLITE_DEVICE_ID	XPAR_UARTLITE_0_DEVICE_ID

/*
 * The following constant controls the length of the buffers to be sent
 * and received with the UartLite, this constant must be 16 bytes or less since
 * this is a single threaded non-interrupt driven example such that the
 * entire buffer will fit into the transmit and receive FIFOs of the UartLite.
 */
#define TEST_BUFFER_SIZE 32




/************************** Variable Definitions *****************************/

XUartLite UartLite;		/* Instance of the UartLite Device */

/*
 * The following buffers are used in this example to send and receive data
 * with the UartLite.
 */
u8 SendBuffer[TEST_BUFFER_SIZE];	/* Buffer for Transmitting Data */
u8 RecvBuffer[TEST_BUFFER_SIZE];	/* Buffer for Receiving Data */

unsigned int SentCount, getCount;
unsigned int ReceivedCount = 0;
int Status;
int delay = 0;
char act[32]={0};

int main()
{
	init_platform();
	Xil_DCacheDisable();

	Status = XUartLite_Initialize(&UartLite, UARTLITE_DEVICE_ID);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}
	xil_printf("\n\n\n\rHello\n\r");

	SendBuffer[0] = 49;
	SendBuffer[1] = 10;  // New line feed in ascii

	while (1) {
		MOTOR_DRIVER_5_ACT_mWriteReg(dcMotorPtr, 0, 3);
		sleep(2);
		SentCount = XUartLite_Send(&UartLite, SendBuffer, 2);
		if (SentCount != 2) {
			xil_printf("Failed\n\r");
			return XST_FAILURE;
		}
		ReceivedCount = 0;  // each time start from first byte of buff
		action = 0;  // if data is not an action command, go straight
		memset(RecvBuffer, 0, sizeof(RecvBuffer));  // Reset recv buff so that act value works correctly
		while (1) {
			getCount = XUartLite_Recv(&UartLite, RecvBuffer + ReceivedCount, 1);
			ReceivedCount += getCount;
			if (getCount > 0){
				xil_printf("%c", RecvBuffer[ReceivedCount-1]);
				if (RecvBuffer[ReceivedCount-1] == 10) {
					xil_printf(" newline\n\r");
					break;
				}
				else if (RecvBuffer[ReceivedCount-1] == 'q'){  // obstacle detected dq is active
					dq_phase();
					action = 3;
				}
				else if (RecvBuffer[ReceivedCount-1] == '\\'){  // action is left
					action = 1;
				}
				else if (RecvBuffer[ReceivedCount-1] == '/'){  // action is right
					action = 2;
				}
				else if (RecvBuffer[ReceivedCount-1] == '_'){  // action is stop
					action = 3;
				}
			}
		}

		if (action == 0) {
			delay = atoi(RecvBuffer);
		}
		else if (action == 1) {
			delay = 1050;
		}
		else if (action == 2) {
			delay = 1100;
		}
		else delay = 1000;

		xil_printf("act: %d\t delay: %d\n\r",action,delay);

		MOTOR_DRIVER_5_ACT_mWriteReg(dcMotorPtr, 0, action);

		usleep(delay*1000);
	}
	return 0;

}

void dq_phase()
{
	int heading = 0;
	int time_ms = 0;
	while(time_ms < dq_duration){
		d[0] = DISTANCESENSOR_mReadReg(distancePtr, 0);
		d[1] = DISTANCESENSOR_mReadReg(distancePtr, 4);
		d[2] = DISTANCESENSOR_mReadReg(distancePtr, 8);

		for (int i=0; i<3; i++){
			gmem0[i] = d[i];
		}

		dram_hls_control[0] |= 0x1;

		while((dram_hls_control[0]&0x2) != 0x2);

		action = gmem2[0];

		MOTOR_DRIVER_5_ACT_mWriteReg(dcMotorPtr, 0, action);

		usleep(dq_step_ms * 1000);
		if (action == 1) heading--;
		else if (action == 2) heading ++;
		time_ms += dq_step_ms;

		MOTOR_DRIVER_5_ACT_mWriteReg(dcMotorPtr, 0, 3);
		usleep(100 * 1000);
	}

	while (heading != 0){
		if (heading > 0){
			MOTOR_DRIVER_5_ACT_mWriteReg(dcMotorPtr, 0, 1);
			usleep(dq_step_ms * 1000);
			MOTOR_DRIVER_5_ACT_mWriteReg(dcMotorPtr, 0, 3);
			usleep(100 * 1000);
			heading--;
		}
		else if (heading < 0){
			MOTOR_DRIVER_5_ACT_mWriteReg(dcMotorPtr, 0, 2);
			usleep(dq_step_ms * 1000);
			MOTOR_DRIVER_5_ACT_mWriteReg(dcMotorPtr, 0, 3);
			usleep(100 * 1000);
			heading++;
		}
	}

}
