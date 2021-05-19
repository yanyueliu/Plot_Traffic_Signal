# Plot_Traffic_Signal
 
## Overview
This program can plot given traffic signal settings and output figure which is friendly for reading.

### Input
link.csv
<br>node.csv
<br>output_signal.csv

#### Format of input files
<b>link.csv</b>
<br> link.csv must contain link_id, from_node, to_node and lanes columns. Length and lane_2 columns are not used yet but they are also required, though value of these columns can be given alternatively.
<br><b>node.csv</b>
<br> node.csv must contain node_id, node_type, x_coord and y_coord. Here, node_type 0 represents signalized intersection and node_type 6 represents dead end. X_coord and y_coord are longtitude and latitude, resepectively.
<br><b>output_signal.csv</b>
<br> output_signal.csv must contain from, to, gdirect, theta and phi. Here from is link id that approaching to this intersection and to is link id that exiting from this intersection.
<br> gdirect is a defination of traffic turning directions.
<br> gdirect = 1 means that this movement is turning left. gdirect = 2 menas that this movement is going straight. gdirect = 3 means that this movement is turning right. In this program, right turn is ignored.
<br> theta means start time of green phase, phi means duration time of green phase.

### Output
![image](https://github.com/yanyueliu/Plot_Traffic_Signal/blob/master/Pic/4.png)
