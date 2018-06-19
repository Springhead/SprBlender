# -*- coding: utf-8 -*-

import spb

from   collections  import defaultdict
from   spb.utils    import *
from   spb.abbrev   import *
from   Spr          import *
from   math         import *


class LookController():
	def __init__(self, headctl, lefteye, righteye, config):
		self.config   = config

		self.headctl  = headctl

		self.enable_eye_look = True
		if lefteye is not None and righteye is not None:
			self.lefteye  = lefteye.spr()
			self.righteye = righteye.spr()
		else:
			self.enable_eye_look = False

		self.targ_pos = Vec3d(0,-20,0)
		self.attractiveness = 0.0

	def set_target_position(self, pos):
		'''視る対象の位置'''
		self.targ_pos = pos

	def set_attractiveness(self, att):
		'''注意度。0～1で'''
		self.attractiveness = att

	def step(self):
		# 注意量に応じて角度のマージンを変える
		max_margin = self.config['look_max_margin']
		th1        = self.config['look_margin_att_lower_th']
		th2        = self.config['look_margin_att_higher_th']
		#margin     = min(max(0, -max_margin/(th2-th1)*(self.attractiveness-th2)), max_margin)
		margin = 0
		#margin = 0
		self.headctl.SetMargin(margin)

		# <!!> 本当はeyemoveにもマージンが必要…？

		# 頭と目を動かす
		self.headctl.SetFinalPos(self.targ_pos)

		if self.enable_eye_look:
			self.eyemove()

	# ----- ----- ----- ----- -----
	
	def eyemove(self):
		ikeHead = self.headctl.GetIKEndEffector()
		joLEye  = self.lefteye.GetPHJoint()
		joREye  = self.righteye.GetPHJoint()
		soLEye  = self.lefteye.GetPHSolid()
		soREye  = self.righteye.GetPHSolid()

		phScene = ikeHead.GetSolid().GetScene()

		# Calc Gaze Direction
		eyeCenter   = (soLEye.GetPose().getPos() + soREye.GetPose().getPos()) * 0.5

		targRelPos  = (self.targ_pos - eyeCenter).unit()
		targRelPos  = ikeHead.GetSolid().GetPose().getOri().Inv() * targRelPos

		targRelPosL = self.targ_pos - soLEye.GetPose().getPos()
		targRelPosL = ikeHead.GetSolid().GetPose().getOri().Inv() * targRelPosL

		targRelPosR = self.targ_pos - soREye.GetPose().getPos()
		targRelPosR = ikeHead.GetSolid().GetPose().getOri().Inv() * targRelPosR

		y  = atan2(-targRelPos.z, -targRelPos.y )
		xL = atan2(targRelPosL.x, -targRelPosL.y)
		xR = atan2(targRelPosR.x, -targRelPosR.y)

		# Limit Range
		## -- Center
		cL = self.config['lefteye_center_xy']
		cR = self.config['righteye_center_xy']

		dL = Vec2d(xL, y)
		dR = Vec2d(xR, y)
		
		limit = self.config['eye_limit_angle']
		if (dL - cL).norm() > limit:
			dL = cL + ( (dL - cL).unit() * limit )

		if (dR - cR).norm() > limit:
			dR = cR + ( (dR - cR).unit() * limit )

		xL = dL.x
		xR = dR.x
		y  = (dL.y + dR.y) * 0.5

		# Move Eye
		qxL = Quaterniond.Rot(xL,'z')
		qxR = Quaterniond.Rot(xR,'z')
		qy  = Quaterniond.Rot(y, 'x')
		joLEye.SetTargetPosition(qxL * qy)
		joREye.SetTargetPosition(qxR * qy)
