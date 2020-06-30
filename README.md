# SelfBulance
Xilinx Open Hardware Contest Project

This project aims that a pre-trained agent that is able to receive route info from where the agent is to target location and follow the path. 
When there is an obstacle which is unknown by the map service, the agent continues to track the route and avoid from collision with this obstacle.
Since our environment so small, real map services (e.g. Google Maps etc.) and location solutions (e.g. GPS) could not be used.
We have implemented a map service in our training environment within Godot. Map finds the shortest path and gives the route directions to the agent.
Agent receives these directions and follow that path whereas collision avoidance is done by a deep neural network.
