import subprocess
import time
import sys
from statistics import mode, median, mean, pstdev
import socket

class ProcMon:
    sleep_time: float = 0                           # Sleep timer, for call in between top commands.
    date_time_format: str = "%Y%m%d-%HH_%MM_%SS"    # This will be used during the graph generation.

    def __init__(self, username: str, process_name: str) -> None:
        ''' Initialize the member variables '''
        self.username: str = username
        self.process_name: str = process_name
        self.total_mem_mb: int = 0            # Total memory available on system in MB
        self.total_cpu_count: int = 0         # Total CPU(s) available on system
        self.total_cpu_mhz: float = 0.0       # Clock cycle information per CPU
        self.cpu_percentages: list = []       # List that hold the CPU use all process
        self.mem_percentages: list = []       # List that hold the MEM use all process
        self.timestamps: list = []            # List that hold the timestamp for each process
        self.pid_to_time_map: dict = dict()   # Map of map that holds <pid, <first seen time, last seen time> >
    
    def get_system_RAM_info(self) -> None:
        ''' This method will use free command to get the total RAM available on system '''
        output = subprocess.check_output(['free', '--mega'], universal_newlines=True)
        self.total_mem_mb = int([i for i in output.split('\n')[1].split(" ") if i != ''][1])
        print(f"Current system has Total RAM of size {self.total_mem_mb} MB i.e. {round(self.total_mem_mb/1024, 2)} GB")
    
    def get_acutal_mem_used(self, mem_in_percentage: float) -> float:
        ''' When we get the memory in %, this function calculates the acutal memory used '''
        return (round((float(self.total_mem_mb))*(mem_in_percentage/100), 3))
    
    def get_non_zero_median(self, stats_list: list) -> float:
        ''' When process is waiting for long time it might happen that median will reach zero, so will filter out 0'''
        median_val = median(stats_list)
        if (median_val == 0):
            non_zero_list = [i for i in stats_list if i != 0]
            if len(non_zero_list) > 0:
                median_val = median(non_zero_list)
        return round(median_val, 3)
    
    def get_system_CPU_info(self) -> None:
        ''' This method will get the CPU count and its clock cycles in MHz using lscpu command '''
        output = subprocess.check_output(['lscpu'], universal_newlines=True)
        for lscpu_line in output.split('\n'):
            if "CPU(s):" in lscpu_line:
                cpu_list = [i for i in lscpu_line.split(" ") if i != '']
                if cpu_list[0] == "CPU(s):":
                    self.total_cpu_count = int(cpu_list[1])
                    print(f"Current system has CPU(s): {self.total_cpu_count}")
            if "CPU MHz:" in lscpu_line:
                cpu_list = [i for i in lscpu_line.split(" ") if i != '']
                self.total_cpu_mhz = float(cpu_list[2])
                print(f"Current system has CPU MHz: {self.total_cpu_mhz}")
    
    def map_pid_with_time(self, pid: str) -> None:
        ''' This method populated a map that keeps track of  <pid, <first seen time, last seen time>>'''
        if pid not in self.pid_to_time_map.keys():
            self.pid_to_time_map.update({pid: [time.time(), time.time()]})
        else:
            self.pid_to_time_map[pid][1] = time.time()
    
    def print_pid_with_time(self) -> None:
        for k,v in self.pid_to_time_map.items():
            print(f"for pid = {k} Total time= {round(v[1] - v[0], 3)} sec")
        if list(self.pid_to_time_map.keys()):
            start_time_pid = list(self.pid_to_time_map.keys())[0]
            end_time_pid = list(self.pid_to_time_map.keys())[-1]
            # end time of last process - start time of first process = effectivat total time
            print(f"Effective total time taken is {round(self.pid_to_time_map[end_time_pid][1] - self.pid_to_time_map[start_time_pid][0], 3)} sec")
    
    def plot_cpu_graph(self) -> None:
        plt.plot(self.cpu_percentages)
        plt.title(f"CPU% Usage over time for process '{self.process_name}'")
        plt.ylabel("CPU %")
        plt.xlabel("Time --->")
        plt.xticks([])
        plt.tight_layout()
        plt.savefig(f"CPU_vs_TIME_{self.process_name}_{time.strftime(ProcMon.date_time_format)}.png")
        plt.cla()
        plt.clf()
    
    def plot_ram_graph(self) -> None:
        plt.plot(self.mem_percentages)
        plt.title(f"RAM% Usage over time for process '{self.process_name}'")
        plt.ylabel("RAM %")
        plt.xlabel("Time --->")
        plt.xticks([])
        plt.tight_layout()
        plt.savefig(f"RAM_vs_TIME_{self.process_name}_{time.strftime(ProcMon.date_time_format)}.png")
        plt.cla()
        plt.clf()

    def print_summary(self) -> None:
        ''' Once the user press ctrl + c this method will show output on the terminal'''
        curr_time = time.strftime("%H:%M:%S", time.localtime())
        print("Current Time is :", curr_time)
        print("*"*15 + f" SUMMARY for '{self.process_name}' process " + "*"*15)
        self.print_pid_with_time()
        if len(self.cpu_percentages) > 0:
            print("*"*10 + " CPU " + "*"*10)
            print(f"Max CPU usage: {max(self.cpu_percentages)}%")
            print(f"Min CPU usage: {min(self.cpu_percentages)}%")
            try:
                print(f"Avg CPU usage: {round(mean(self.cpu_percentages), 2)}%")
                print(f"Median CPU usage: {median(self.cpu_percentages)}%")
                if (median(self.cpu_percentages) == 0):
                    print(f"Non-zero Median CPU usage: {self.get_non_zero_median(self.cpu_percentages)}%")
                print(f"Mode CPU usage: {mode(self.cpu_percentages)}%")
                print(f"P.Std.Dev CPU: {round(pstdev(self.cpu_percentages), 2)}%")
            except:
                print(f"DEBUG: CPU% list is {list(self.cpu_percentages)}")
                pass
        else:
            print(f"No information available for CPU for process {self.process_name}")

        if len(self.mem_percentages) > 0:
            print("*"*10 + " RAM " + "*"*10)
            print(f"Max RAM usage: {max(self.mem_percentages)}% \ti.e. {self.get_acutal_mem_used(max(self.mem_percentages))} MB")
            print(f"Min RAM usage: {min(self.mem_percentages)}% \ti.e. {self.get_acutal_mem_used(min(self.mem_percentages))} MB")
            try:
                print(f"Avg RAM usage: {round(mean(self.mem_percentages), 2)}% \ti.e. {self.get_acutal_mem_used(mean(self.mem_percentages))} MB")
                print(f"Median RAM usage: {median(self.mem_percentages)}% \ti.e. {self.get_acutal_mem_used(median(self.mem_percentages))} MB")
                if (median(self.mem_percentages) == 0):
                    print(f"Non-zero Median RAM usage: {self.get_non_zero_median(self.mem_percentages)}% \ti.e. {self.get_acutal_mem_used(self.get_non_zero_median(self.mem_percentages))} MB")
                print(f"Mode RAM usage: {mode(self.mem_percentages)}% \ti.e. {self.get_acutal_mem_used(mode(self.mem_percentages))} MB")
                print(f"P.Std.Dev RAM: {round(pstdev(self.mem_percentages), 2)}% \ti.e. {self.get_acutal_mem_used(pstdev(self.mem_percentages))} MB")
            except:
                print(f"DEBUG: RAM% list is {list(self.mem_percentages)}")
                pass
        else:
            print(f"No information available for RAM for process {self.process_name}")
        
        print("*"*10 + " SYSTEM INFORMATION " + "*"*10)
        print(f"Machine hostname {socket.gethostname()}")
        print(f"IP Address: {socket.gethostbyname(socket.gethostname())}")
        print(f"Total RAM on the system {self.total_mem_mb} MB i.e. {round(self.total_mem_mb/1024, 2)} GB")
        print(f"CPU count on the system = {self.total_cpu_count}")
        print(f"CPU clock cycles are {self.total_cpu_mhz} MHz i.e. {round(self.total_cpu_mhz/1000, 1)} GHz")

    def start_monitor(self) -> None:
        ''' Infinite loop, till user press the ctrl + c '''
        process_found = True
        while True:
            # Run the top command
            output = subprocess.check_output(
                ['top', '-b', '-n', '1', '-u', self.username], universal_newlines=True)
            #TODO: Remove first 7 lines from output

            cur_cpu = 0
            cur_mem = 0
            pid_list = []
            # Find the line for the process
            for line in output.split('\n'):
                if self.process_name in line:
                    process_found = True
                    # Parse the CPU and memory usage
                    # print(line)
                    fields = line.split()
                    self.map_pid_with_time(fields[0])
                    pid_list.append(fields[0])
                    cpu = float(fields[8])  # CPU usage is the 9th field
                    mem = float(fields[9])  # Memory usage is the 10th field
                    cur_cpu = round(cur_cpu + cpu, 2)
                    cur_mem = round(cur_mem + mem, 2)
                    ''' ideally we should not break but add the cpu and mem % if more than
                        one process is running, this is applicable for client process. '''
                    # break

            if (pid_list):
                print(f"PID: {pid_list}", end=" ")
                if True: # (cur_cpu != 0):
                    print(f"CPU: {cur_cpu}%", end=" ")
                    self.cpu_percentages.append(cur_cpu)
                
                if True: # (cur_mem != 0):
                    print(f"MEM: {cur_mem}%", end=" ")
                    self.mem_percentages.append(cur_mem)
                
                self.timestamps.append(time.time())
                print()
            else:
                if process_found:
                    print(f"Waiting!! Process name {process_name} is not yet found in TOP command output")
                process_found = False
                pass

            time.sleep(ProcMon.sleep_time)  # adjust the sleep time as needed

# Driver code
if __name__ == "__main__":
    
    # Get the process name and username from the command line arguments
    if len(sys.argv) != 3:
        print("Usage: python monitor.py <username used in TOP> <process_name>")
        print("For example for compare/repair processes")
        print("python3 ProcMon.py adeshpande sp_xdesvr")
        print("python3 ProcMon.py adeshpande sp_xdeclt")
        print("try running 'top -u <username>' and check if your username exists")
        sys.exit(1)

    # Collect username and process name that we get from commandline
    username = sys.argv[1]
    process_name = sys.argv[2]

    # Create an object of ProcMon class
    monitor = ProcMon(username, process_name)

    # Get the RAM infomarion from free command
    monitor.get_system_RAM_info()

    # Get the CPU information from lscpu command
    monitor.get_system_CPU_info()
    try:
        # continiously monitor top command output for our process
        monitor.start_monitor()
    except KeyboardInterrupt:
        print('\nMonitoring stopped by user\n')
        # show the detailed summary at the end
        monitor.print_summary()

    # to execute below code you need to have matplotlib installed
    # try running below commands to install it.
    # python3 -m pip install --upgrade pip --user
    # python3 -m pip install --upgrade matplotlib --user
    try:
        import matplotlib.pyplot as plt
        import matplotlib as mpl
        mpl.rcParams['axes.spines.right'] = False
        mpl.rcParams['axes.spines.top'] = False
        mpl.rcParams["figure.figsize"] = [9.6, 4.8] # [6.4, 4.8] is default size
        monitor.plot_cpu_graph()
        monitor.plot_ram_graph()
    except Exception:
        print("Unable to save the graphs")
        print("Try installing latest pip and then matplotlib")
        print("Try running below command")
        print("python3 -m pip install --upgrade pip --user && python3 -m pip install --upgrade matplotlib --user")

#TODO: Save the summary in a file for further analysis
