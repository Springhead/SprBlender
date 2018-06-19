# -*- coding: utf-8 -*-

import spb

from   collections  import defaultdict
from   spb.utils    import *
from   spb.abbrev   import *
from   Spr          import *
from   math         import *


class TouchController:
	def __init__(self, reachctl, perception, config):
		# Init
		self.state		= ObjectStates().Create()
		self.reachctl	= reachctl
		self.perception = perception
		self.config		= config
		
		self.targ_solid = None
		self.Cal		= Caliculate(self.reachctl)
		self.InitPos	= self.reachctl.GetIKEndEffector().GetSolid().GetPose().getPos()

		# Flag
		self.Time		= 0
		
	def set_target_solid(self, solid, touch_pos = Vec3d(0,0,0)):
		'''触れる対象の剛体'''
		self.targ_solid = solid
		self.touch_pos	= touch_pos
		
	def set_parameter(self, CalLPFvalue):
		# Caliculate parameter
		self.Cal.Set_parameter(CalLPFvalue)
		
	def step(self):
		# renew target state
		if self.targ_solid is None:
			return

		# <!!>
		targ_pos = self.targ_solid.GetPose().transform(self.touch_pos)

		targ_rel_pos = So["so_Waist"].spr().GetPose().Inv().transform(targ_pos)
		#print(targ_rel_pos)

		if targ_pos.norm() < 50 and targ_rel_pos.y < 2:
			self.reachctl.SetFinalPos(targ_pos)

		return

		
		# -----

		targPos			= self.targ_solid.GetPose().getPos()
		targVel			= self.targ_solid.GetVelocity()
		
		### 興味対象の位置推定
		# lefthand
		# LPF-handVelocity
		LPFVel		= self.Cal.LPFVelocity()
		
		# Reaching Off
		# handPosition init
		self.InitPos	= self.reachctl.GetIKEndEffector().GetSolid().GetPose().getPos()
		# estimatePosition
		EstimatePos	= self.Cal.EstimatePos(targPos, targVel, self.InitPos, LPFVel)
		#--debugDraw
		TemporaryPos = self.reachctl.GetIKEndEffector().GetSolid().GetPose().getPos()
		# Reaching On
		if self.reachctl.GetStatus() == 1:
			# handPosition renew
			if self.reachctl.GetCurrentTime() < self.Time:
				#print("renew(lh)")
				self.InitPos	= self.reachctl.GetIKEndEffector().GetSolid().GetPose().getPos()
			self.Time		= self.reachctl.GetCurrentTime()
			# AverageVelocity & temporaryPosition
			AverageVel, TemporaryPos = self.Cal.TemporaryPos(EstimatePos, self.InitPos)
			# estimatePosition
			EstimatePos	= self.Cal.EstimatePos(targPos, targVel, TemporaryPos, AverageVel)	
		
		# SetFinalPosition
		self.reachctl.SetFinalPos(EstimatePos)

class Caliculate:
	def __init__(self,reachctl):
		self.ctl			= reachctl
		# LPF
		self.alpha			= 0.5
		self.velocityLPF	= Vec3d(0,0,0)
		
	def Set_parameter(self, alpha):
		self.alpha			= alpha
		
	def LPFVelocity(self):
		Velocity			= self.ctl.GetIKEndEffector().GetSolid().GetVelocity()
		self.velocityLPF	= Vec3d( self.alpha * Velocity.x + (1 - self.alpha) * self.velocityLPF.x
								   , self.alpha * Velocity.y + (1 - self.alpha) * self.velocityLPF.y
								   , self.alpha * Velocity.z + (1 - self.alpha) * self.velocityLPF.z)
		return self.velocityLPF
		
	def EstimatePos(self, targPos, targVel, handPos, handLPFVel):
		closingVel		= targVel - handLPFVel
		closingPos		= targPos - handPos
		closingTime		= closingPos.norm() / closingVel.norm()
		estPos			= targPos + targVel * closingTime
		return estPos
		
	def TemporaryPos(self, estimatePos, handInitPos):
		distance		= (estimatePos - handInitPos).norm()
		AverageVel		= Vec3d( ( distance / self.ctl.GetReachTime() ) * ( estimatePos - handInitPos ).unit().x
							   , ( distance / self.ctl.GetReachTime() ) * ( estimatePos - handInitPos ).unit().y
							   , ( distance / self.ctl.GetReachTime() ) * ( estimatePos - handInitPos ).unit().z )
		temporaryPos	= handInitPos + AverageVel * self.ctl.GetCurrentTime()
		return AverageVel, temporaryPos