#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import sys
import time
import signal
import string
import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
from queue import Queue
import re

i = 0
q_mag_x = Queue(maxsize=0)
q_mag_y = Queue(maxsize=0)
q_mag_z = Queue(maxsize=0)
curve_num = 0;

def Serial():
    global i;
    global q_mag_x;
    global q_mag_y;
    global q_mag_z;
    ret = b''
    while(True):
        n = mSerial.inWaiting()
        if(n):
            ret = mSerial.readline()
            #print(ret)
            if len(ret):
                data_get = ret.decode('utf-8', 'ignore')
                pattern_line = re.compile(r'^energys:.*$')
                data_line = pattern_line.findall(data_get)
                #print(data_line)
                pattern = re.compile(r"[+-]?\d+(?:\.\d+)?") # find the num
                data_all = []
                if len(data_line):
                    data_all = pattern.findall(data_line[0])
                if len(data_all):
                    print(data_all)
                for j in range(len(data_all)):
                    if j==0:
                        q_mag_x.put(float(data_all[j]))
                    if j==1:
                        q_mag_y.put(float(data_all[j]))
                    if j==2:
                        q_mag_z.put(float(data_all[j]))

def plotData():
    global i;
    if i < historyLength:
        data_x[i] = q_mag_x.get()
        if curve_num >= 2:
            data_y[i] = q_mag_y.get()
        if curve_num >= 3:
            data_z[i] = q_mag_z.get()
        i = i + 1
    else:
        data_x[:-1] = data_x[1:]
        data_x[i-1] = q_mag_x.get()
        if curve_num >= 2:
            data_y[:-1] = data_y[1:]
            data_y[i-1] = q_mag_y.get()
        if curve_num >= 3:
            data_z[:-1] = data_z[1:]
            data_z[i-1] = q_mag_z.get()
    curve1.setData(data_x)
    curve2.setData(data_y)
    curve3.setData(data_z)

def sig_handler(signum, frame):
    print("catched signal: %d" % signum)
    mSerial.close()
    sys.exit()

if __name__ == '__main__':
    curve_num = 3

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    app = pg.mkQApp()
    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle(u'pyqtgraph chart tool')
    win.resize(1200, 800)
    data_x = array.array('i')
    data_y = array.array('i')
    data_z = array.array('i')
    historyLength = 320

    data_x = np.zeros(historyLength).__array__('d')
    data_y = np.zeros(historyLength).__array__('d')
    data_z = np.zeros(historyLength).__array__('d')
    p = win.addPlot()
    p.showGrid(x=True, y=True)
    p.setRange(xRange=[0, historyLength], yRange=[-100, 20000], padding=0)
    p.setLabel(axis='left', text='y-mag')
    p.setLabel(axis='bottom', text='x-time')
    p.setTitle('Serial Chart')
    curve1 = p.plot(data_x, pen='r')
    curve2 = p.plot(data_y, pen='g')
    curve3 = p.plot(data_z, pen='b')

    portx = '/dev/tty.usbserial-14103'
    bps = 3000000
    mSerial = serial.Serial(portx, int(bps), timeout=1, parity=serial.PARITY_NONE)
    if (mSerial.isOpen()):
        print("open success")
        mSerial.flushInput()
    else:
        print("open failed")
        serial.close()
        sys.exit()

    #serial data receive thread
    th1 = threading.Thread(target=Serial)
    th1.setDaemon(True)
    th1.start()

    #plot timer define
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(plotData)
    timer.start(10)
    app.exec()
