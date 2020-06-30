# SelfBulance - xohw20_205
Xilinx Open Hardware Contest Project

This project aims to infer a pre-trained agent as an SoC solution.The agent is able to receive route info from its current location to a target location and follow the path.  
When there is an obstacle, the agent can continue to track the route and avoid any collision with this obstacle.
Since our environment is so small, real map services (e.g. Google Maps etc.) and location solutions (e.g. GPS) could not be used.
We have implemented a map service in our training environment within Godot. Map service finds the shortest path and gives the route directions to the agent.
Agent receives these directions and follows that path whereas collision avoidance is done by a deep neural network.

Deep neural network, sensor handler and motor driver logic is implemented in PL part of Zedboard in order to reduce energy consumption and latency.
PS part of Zedboard is responsible for management of data flow between distance sensor, neural network and motor driver IP.

![Block Diagram](/block_design.png)
