# -*- coding: utf-8 -*-

import spb

from   collections  import defaultdict
from   spb.utils    import *
from   spb.abbrev   import *
from   Spr          import *
from   math         import *


class WalkAnimationController():
	def __init__(self, waist_base, leftfoot, rightfoot, lefttarget_name, righttarget_name):
		self.phScene          = waist_base.spr().GetPHSolid().GetScene()

		self.waist_base       = waist_base
		self.leftfoot         = leftfoot
		self.rightfoot        = rightfoot
		self.lefttarget_name  = lefttarget_name
		self.righttarget_name = righttarget_name

		# states
		self.init_states()

		# parameters
		self.anim_cycle       = 100
		self.foot_distance    = 1.14111 * 2

		self.foot_height      = 0.65414
		#self.foot_height      = 0.1

		self.phase_per_meter  = ((30/100.0) / (1.9301))
		self.pace_scale       = 0.8 # <!!>

		# Flags
		self.b_enabled        = True


	def init_states(self):
		self.phase_master     = 0.0
		self.phase_left       = 0.0
		self.phase_right      = 0.0
		self.foot_pos         = Vec3d(0, 0, 0)
		self.last_foot_pos    = Vec3d(0, 0, 0)
		self.azimuth          = 0
		self.true_azimuth     = 0
		self.phase_direction  = +1


	def enable(self, b_enable):
		if b_enable:
			if not self.b_enabled:
				# Enable
				self.init_states()
				#self.leftfoot.spr().GetIKEndEffector().EnableOrientationControl(False)
				self.leftfoot.spr().GetIKEndEffector().EnablePositionControl(True)
				#self.rightfoot.spr().GetIKEndEffector().EnableOrientationControl(False)
				self.rightfoot.spr().GetIKEndEffector().EnablePositionControl(True)
				self.b_enabled = True

		else:
			if self.b_enabled:
				# Disable
				self.leftfoot.spr().GetIKEndEffector().EnableOrientationControl(False)
				self.leftfoot.spr().GetIKEndEffector().EnablePositionControl(False)
				self.rightfoot.spr().GetIKEndEffector().EnableOrientationControl(False)
				self.rightfoot.spr().GetIKEndEffector().EnablePositionControl(False)
				self.b_enabled = False


	def step(self, pos):
		if not self.b_enabled:
			return

		# --

		body_front = self.waist_base.spr().GetPHSolid().GetPose().getOri() * Vec3d(0,-1,0)
		body_front.z = 0
		q = Quaterniond(); q.RotationArc(Vec3d(0,-1,0), body_front.unit())
		diff_local   = pos - self.last_foot_pos
		diff_local.z = 0
		diff_local   = q.Inv() * diff_local
		
		if (diff_local.norm() > 0.5):
			self.last_foot_pos = pos
			next_azimuth = atan2(diff_local.x, -diff_local.y)
			curr_azimuth = self.azimuth
			diff_azimuth = angle_diff(curr_azimuth, next_azimuth)
			if diff_azimuth > rad(90):
				self.phase_direction *= -1

			self.azimuth = angle_normalize(next_azimuth)

		# 本当の進行方向（逆進中はazimuthとは180度逆）
		true_azimuth = self.azimuth if self.phase_direction>0 else angle_normalize(self.azimuth-rad(180))
		# 補間
		self.true_azimuth = angle_close(self.true_azimuth, true_azimuth, rad(5))

		# --

		path_base_left  = bpy.data.objects[self.lefttarget_name ].constraints['Follow Path'].target.parent
		path_base_right = bpy.data.objects[self.righttarget_name].constraints['Follow Path'].target.parent

		# --

		# 歩幅の変更
		path_base_left.scale  = Vector((1,1,1)) * self.pace_scale
		path_base_right.scale = Vector((1,1,1)) * self.pace_scale

		# phaseの更新
		diff               = pos - self.foot_pos; diff.z = 0
		self.foot_pos      = pos

		self.phase_master += (diff.norm() * self.phase_per_meter * (1/self.pace_scale) * self.phase_direction)
		self.phase_left    = self.phase_master
		self.phase_right   = self.phase_master + 0.5 # <!!>




		# <!!>
		#self.phase_left    = 0.25
		#self.phase_right   = 0.25




		# --

		# 足同士がぶつからないように調整

		#'''
		feet_center = self.foot_pos
		'''
		feet_center = self.waist_base.spr().GetPHSolid().GetPose().getPos()
		#'''
		feet_center.z = 0

		foot_shift  = (self.foot_distance * self.pace_scale * 0.25) * (abs(self.true_azimuth) if abs(self.true_azimuth)<rad(90) else rad(180)-abs(self.true_azimuth)) * (1/rad(90.0))
		path_base_left.location  = to_bpy(feet_center + q * Vec3d( (self.foot_distance*0.5 + foot_shift),0,self.foot_height))
		path_base_right.location = to_bpy(feet_center + q * Vec3d(-(self.foot_distance*0.5 + foot_shift),0,self.foot_height))

		path_base_left.rotation_mode  = "QUATERNION"
		path_base_left.rotation_quaternion  = to_bpy(q * Quaterniond.Rot(self.true_azimuth, 'z'))

		path_base_right.rotation_mode = "QUATERNION"
		path_base_right.rotation_quaternion = to_bpy(q * Quaterniond.Rot(self.true_azimuth, 'z'))

		# ---

		self.phase_left  = cyclic_normalize(self.phase_left,  (0,1), 1)
		c_left  = self.anim_cycle - int(self.anim_cycle * self.phase_left)

		self.phase_right = cyclic_normalize(self.phase_right, (0,1), 1)
		c_right = self.anim_cycle - int(self.anim_cycle * self.phase_right)

		# ---

		#<!!>
		self.set_ik_target_value(self.leftfoot,  self.lefttarget_name,  c_left,  self.true_azimuth)
		self.set_ik_target_value(self.rightfoot, self.righttarget_name, c_right, self.true_azimuth)


	def set_ik_target_value(self, foot, target_name, cycle, azimuth):
		# 目標位置の設定
		bpy.data.objects[target_name].constraints['Follow Path'].offset = cycle
		footpos = to_spr(bpy.data.objects[target_name].matrix_world.translation)

		if foot==self.leftfoot:
			if 'DebugL' in bpy.data.objects:
				bpy.data.objects['DebugL'].location = to_bpy(footpos)
		if foot==self.rightfoot:
			if 'DebugR' in bpy.data.objects:
				bpy.data.objects['DebugR'].location = to_bpy(footpos)

		'''
		foot.spr().GetIKEndEffector().SetTargetPosition(footpos)
		'''
		foot.spr().GetIKEndEffector().GetSolid().SetFramePosition(footpos)
		foot.spr().GetIKEndEffector().GetSolid().SetDynamical(False)
		#'''


		# 目標姿勢の設定
		target_path = bpy.data.objects[target_name].constraints['Follow Path'].target
		ori_objs = {o.constraints['Follow Path'].offset : o for o in bpy.data.objects if 'Follow Path' in o.constraints and o.constraints['Follow Path'].target==target_path and o.name!=target_name}
		if len(ori_objs) < 2:
			return

		ori_objs = sorted(ori_objs.items())
		ori_objs = [(ori_objs[-1][0]-100, ori_objs[-1][1])] + ori_objs + [(ori_objs[0][0]+100, ori_objs[0][1])]
		for i in range(len(ori_objs)-1):
			if ori_objs[i][0] <= cycle and cycle < ori_objs[i+1][0]:
				v1 = ori_objs[i  ][0]
				v2 = ori_objs[i+1][0]
				v  = cycle
				r1 = (v-v1)/(v2-v1)
				r2 = (v2-v)/(v2-v1)

				q1 = to_spr( ori_objs[i  ][1].matrix_world.to_quaternion() ).Rotation()
				q2 = to_spr( ori_objs[i+1][1].matrix_world.to_quaternion() ).Rotation()
				q  = Quaterniond.Rot((q1*r2) + (q2*r1))

				q_ = Quaterniond.Rot(-azimuth,'z') * Quaterniond.Rot( Quaterniond.Rot(azimuth,'z') * q.RotationHalf() )

				'''
				foot.spr().GetIKEndEffector().SetTargetOrientation(q_)
				'''
				foot.spr().GetIKEndEffector().GetSolid().SetOrientation(q_)
				foot.spr().GetIKEndEffector().GetSolid().SetDynamical(False)
				#'''

