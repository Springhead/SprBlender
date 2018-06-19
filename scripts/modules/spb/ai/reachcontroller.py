# -*- coding: utf-8 -*-

import spb
import time

from collections           import defaultdict
from Spr                   import *
from spb.abbrev            import *
from spb.utils             import *
from random                import *
from math                  import *

class ReachController():
	def __init__(self, leftreach, rightreach, handsreach, perception, config):
		self.leftreach		= leftreach
		self.rightreach		= rightreach
		self.handsreach		= handsreach
		self.perception		= perception
		self.config			= config

		self.curr_grab_target = None
		
	def set_reach_target(self, target,touch_pos = Vec3d(0,0,0)):
		self.reach_target	= target
		self.touch_pos		= touch_pos
			
	def step(self, leftcnt, rightcnt):
		targ_pos	= self.reach_target
		#targ_pos	= self.reach_target.GetPose().transform(self.touch_pos)
		#bpy.data.objects['Empty'].location = to_bpy(targ_pos)
		if leftcnt == 1:
			self.handsreach.spr().Enable(False)
			self.rightreach.Enable(False)
			self.rightreach.GetIKEndEffector().EnablePositionControl(False)
			self.leftreach.Enable(True)
			self.leftreach.SetFinalPos(targ_pos)
			
		if rightcnt == 1:
			self.handsreach.spr().Enable(False)
			self.leftreach.Enable(False)
			self.leftreach.GetIKEndEffector().EnablePositionControl(False)
			self.rightreach.Enable(True)
			self.rightreach.SetFinalPos(targ_pos)
			
		if leftcnt == 0 and rightcnt == 0:
			self.leftreach.GetIKEndEffector().EnablePositionControl(True)
			self.rightreach.GetIKEndEffector().EnablePositionControl(True)
			self.handsreach.spr().Enable(True)
			self.leftreach.Enable(False)
			self.rightreach.Enable(False)
			

