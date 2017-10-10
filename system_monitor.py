import csv
import shlex
import os
import sys
import re
import subprocess
import time
import logging
from xlwt import Workbook
from xlrd import *
from xlutils import *
from xlutils.copy import copy
import argparse
import pandas as pd
import random
import numpy as np

GLOBAL_DATA_TO_MONITOR = ['load average:']
def run_top_command(processes):
    '''
    Fn to run the top command and return the result of top command only for the given processes.
    Returns result of top command if successful
    Else returns None
    '''
    try:
        proc =  processes
        proc.insert(0, "pidof")
        _cmd = proc
        output = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res=output.stdout.read().strip("\n")
        if res is None:
            return None
        res = res.replace(" ",",")
        _cmd=['top','-b','-n', '2', '-p', res]
        output = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res=output.stdout.read().strip("/n")
        if res is None:
            return None
        samples = re.sub('top - ','splitstrtop - ',res).split('splitstr')
        if(len(samples) > 1):
            samples = samples[1:]
            output =  re.sub('\n','\nsplitstr',samples[1]).split('splitstr')[:-1]
            return samples[1].split('\n')[:-1]
        return None
    except:
        print "Exception occured in run_top_command()"
        return None

def parseGlobalData(output):
    '''
    Fn to parse global data from top output.
    '''
    try:
        globalInfo=[]
        globalData={}
        for i in output:
            data = []
            for x in GLOBAL_DATA_TO_MONITOR:
                if re.search(x,i):
                    m = re.search('.*'+ '(' + x +'.*)', i)
                    data.append(m.group(1))
            if data != []:
                globalInfo.append(data[0])
        for _info in globalInfo:
            globalData[GLOBAL_DATA_TO_MONITOR[globalInfo.index(_info)]]=re.sub(GLOBAL_DATA_TO_MONITOR[globalInfo.index(_info)],'',_info)
        return globalData
    except:
        print "Exception occured in parseGlobalData()"
        return None

def getLoadAvg(loadAvgVal):
    '''
    Fn to get load average from loadAverage values passed.
    Returns dict with loadaverage data
    '''
    _loadAvgHdr=['LOADAVG1X','LOADAVG5X','LOADAVG15X']
    _loadAvgData=dict(zip(_loadAvgHdr,[float(x) for x in shlex.split(loadAvgVal.replace(',',''))]))
    return _loadAvgData

def getGlobalData(output):
    """
    This method retrieves the global metrics
    On success, returns metrics
    On failure, returns None
    """
    try:
        globalData=parseGlobalData(output)
        if globalData is None:
            return None
        globalStatDict={}
        metricsList = [getLoadAvg(globalData['load average:'])]

        for _result in metricsList:
            if _result != {}:
                globalStatDict.update(_result)
        return globalStatDict
    except:
        return None

def parse_top_output(output,book,proclist):
    '''
    Fn to parse top output and copy the data to CSV.
    '''
    try:
        allProcInfo=[]
        load_avg = getGlobalData(output)
        #output = [re.sub("(.*\s)\S+", "\\1" + proclist[-1], w) for w in output if w.endswith("+")]
        for i in reversed(output):
            procInfo=[shlex.split(re.sub('[\+\-]','',i)) for x in proclist if x in i]
            for p in procInfo:
                output = subprocess.Popen("date", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                res=output.stdout.read().strip("\n")
                p.insert(0,str(res))
            if procInfo != [] and len(procInfo[0]) != 1:
                procInfo[0] = procInfo[0] + [load_avg['LOADAVG1X'],load_avg['LOADAVG5X'], load_avg['LOADAVG15X']]
                _curSheet=book.get_sheet(book._Workbook__worksheet_idx_from_name[unicode(procInfo[0][12].lower())])
                _rowNum=max(_curSheet.get_rows().keys())+1
                _colNum=0
                for item in procInfo[0]:
                    _curSheet.write(_rowNum,_colNum,item)
                    _colNum=_colNum+1
                _rowNum=_rowNum+1
    except:
        return False
    return True

def system_monitor(args):
    proc_to_monitor = args.p.split()
    filename = args.o
    interval = args.i

    if os.path.exists(filename):
            #Read existing workbook to append the data.
            readBook=open_workbook(filename)
            book=copy(readBook)
    else:
        book=Workbook()
        proc_header = ["TIME","PID","USER","PR","NI","VIRT","RES","SHR","S","%CPU", "%MEM","TIME+","COMMAND", "LOADAVG1X", "LOADAVG5X", "LOADAVG15X" ]
        for proc in proc_to_monitor:
            sheet=book.add_sheet(proc)
            for _header in proc_header:
                sheet.row(0).write(proc_header.index(_header),_header)

    while(True):
        output =  run_top_command(proc_to_monitor)
        if not parse_top_output(output, book, proc_to_monitor):
            print "Incorrect Parser Output"
        book.save(filename)
        print "Waiting for ",interval," seconds to take samples"
        time.sleep(int(interval))

def draw_chart(args):
    """
    Draws chart with system monitor data
    """
    files = args.file_names.split()
    output_file = args.o
    sheet_name = args.process_name
    stat_to_compare = args.field_name
    interval = args.i
    chart_type = args.chart_type
    stats_map = {'memory' : '%MEM',
                 'cpu' : '%CPU',
                 'loadavg1x' : 'LOADAVG1X',
                 'loadavg5x' : 'LOADAVG5X',
                 'loadavg15x' : 'LOADAVG15X',
                }
    values_list = []
    for file in files:
        df = pd.read_excel(file, sheetname=sheet_name)
        values = df[stats_map[stat_to_compare]].values
        values = np.array(values).tolist()
        values_list.append(values)
        FORMAT = stats_map[stat_to_compare]
        df_selected = df[FORMAT]
        print df_selected

    # Create some sample data to plot.
    b = [len(x) for x in values_list]
    v = b.index(min(b))

    max_row     = len(values_list[v])
    va = []
    for val in values_list:
        va.append(val[:max_row])
    categories = []
    for file in files:
        categories.append(os.path.splitext(os.path.basename(file))[0])
    index_1 = [i for i in range(0,max_row*int(interval),int(interval)) if True]
    multi_iter1 = {'index': index_1}

    for index,category in enumerate(categories):
        multi_iter1[category] = va[index]

    index_2 = multi_iter1.pop('index')
    df      = pd.DataFrame(multi_iter1, index=index_2)
    df      = df.reindex(columns=sorted(df.columns))

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer     = pd.ExcelWriter(output_file, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name)

    # Access the XlsxWriter workbook and worksheet objects from the dataframe.
    workbook  = writer.book
    worksheet = writer.sheets[sheet_name]

    # Create a chart object.
    chart = workbook.add_chart({'type': chart_type})

    # Configure the series of the chart from the dataframe data.
    for i in range(len(categories)):
        col = i + 1
        chart.add_series({
            'name':       [sheet_name, 0, col],
            'categories': [sheet_name, 1, 0,   max_row, 0],
            'values':     [sheet_name, 1, col, max_row, col],
            'data_labels': {'value': True},
        })

    # Configure the chart axes.
    if ((stats_map[stat_to_compare] == 'LOADAVG1X') or
        (stats_map[stat_to_compare] == 'LOADAVG5X') or
        (stats_map[stat_to_compare] == 'LOADAVG15X')):
        chart.set_title({'name': 'system_' + stats_map[stat_to_compare]})
    else:
        chart.set_title({'name': sheet_name +'_' + stats_map[stat_to_compare]})
    chart.set_x_axis({'name': 'Time Interval(in seconds)'})
    chart.set_y_axis({'name': stat_to_compare, 'major_gridlines': {'visible': False}})
    chart.set_size({'width': 1000, 'height': 650})
    # Insert the chart into the worksheet.
    worksheet.insert_chart('G2', chart)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

def main():
    parser = argparse.ArgumentParser(prog="system monitoring",
                                     description=("Tool for monitoring system"))

    subparsers = parser.add_subparsers(title='Available sub commands',
                                       help='sub-command help')

    monitor_parser = subparsers.add_parser(
        'system_monitor',
        help=("collects cpu, mem usage and load average of system."),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    monitor_required_parser = monitor_parser.add_argument_group(
                                                    'required named arguments')
    monitor_required_parser.add_argument('-p', help="Process names")
    monitor_required_parser.add_argument('-o', help="Output file name for collecting data")
    monitor_required_parser.add_argument('-i', help="Time Interval(in seconds) to take samples")

    monitor_parser.set_defaults(func=system_monitor)

    draw_chart_parser = subparsers.add_parser(
        'draw_chart',
        help=("draws chart with system monitor data."),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    chart_required_parser = draw_chart_parser.add_argument_group(
                                                    'required named arguments')

    chart_required_parser.add_argument('--files-to-compare', help="Excel files to compare",
                                       metavar=('file_names'), dest='file_names', type=str)
    chart_required_parser.add_argument('--process_name', help="Process name to draw chart",
                                       metavar=('process_name'), dest='process_name', type=str)
    chart_required_parser.add_argument('--field-name', help="Field name to compare. "
                                       "Field name can be memory, cpu, loadavg1x, "
                                       "loadavg5x, loadavg15x",
                                       metavar=('field_name'), dest='field_name', type=str)
    draw_chart_parser.add_argument('--chart-type', help="Type of chart to plot "
                                       "Chart type can be line or column",
                                       metavar=('chart_type'), dest='chart_type', type=str,
                                       default='line')
    chart_required_parser.add_argument('-o', help="Output file name for drawing chart")
    chart_required_parser.add_argument('-i', help="Time Interval(in seconds) to take samples")

    draw_chart_parser.set_defaults(func=draw_chart)

    args = parser.parse_args()
    args.func(args)
    sys.exit(0)

if __name__ == "__main__":
    main()
