# ProcMon
This is a process monitor Python script that keeps an eye on the TOP command output for CPU and RAM utilization. The script also provides statistics and graphs when a user terminates it.

The script is designed in such a way that the user needs to start the script before executing their binary, the script will continuously pull the top command output to check if it contains the binary name in it.

## Steps to execute
``` python3 ProcMon.py adeshpande sp_xdesvr ```

ProcMon expects the user to give 2 arguments 
1. Username of Linux
2. Binary name which you want to monitor.

## Requirements
Python3 installed 3.6 or above <br>
matplotlib (optional) if you need graphs as well. <br>

## Note:
- In case there are 2 processes with the same name, then resources used by both of them are added. Having understood that we are monitoring multiple processes having the same name on the system. So we are interested in the total resources used by them.

## Example output
Statistics are shown on the console. <br>
![image](https://github.com/AadityaDeshpande/ProcMon/assets/41305804/f4ce644a-2f42-4139-b802-cd60deafd613)

Graph generated for CPU <br>
![CPU_vs_TIME_sp_xdesvr_20231206-12H_59M_12S](https://github.com/AadityaDeshpande/ProcMon/assets/41305804/82aa06a8-6c6e-4266-a6d7-9bd28acad63b)

Graph generated for RAM <br>
![RAM_vs_TIME_sp_xdesvr_20231206-12H_59M_12S](https://github.com/AadityaDeshpande/ProcMon/assets/41305804/d3cc5868-5ec5-4889-9511-7ee79f6a39ad)


## Future scope.
- Save the statistics in a file and analysis in a CSV file that can be seen on an Excel file.
- Once we have the statistics file, we can further develop an analysis.py file that can predict the CPU or RAM usage using ML or any other way.
- Currently, the script uses the TOP command output and looks for columns %CPU and %MEM. I am sure this script can be extended to include other columns as well.
- We can optimize the function start_monitor by reducing the first 7/8 lines of stats.
