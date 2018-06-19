# -*- coding: utf-8 -*-

import spb
import time

from   collections  import defaultdict
from   spb.utils    import *
from   spb.abbrev   import *
from   Spr          import *
from   math         import *


class EatController():
	def __init__(self, headlook, headreach, perception, config):
		self.config     = config

		self.headlook   = headlook
		self.headreach  = headreach
		self.perception = perception

		self.target_cands = []
		self.curr_target  = None

		self.control_mode = "Look"

		self.last_touched = False
		self.last_touch_time = time.time()
		self.touching_time = 0

		self.mouth_open = 0

		self.wait_start_time = time.time()

	def add_eat_target(self, target):
		if not target in self.target_cands and not target is None:
			self.target_cands.append(target)

		n = self.config['max_eat_candidates']
		if len(self.target_cands) > n:
			self.target_cands = self.target_cands[-n:]

	def step(self):
		self.mouth_open = max(0, self.mouth_open - 0.1)

		head_ike_hnd = spb.handlers.ikeff_handlers[ self.headreach.bpy().target ]

		mouth_pos = to_spr(bpy_object_pose(bpy.data.objects[self.config['head_ik_tips']['Eat']]).translation)
		distances = sorted([((mouth_pos - targ.GetPose().getPos()).norm(), targ) for targ in self.target_cands])

		# print([(d[0], d[1].GetName()) for d in distances])

		if   self.control_mode == "Look":
			if len(distances) > 0 and distances[0][0] < self.config['eat_start_distance']:
				self.control_mode = "Reach"

				self.curr_target = distances[0][1]
				self.touching_time = 0
				self.change_ik_tip("Eat", self.curr_target.GetPose().getPos())


		elif self.control_mode == "Reach":
			self.headreach.spr().SetFinalPos(self.curr_target.GetPose().getPos())

			# 接触判定
			head_solid = self.headreach.spr().GetIKEndEffector().GetSolid()
			targ_solid = self.curr_target
			if ( (targ_solid in self.perception.info)
			and  (self.perception.info[targ_solid].touching)
			and  (head_solid in self.perception.info[targ_solid].list) ):
				now = time.time()
				if self.last_touched:
					self.touching_time += (now - self.last_touch_time)
				self.last_touch_time = now
				self.last_touched = True
			else:
				self.last_touched = False

			eat_complete = (self.touching_time > self.config['eat_complete_time'])
			distance     = (mouth_pos - self.curr_target.GetPose().getPos()).norm()

			# 口開ける度（距離依存）
			start_open = self.config['eat_mouth_start_open']
			compl_open = self.config['eat_mouth_compl_open']
			self.mouth_open = max(0, min((distance-start_open)/(compl_open - start_open), 1))

			if (distance > self.config['eat_resign_distance']):
				self.control_mode = "Look"
				self.change_ik_tip("Look")

			if (eat_complete):
				self.control_mode = "Eat"
				self.target_cands.remove(self.curr_target)


		elif self.control_mode == "Eat":
			self.mouth_open -= 0.2
			if self.mouth_open < 0.1:
				self.control_mode = "Wait"
				self.wait_start_time = time.time()
				self.change_ik_tip("Look")


		elif self.control_mode == "Wait":
			if time.time() - self.wait_start_time > self.config['wait_after_eat']:
				self.control_mode = "Look"



	def change_ik_tip(self, type_tip, targ_pos=None):
		look_tip_name  = self.config['head_ik_tips']['Look']
		mouth_tip_name = self.config['head_ik_tips']['Eat']
		head_ike_hnd   = spb.handlers.ikeff_handlers[ self.headreach.bpy().target ]
		if type_tip == "Look":
			head_ike_hnd.bpy().spr_ik_tip_object_name = look_tip_name
			head_ike_hnd.targetlocalpos_sync.sync_bpy_to_spr()
			head_ike_hnd.targetlocaldir_sync.sync_bpy_to_spr()
			self.headreach.spr().Enable(False)
			self.headreach.spr().GetIKEndEffector().EnablePositionControl(False)
			self.headlook.spr().Reset()

		elif type_tip == "Eat":
			head_ike_hnd.bpy().spr_ik_tip_object_name = mouth_tip_name
			head_ike_hnd.targetlocalpos_sync.sync_bpy_to_spr()
			head_ike_hnd.targetlocaldir_sync.sync_bpy_to_spr()
			self.headlook.spr().Reset()
			self.headreach.spr().GetIKEndEffector().EnablePositionControl(True)
			self.headreach.spr().Enable(True)
			self.headreach.spr().SetFinalPos(targ_pos)
			self.headreach.spr().Reset()
