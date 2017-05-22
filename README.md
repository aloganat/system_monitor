# Description

This script will be used to monitor cpu, memory usage of the
processes and load average of the system in regular intervals of time
and collects the data in an excel sheet for later reference and
draws chart with the system monitor data.

## Python packages to be installed:

Python Packages to be installed:
  - yum install python-setuptools
  - easy_install pip
  - pip install pandas
  - pip install xlsxwriter

## Installing system_monitor directly Git via pip

             pip install --upgrade git+git://github.com/aloganat/system_monitor.git

## Uninstalling system_monitor

             pip uninstall system_monitor

## Usage:
  system_monitor -h

             usage: system monitoring [-h] {system_monitor,draw_chart} ...
             Tool for monitoring system
             optional arguments:
                 -h, --help            show this help message and exit

             Available sub commands:
             {system_monitor,draw_chart}
                        sub-command help
             system_monitor      collects cpu, mem usage and load average of system.
             draw_chart          draws chart with system monitor data.


  system_monitor system_monitor -h

             usage: system monitoring system_monitor [-h] [-p P] [-o O] [-i I]
             optional arguments:
             -h, --help  show this help message and exit

             required named arguments:
             -p P        Process names (default: None)
             -o O        Output file name for collecting data (default: None)
             -i I        Time Interval(in seconds) to take samples (default: None)


  system_monitor draw_chart -h

             usage: system monitoring draw_chart [-h] [--files-to-compare file_names]
                                    [--process_name process_name]
                                    [--field-name field_name]
                                    [--chart-type chart_type] [-o O] [-i I]

             optional arguments:
             -h, --help            show this help message and exit
             --chart-type chart_type
                        Type of chart to plot Chart type can be line or column
                        (default: line)

             required named arguments:
             --files-to-compare file_names
                        Excel files to compare (default: None)
             --process_name process_name
                        Process name to draw chart (default: None)
             --field-name field_name
                        Field name to compare. Field name can be memory, cpu,
                        loadavg1x, loadavg5x, loadavg15x (default: None)
             -o O       Output file name for drawing chart (default: None)
             -i I       Time Interval(in seconds) to take samples (default:
                        None)

## Example:
             system_monitor system_monitor -p "systemd glusterfsd glusterd" -o "/tmp/node_1.xlsx" -i 5
             system_monitor draw_chart --files-to-compare "/tmp/node_1.xlsx /tmp/node_2.xlsx" --process_name "glusterd" --field-name "loadavg1x" -o "/tmp/chart.xlsx" -i 5
## Note: 

With system_monitor option, the data will get collected in excel sheet unitl user terminates the script. If you try to monitor different process in the subsequent runs, then collect the data in new output file. 

## Future Enhancements:

  - Adding error handling if process names are not found in system.
  - Feedbacks are welcome.

