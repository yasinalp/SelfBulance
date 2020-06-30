#include "forward_propagation.h"
#include "ap_int.h"
#include <stdio.h>
#include "selfbulance_output_weights0.h"
#include "selfbulance_hidden_weights0.h"
#include <stdio.h>

#define inputsize 3
#define hiddensize 8
#define actionnum 3
int max=0;
int k=0;


void inference(unsigned int input_neurons[inputsize], float* output){
	float hidden_neurons[hiddensize];
	if (k==0){
		input_layer_to_hidden_layer(input_neurons, hidden_weights0, hidden_neurons);
		hidden_layer_to_output_layer(hidden_neurons, output_weights0, output);
	}
	else if(k==1){
		input_layer_to_hidden_layer(input_neurons, hidden_weights1, hidden_neurons);
		hidden_layer_to_output_layer(hidden_neurons, output_weights1, output);
	}
	else if(k==2){
			input_layer_to_hidden_layer(input_neurons, hidden_weights2, hidden_neurons);
			hidden_layer_to_output_layer(hidden_neurons, output_weights2, output);
		}
	printf("output of a0: %f\n", output[0]);
}


void input_layer_to_hidden_layer(unsigned int input[inputsize], float weights[inputsize][hiddensize], float output[hiddensize]){
	for(int col_o = 0; col_o < hiddensize; col_o++)
		output[col_o] = 0;
	for(int col_w = 0; col_w < hiddensize; col_w++)
		for(int col_i = 0; col_i < inputsize; col_i++)
			output[col_w] += input[col_i] * weights[col_i][col_w];
}
void hidden_layer_to_output_layer(float input[hiddensize], float weights[hiddensize], float *output){
	output[0] = 0.0;
	for(int col_i = 0; col_i < hiddensize; col_i++)
		output[0] += input[col_i] * weights[col_i];
}


void dnn(unsigned int distances[inputsize], float output[inputsize], unsigned int action[1]){
#pragma HLS INTERFACE m_axi port=distances bundle=gmem0
#pragma HLS INTERFACE m_axi port=output bundle=gmem1
#pragma HLS INTERFACE m_axi port=action bundle=gmem2
#pragma HLS INTERFACE s_axilite port=return bundle=control



	for (k=0;k<actionnum;k++)
	{
		inference(distances,output+k);
	}

	for(int i=1;i<inputsize;i++){
		if (output[i]>output[max])
			max=i;
	}
	action[0]=max;


	printf("action: %d", action[0]);
	return;
}
