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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="system monitoring",
                                     description=("collects cpu,mem usage "
                                                  "and load average of system"))
    parser.add_argument('-p', help="Process names", required=True)
    parser.add_argument('-o', help="Output file name for collecting data", required=True)
    parser.add_argument('-i', help="Time Interval(in seconds) to take samples", required=True)

    args = parser.parse_args()   
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

