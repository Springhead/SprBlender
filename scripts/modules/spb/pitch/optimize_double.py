#!/usr/bin/env python
# encoding: utf-8

import subprocess
import threading
import spb
import bpy
import os
#import numpy as np
#import matplotlib.pyplot as plt

class Thread_optimize(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
	
	def run(self):
		bnlen = len(bpy.path.basename(bpy.data.filepath))
		dir = bpy.data.filepath[0:-bnlen]
		os.chdir(dir)

		MathKernel_path = '"C:\\Program Files\\Wolfram Research\\Mathematica\\10.0\\math.exe"'
		file_path		= '"'+(spb.__path__[0])+'\\pitch\\interaction\\opt_double.m"'
		
		cmd =  "%s -script %s" % (MathKernel_path,file_path)
		# subprocess.call(cmd, shell=True)
		
		#update
		spb.handlers.scene_handler.rule.update()
		spb.handlers.scene_handler.rule.init()
		#start
		if len(threading.enumerate()) < 3:
			bpy.context.scene.spr_step_enabled = 1
		