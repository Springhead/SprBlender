# -*- coding: utf-8 -*-

import spb
import time

from collections           import defaultdict
from Spr                   import *
from spb.abbrev            import *
from spb.utils             import *
from random                import *
from math                  import *
from spb.ai.ai_utils       import *

class GrabController():
	def __init__(self, leftgrab, rightgrab, handsreach, perception, config):
		self.leftgrab		= leftgrab
		self.rightgrab		= rightgrab
		self.handsreach		= handsreach
		self.perception		= perception
		self.config			= config
		
		self.lefthand_ike_hnd	= IKe[self.config['hands_name']['L']]
		self.righthand_ike_hnd	= IKe[self.config['hands_name']['R']]
		
		self.curr_grab_target = None
		
		self.last_lefttouched = False
		self.last_righttouched = False
		
		self.leftcnt = 0
		self.rightcnt = 0
		
		self.cnt = 0

	def set_grab_target(self, target):
		self.curr_grab_target = target
			
	def step(self):
		if not self.curr_grab_target is None:
			# 接触判定
			lefthand_solid = self.leftgrab.GetSolid()
			righthand_solid = self.rightgrab.GetSolid()
			targ_solid = self.curr_grab_target
			# lefthand
			if ( (targ_solid in self.perception.info)
			and  (self.perception.info[targ_solid].touching)
			and  (lefthand_solid in self.perception.info[targ_solid].list) ):
				self.last_lefttouched = True
				# 位置判定
				#if "Debug2" in bpy.data.objects:
				#	bpy.data.objects["Debug2"].location = to_bpy(self.perception.info[targ_solid].touch_pos.curr_var)
				inner_leftarea = point_in('area_lefthand', self.perception.info[targ_solid].touch_pos.curr_var)
				#bpy.data.objects['Empty'].location = to_bpy(self.perception.info[targ_solid].touch_pos.curr_var)
				#print("point_inner_area",inner_leftarea)
			else:
				self.last_lefttouched = False
			# righthand
			if ( (targ_solid in self.perception.info)
			and  (self.perception.info[targ_solid].touching)
			and  (righthand_solid in self.perception.info[targ_solid].list) ):
				self.last_righttouched = True
				# 位置判定
				inner_rightarea = point_in('area_righthand', self.perception.info[targ_solid].touch_pos.curr_var)
			else:
				self.last_righttouched = False

			# grab開始
			if self.last_lefttouched and self.leftcnt == 0 and inner_leftarea:
				self.leftgrab.SetTargetSolid(targ_solid)
				self.change_ik_tip("L")
				#print("leftgrab!!!!!!!!!")
				self.leftcnt = 1
			
			if self.last_righttouched and self.rightcnt == 0 and inner_rightarea:
				self.rightgrab.SetTargetSolid(targ_solid)
				self.change_ik_tip("R")
				#print("rightgrab!!!!!!!!!")
				self.rightcnt = 1
			
			if (self.leftcnt is 1
			and not self.last_lefttouched
			and self.leftgrab.GetGrabbingSolid() is None):
				bpy.data.objects[self.config['hands_name']['L']].spr_ik_tip_use_obj = True
				self.lefthand_ike_hnd.targetlocalpos_sync.sync_bpy_to_spr()
				self.handsreach.spr().Reset()
				#print("miss grabbing!!!!!!!!!!!!!")
				self.leftcnt = 0

			if (self.rightcnt is 1
			and not self.last_righttouched
			and self.rightgrab.GetGrabbingSolid() is None):
				bpy.data.objects[self.config['hands_name']['R']].spr_ik_tip_use_obj = True
				self.righthand_ike_hnd.targetlocalpos_sync.sync_bpy_to_spr()
				self.handsreach.spr().Reset()
				self.rightcnt = 0
		
		else:
			self.leftcnt = 0
			self.rightcnt = 0

		return self.leftcnt, self.rightcnt

	def change_ik_tip(self, type_tip):
		lefthand_tip_name	= self.config['hands_ik_tips']['L']
		righthand_tip_name	= self.config['hands_ik_tips']['R']
		if type_tip == "L":
			bpy.data.objects[self.config['hands_name']['L']].spr_ik_tip_use_obj = False
			local_pos = self.lefthand_ike_hnd.spr().GetSolid().GetPose().Inv().transform(self.leftgrab.GetGrabbingSolid().GetPose().getPos())
			bpy.data.objects[self.config['hands_name']['L']].spr_ik_target_local_pos_x = local_pos.x
			bpy.data.objects[self.config['hands_name']['L']].spr_ik_target_local_pos_y = local_pos.y
			bpy.data.objects[self.config['hands_name']['L']].spr_ik_target_local_pos_z = local_pos.z
			self.lefthand_ike_hnd.targetlocalpos_sync.sync_bpy_to_spr()
			self.handsreach.spr().Reset()
			
		elif type_tip == "R":
			bpy.data.objects[self.config['hands_name']['R']].spr_ik_tip_use_obj = False
			local_pos = self.righthand_ike_hnd.spr().GetSolid().GetPose().Inv().transform(self.rightgrab.GetGrabbingSolid().GetPose().getPos())
			bpy.data.objects[self.config['hands_name']['R']].spr_ik_target_local_pos_x = local_pos.x
			bpy.data.objects[self.config['hands_name']['R']].spr_ik_target_local_pos_y = local_pos.y
			bpy.data.objects[self.config['hands_name']['R']].spr_ik_target_local_pos_z = local_pos.z
			self.righthand_ike_hnd.targetlocalpos_sync.sync_bpy_to_spr()
			self.handsreach.spr().Reset()
			

