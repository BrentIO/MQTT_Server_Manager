#!/usr/bin/env python3

import psutil
import platform
from datetime import datetime


def execute(payload):

  #Payload ignored

  returnValue = {}

  #Retrieve the data about the system
  returnValue['operatingSystem'] = platform.system()
  returnValue['version'] = platform.release()
  returnValue['name'] = platform.node()
  returnValue['architecture'] = platform.machine()
  returnValue['processorCores'] = psutil.cpu_count()
  returnValue['processorUtilization'] = psutil.cpu_percent()
  returnValue['memoryUtilization'] = psutil.virtual_memory()[2]
  returnValue['diskUtilization'] = psutil.disk_usage('/')[3]
  returnValue['bootTime'] = datetime.fromtimestamp(psutil.boot_time()).isoformat()

  returnValue['disks'] = []

  #Cycle through each partitiion
  for diskPartition in psutil.disk_partitions():

    tmpDisk = {}

    #Convert the tuple to a dictionary
    tmpPartition = diskPartition._asdict()
   
    #Buld the response object
    tmpDisk['mountPoint'] = tmpPartition['mountpoint']
    tmpDiskUsage = psutil.disk_usage(tmpDisk['mountPoint'])._asdict()
    tmpDisk['total'] = humanbytes(tmpDiskUsage['total'])
    tmpDisk['total_bytes'] = tmpDiskUsage['total']
    tmpDisk['used'] = humanbytes(tmpDiskUsage['used'])
    tmpDisk['used_bytes'] = tmpDiskUsage['used']
    tmpDisk['used_percent'] = tmpDiskUsage['percent']
    tmpDisk['free'] = humanbytes(tmpDiskUsage['free'])
    tmpDisk['free_bytes'] = tmpDiskUsage['free']

    returnValue['disks'].append(tmpDisk)

  return returnValue


def humanbytes(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)