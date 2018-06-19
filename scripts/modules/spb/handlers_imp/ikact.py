# -*- coding: utf-8 -*-

import bpy
import spb

from   mathutils        import Vector,Quaternion
from   spb.handler      import Handler
from   spb.spbapi       import spbapi

from   Spr              import *
from   spb.synchronizer import *
from   spb.utils        import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handler
#

class IKActHandler(Handler):
	'''Spr.PHIKActuatorとbpy.objectを同期するクラス．'''

	def __init__(self, object):
		Handler.__init__(self)
		self.name      = object.name

		# Bpy Object
		self.object    = object

		# Spr Object
		self.phIKAct   = None

		# -- Synchronizers
		self.bias_sync         = IKActBiasSync(self)
		self.pullbackrate_sync = IKActPullbackRateSync(self)

	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def before_sync(self):
		'''Synchronize前に行う処理を記述する．オーバーライド用．'''
		# 各PanelのHold/Applyを読み取って，対応するSynchronizerをHold/Applyする．

		# -- IKActuator Properties
		hold = (self.object.spr_joint_props_hold==1)
		self.bias_sync.hold(hold)

		if (self.object.spr_joint_props_apply==1):
			self.bias_sync.apply()

	def after_sync(self):
		'''Synchronize後に行う処理を記述する．オーバーライド用．'''
		# ApplyボタンをFalseにリセットする．
		self.object.spr_joint_props_apply = 0

	def update_dependency(self):
		'''依存関係を更新。これが変化すると再構築される。
		ビルドに必要な依存ハンドラがすべて出揃った場合のみTrueを返すこと'''
		# Joint
		try:
			self.dependency["joint"] = spb.handlers.joint_handlers[self.name]
		except (AttributeError, KeyError):
			return False

		# 子IKAct : 無いこともある
		try:
			cnt = 0
			jointHnd = self.dependency["joint"]
			for iah in spb.handlers.ikact_handlers.values():
				if (iah.dependency["joint"].dependency["soSocket"].name==jointHnd.dependency["soPlug"].name):
					self.dependency["child"+str(cnt)] = iah
					cnt += 1
		except (AttributeError, KeyError):
			pass # なくても良いので気にせず通過

		# IKEff : 無くても良い
		try:
			soPlugName = self.dependency["joint"].dependency["soPlug"].name
			if soPlugName in spb.handlers.ikeff_handlers:
				self.dependency["ikeff"] = spb.handlers.ikeff_handlers[soPlugName]
		except (AttributeError, KeyError):
			pass # なくても良いので気にせず通過

		return True

	def build(self):
		'''sprのオブジェクトを構築する'''
		# Info
		jointHnd  = self.dependency["joint"]
		jointtype = jointHnd.build_info["jointtype"]

		# Create IKAct
		phScene = spbapi.GetFWSdk().GetScene(0).GetPHScene()
		if jointtype=="Ball":
			ballinfo = PHIKBallActuator().GetIfInfoStatic()
			balldesc = PHIKBallActuatorDesc()
			self.phIKAct = phScene.CreateIKActuator(ballinfo, balldesc)
		elif jointtype=="Hinge":
			hingeinfo = PHIKHingeActuator().GetIfInfoStatic()
			hingedesc = PHIKHingeActuatorDesc()
			self.phIKAct = phScene.CreateIKActuator(hingeinfo, hingedesc)
		else:
			debuglog.log("ERROR", "Error : IKActuator is only for Ball / Hinge.", self.name)
			return

		self.phIKAct.Enable(True)

		# Set Name
		self.phIKAct.SetName("ika_"+self.object.name)

		# Set Joint
		self.phIKAct.AddChildObject(jointHnd.spr())
		
		# Add Child IKActuator
		cnt = 0
		while True:
			if ("child"+str(cnt)) in self.dependency:
				self.spr().AddChildObject( self.dependency["child"+str(cnt)].spr() )
				cnt += 1
			else:
				break

		# Set EndEffector
		if ("ikeff" in self.dependency):
			self.phIKAct.AddChildObject(self.dependency["ikeff"].spr())

		if self.phIKAct is None:
			return False
		return True		

	def destroy(self):
		if not self.phIKAct is None:
			self.phIKAct.Enable(False)
			self.phIKAct.SetName("ika_removed_"+self.name)
			spbapi.GetFWSdk().GetScene(0).GetPHScene().GetIKEngine().DelChildObject(self.phIKAct)
			self.phIKAct = None

	def spr(self):
		return self.phIKAct

	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		if not type(object) is bpy.types.Object:
			return False
		joint_type = (object.spr_object_type== "Joint")
		ik_enable  = (object.spr_ik_enabled == 1)
		balljoint  = (object.spr_joint_mode == "Ball")
		hingejoint = (object.spr_joint_mode == "Hinge")
		return joint_type and ik_enable and (balljoint or hingejoint)


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class IKActBiasSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.spr_ik_bias
	def get_spr_value(self, last):
		return self.handler.phIKAct.GetBias()
	def set_bpy_value(self, value):
		self.handler.object.spr_ik_bias = value
	def set_spr_value(self, value):
		self.handler.phIKAct.SetBias(value)


class IKActPullbackRateSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.spr_ik_pullback_rate
	def get_spr_value(self, last):
		return self.handler.phIKAct.GetPullbackRate()
	def set_bpy_value(self, value):
		self.handler.object.spr_ik_pullback_rate = value
	def set_spr_value(self, value):
		self.handler.phIKAct.SetPullbackRate(value)


