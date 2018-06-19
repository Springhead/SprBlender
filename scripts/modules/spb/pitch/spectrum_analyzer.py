#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import atexit
import math
import numpy as np
import threading
import wave
import shutil
import struct
from datetime import *
from time     import sleep
from time     import time
import spb
import bpy

bnlen = len(bpy.path.basename(bpy.data.filepath))
dir = bpy.data.filepath[0:-bnlen]

ver = "%d%d" % (sys.version_info.major, sys.version_info.minor)
sys.path.append("C:\\Python"+ver+"\\Lib\\site-packages")

import pyaudio

class Thread_record(threading.Thread):

	def __init__(self,volume):
		threading.Thread.__init__(self)
		self.spe = Spectrum(volume)
		file = open(dir+"pitch.txt","w")
		file.write("")
		file.close()
		test = open(dir+"vol.txt","w")
		test.write("")
		test.close()
		spb.voice_volume_data     = []
		spb.voice_volume_data_avg = []

		
	def run(self):
		print("====== recording start ======")
		self.spe.record()
		print("====== recording done ======")
		opt = spb.pitch.optimize_double.Thread_optimize()
		opt.start()
		


class Spectrum(object):
	
	#initialize
	FORMAT = pyaudio.paFloat32
	CHANNELS = 1
	RATE = 44100


	def __init__(self,volume_level):
		self.volume = volume_level
		self.pa = pyaudio.PyAudio()
		self.last_samples = None
		atexit.register(self.pa.terminate)
		self.cnt = 0
		self.smooth_pastdata = None
		self.Thre_pastdata	 = None
		self.DATETIME = datetime.utcnow() + timedelta(hours=9)
		copy = open(dir+self.DATETIME.strftime("%Y_%m_%d_%H_%M_%S")+".txt","w")
		copy.write("")
		copy.close()
		
		
		
	def is_peak(self, a, index):
		if index == 0:
			if a[index] > a[index+1]:
				return True
			else:
				return False
		elif index == len(a)-1:
			if a[index] > a[index-1]:
				return True
			else:
				return False
		else:
			if (a[index-1] < a[index] and a[index] > a[index+1]):
				return True
			else:
				return False

	def autocorrelation(self,samples):
		autocorr	= np.correlate(samples,samples,"full")
		autocorr	= autocorr[len(autocorr) / 2 : ]
		peakindices = [i for i in range(len(autocorr)) if self.is_peak(autocorr,i)]
		peakindices = [i for i in peakindices if i != 0]
		if not len(peakindices) == 0:
			peakindex = max(peakindices, key = lambda index: autocorr[index])
			quefrency = 1/self.RATE * peakindex
			f0 = 1 / quefrency
			vol= autocorr[peakindex]
		else:
			f0 = 4000
			vol= 0
		return [f0,vol]
		
	def RMS(self, samples):
		return math.sqrt(np.dot(samples,samples) / len(samples))
		
			
		return math.sqrt( sum_squares / count )
		
	def smoothing(self,currentdata):
		if self.smooth_pastdata == None:
			self.smooth_pastdata = currentdata
		smooth = (0.5 * self.smooth_pastdata + 0.5 * currentdata)
		self.smooth_pastdata = smooth
		return smooth
		
	def Thre(self,currentdata):
		thre = None
		if self.Thre_pastdata == None:
			self.Thre_pastdata = currentdata
			thre = False
		else:
			if math.fabs(self.Thre_pastdata - currentdata) < 40:
				thre = True
				self.Thre_pastdata = currentdata
			else:
				thre = False
		return thre
	
	def callback(self, in_data, frame_count, time_info, status):
		data = np.fromstring(in_data, np.float32)
		#基本周波数
		d  = self.autocorrelation(data)[1]
		d2 = math.log(d+1)**2
		spb.voice_volume_data.append(d)
		if len(spb.voice_volume_data_avg)==0:
			spb.voice_volume_data_avg.append(0.5*d2)
		else:
			spb.voice_volume_data_avg.append(0.5*spb.voice_volume_data_avg[-1] + 0.5*d2)
		print(20 * np.log10(self.RMS(data)))
		if (20 * np.log10(self.RMS(data))) > float(self.volume):
			test1 = open(dir+"vol.txt","a")
			#test1.write(str(self.autocorrelation(data)[1])+"\n")
			test1.write(str(self.smoothing(self.autocorrelation(data)[1]))+"\n")
			test1.close()
			file = open(dir+"pitch.txt","a")
			if self.cnt > 2: 
				if self.autocorrelation(data)[0] < 400:
					if self.Thre(self.autocorrelation(data)[0]):
						file.write(str(self.autocorrelation(data)[0]) + "\n")
						file.close()
			else:
				self.cnt += 1
			file.close()
		return (in_data, self.recording)
 
	def record(self):
		self.recording = pyaudio.paContinue
		stream = self.pa.open(format = self.FORMAT,
						channels = self.CHANNELS,
						rate = self.RATE,
						input = True,
						output = False,
						#frames_per_buffer = self.FRAME_LEN,
						frames_per_buffer = 1024,
						stream_callback = self.callback)
		stream.start_stream()
		start_time = time()
		while stream.is_active():
			sleep(5)
			if(3 <= (time() - start_time)):
				stream.stop_stream()
				
		if(stream.is_stopped()):
			src =open(dir+"pitch.txt","r")
			copy = open(dir+self.DATETIME.strftime("%Y_%m_%d_%H_%M_%S")+".txt","w")
			shutil.copyfileobj(src,copy)
			src.close()
			copy.close()
			
		stream.close()
		
