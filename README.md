# Description

This script will be used to monitor cpu, memory usage of the
processes and load average of the system in regular intervals of time
and collects the data in an excel sheet for later reference.

## How to Run the script:

Python Packages to be installed:
  - yum install python-setuptools
  - easy_install pip
  - pip install xlwt
  - pip install xlrd
  - pip install xlutils

             python system_monitor.py -p "systemd glusterfsd glusterd" -o "/tmp/monitor.xlsx"

## Usage:
  python system_monitor.py --help
  
             usage: system monitoring [-h] -p P -o O -i I
             collects cpu,mem usage and load average of system
             optional arguments:
             -h, --help  show this help message and exit
             -p P        Process names
             -o O        Output file name for collecting data
             -i I        Time Interval(in seconds) to take samples

The script will get executed and collects data until the user termintaes it.

##Note: 

The data will get collected in excel sheet unitl user terminates the script. If you try to monitor different process in the subsequent runs, then collect the data in new output file. 
