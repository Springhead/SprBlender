# -*- coding: utf-8 -*-

import spb

from   collections  import defaultdict
from   spb.utils    import *
from   spb.abbrev   import *
from   Spr          import *
from   math         import *


class FootStepController():
	def __init__(self, so_base, so_leftfoot, so_rightfoot, config):
		self.config         = config

		self.so_base        = so_base
		self.so_leftfoot    = so_leftfoot
		self.so_rightfoot   = so_rightfoot

		# Params

		self.foot_distance  = self.config['foot_distance']
		self.foot_height    = self.config['foot_height']
		self.foot_up_height = self.config['foot_up_height']
		self.max_pace       = self.config['max_pace']

		# States

		self.state          = "Stand"

		self.last_pos       = Vec2d()
		self.diff_lpf       = Vec2d()

		self.stand_pos      = Vec2d()
		self.left_pos       = self.so_base.GetPose().getOri() * Vec3d(+self.foot_distance*0.5,0,self.foot_height)
		self.right_pos      = self.so_base.GetPose().getOri() * Vec3d(-self.foot_distance*0.5,0,self.foot_height)

		self.free_foot      = "Left"
		self.last_ch_pos    = 0
		self.pace           = self.max_pace
		self.last_pace       = self.pace

		self.left_start     = self.left_pos
		self.right_start    = self.right_pos
		self.left_end       = self.left_pos
		self.right_end      = self.right_pos

		self.last_count     = Scn.spr().GetCount()

		# Init

		self.so_leftfoot.SetDynamical(False)
		self.so_rightfoot.SetDynamical(False)

		# Flags
		self.b_enabled = True

		# fix_posuture
		self.fix_timer = 0
		self.fix_state = "STEP0"

		# ezoe
		self.walk_x = 0
		self.transition_timer = 0


	def enable(self, b_enable):
		if b_enable :
			if not self.b_enabled:
				self.so_leftfoot.SetDynamical(False)
				self.so_rightfoot.SetDynamical(False)
				self.b_enable = True
		else :
			self.so_leftfoot.SetDynamical(True)
			self.so_rightfoot.SetDynamical(True)
			self.b_enabled = False


	def step(self, pos):
		if not self.b_enabled:
			return


		count = Scn.spr().GetCount()
		diff_count = count - self.last_count
		self.last_count = count

		if diff_count < 0:
			return

		dt = diff_count * Scn.spr().GetTimeStep()

		# -----

		diff = (to_2d(pos) - self.last_pos)
		self.last_pos = to_2d(pos)
		alpha = self.config['low_pass_filter_alpha']
		self.diff_lpf = self.diff_lpf*(1-alpha) + diff*alpha

		self.so_leftfoot.SetVelocity(Vec3d())
		self.so_leftfoot.SetAngularVelocity(Vec3d())
		self.so_rightfoot.SetVelocity(Vec3d())
		self.so_rightfoot.SetAngularVelocity(Vec3d())

		self.velocity_lpf = self.diff_lpf * (1/dt)

		# -----

		base_ori  = self.so_base.GetPose().getOri()

		if   self.state == "Stand":
			# 足を降ろす
			if self.left_pos.z > self.foot_height:
				self.left_pos.z -= 0.05
			if self.right_pos.z > self.foot_height:
				self.right_pos.z -= 0.05

			# Transition
			if (self.stand_pos - to_2d(pos)).norm() > self.config['walk_transition_threshold']:
				self.state = "Walk"
				self.left_start = self.left_pos
				self.right_start = self.right_pos
				self.last_ch_pos = to_2d(pos)

		elif self.state == "Walk":
			# 歩幅
			pace_coefficient = self.config['pace_coefficient']
			self.pace = min(self.velocity_lpf.norm() * pace_coefficient, self.max_pace)

			# 方向
			direction = self.velocity_lpf.unit()

			# 足を切り替える
			distance = (to_2d(pos) - self.last_ch_pos).norm()

			if distance > self.last_pace:
				self.last_pase = self.pace
				if self.free_foot=="Left":
					self.free_foot = "Right"
					self.right_start = self.right_pos
					#print("Right")
				else:
					self.free_foot = "Left"
					self.left_start = self.left_pos
					#print("Left")
				self.last_ch_pos = to_2d(pos)

			# <!!>
			distance = (to_2d(pos) - self.last_ch_pos).norm()
			self.walk_x = max(distance/self.last_pace, 0.0)
			x = self.walk_x
			foot_up = self.calcFootUp(x)

			if self.free_foot=="Left":
				self.left_pos = self.calcFootPos(self.left_start, pos, base_ori, x, 1)
			else :
				self.right_pos = self.calcFootPos(self.right_start, pos, base_ori, x, -1)

			# Transition
			if self.velocity_lpf.norm() < self.config['fix_transition_threshold']:
				if self.transition_timer > self.config['fix_transition_timer'] :
					self.state = "Fix_posture"
					self.left_start = self.left_pos
					self.right_start = self.right_pos
					self.last_ch_pos = to_2d(pos)
					self.transition_timer = 0
				else :
					self.transition_timer += 1
					#print("in timer : ", self.transition_timer)
			else :
				self.transition_timer = 0

		elif self.state == "Fix_posture":
			delta_t = self.config['fix_time_step']
			if self.free_foot == "Left":
				if self.fix_state == "STEP0":
					#　現在の遊脚を降ろす
					if self.walk_x < 0.5 :
						x = self.walk_x - delta_t * self.fix_timer
					else :
						x = self.walk_x + delta_t * self.fix_timer
					if (x>0) and (x<1) :
						temp_pos = self.calcFootPos(self.left_start, pos, base_ori, x, 1)
						self.left_pos.z = temp_pos.z
					else :
						temp_pos = self.calcFootPos(self.left_start, pos, base_ori, 1, 1)
						self.left_pos.z = temp_pos.z
						self.fix_state = "STEP1"
						self.right_start = self.right_pos
						self.last_ch_pos = to_2d(pos)
						self.fix_timer = -1
					self.fix_timer += 1

				elif self.fix_state == "STEP1":
					x = delta_t * self.fix_timer
					if x<1 :
						self.right_pos = self.calcFootPos(self.right_start, pos, base_ori, x, -1)
					else :
						self.right_pos = self.calcFootPos(self.right_start, pos, base_ori, 1, -1)
						self.fix_state = "STEP2"
						self.left_start = self.left_pos
						self.last_ch_pos = to_2d(pos)
						self.fix_timer = -1
					self.fix_timer += 1

				elif self.fix_state == "STEP2":
					x = delta_t * self.fix_timer
					if x<1 :
						self.left_pos = self.calcFootPos(self.left_start, pos, base_ori, x, 1)
					else :
						self.left_pos = self.calcFootPos(self.left_start, pos, base_ori, 1, 1)
						self.fix_state = "STEP0"
						self.state = "Stand"
						self.last_ch_pos = to_2d(pos)
						self.fix_timer = -1
					self.fix_timer += 1
					
			elif self.free_foot == "Right":
				if self.fix_state == "STEP0":
					#　現在の遊脚を降ろす
					if self.walk_x < 0.5 :
						x = self.walk_x - delta_t * self.fix_timer
					else :
						x = self.walk_x + delta_t * self.fix_timer
					if (x>0) and (x<1) :
						temp_pos = self.calcFootPos(self.right_start, pos, base_ori, x, -1)
						self.right_pos.z = temp_pos.z
					else :
						temp_pos = self.calcFootPos(self.right_start, pos, base_ori, 1, -1)
						self.right_pos.z = temp_pos.z
						self.fix_state = "STEP1"
						self.left_start = self.left_pos
						self.last_ch_pos = to_2d(pos)
						self.fix_timer = -1
					self.fix_timer += 1

				elif self.fix_state == "STEP1":
					x = delta_t * self.fix_timer
					if x<1 :
						self.left_pos = self.calcFootPos(self.left_start, pos, base_ori, x, 1)
					else :
						self.left_pos = self.calcFootPos(self.left_start, pos, base_ori, 1, 1)
						self.fix_state = "STEP2"
						self.right_start = self.right_pos
						self.last_ch_pos = to_2d(pos)
						self.fix_timer = -1
					self.fix_timer += 1

				elif self.fix_state == "STEP2":
					x = delta_t * self.fix_timer
					if x<1 :
						self.right_pos = self.calcFootPos(self.right_start, pos, base_ori, x, -1)
					else :
						self.right_pos = self.calcFootPos(self.right_start, pos, base_ori, 1, -1)
						self.fix_state = "STEP0"
						self.state = "Stand"
						self.stand_pos = to_2d(pos)
						self.fix_timer = -1
					self.fix_timer += 1
				else:
					self.fix_state = "STEP0"

			# Transition
			if (self.stand_pos - to_2d(pos)).norm() > self.config['walk_transition_threshold']:
				self.state = "Walk"
				self.fix_state = "STEP0"
				self.last_ch_pos = to_2d(pos)




		# -----

		self.so_leftfoot.SetOrientation(self.so_base.GetPose().getOri())
		self.so_rightfoot.SetOrientation(self.so_base.GetPose().getOri())
		self.so_leftfoot.SetFramePosition(self.left_pos)
		self.so_rightfoot.SetFramePosition(self.right_pos)

	def calcFootUp(self, x):
		return 0.5 * (1 + sin(2*pi*x - pi/2)) * self.foot_up_height
		#return sqrt(1-(2*x-1)**2) * self.foot_up_height

	def calcFootPos(self, start, pos, base_ori, x, sign):
		interpolation = (start - (pos + base_ori * Vec3d(sign * self.foot_distance*0.5,0,0))) * (1-x)
		interpolation.z = 0
		return (pos + base_ori * Vec3d(sign * self.foot_distance*0.5,0,self.foot_height + self.calcFootUp(x)) + interpolation)
