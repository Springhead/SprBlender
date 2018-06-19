# -*- coding: utf-8 -*-

import bpy
import spb

from   mathutils               import Vector,Quaternion
from   spb.handler             import Handler
from   spb.spbapi              import spbapi

from   spb.handlers_imp.solid  import *
from   Spr                     import *
from   spb.synchronizer        import *
from   spb.utils               import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handler
#

class PointerHandler(SolidHandler):
	'''Haptic Pointerとbpy.objectを同期するクラス．'''

	def __init__(self, object):
		Handler.__init__(self)
		self.name       = object.name

		# Bpy Object
		self.object     = object

		# Spr Object
		self.fwPointer  = None
		self.phSolid    = None
		self.hiPose     = None
		self.phTreeNode = None

		# Linked Handlers		
		self.parent     = None
		self.children   = []

		# -- Synchronizers
		self.iftype_sync    = PointerIfTypeSync(self)
		self.state_sync     = PointerStateSync(self)
		# self.inertia_sync   = SolidInertiaSync(self) # <!!>
		self.mass_sync      = SolidMassSync(self)
		self.com_sync       = SolidCoMSync(self)
		self.dynamical_sync = SolidDynamicalSync(self)

	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def before_sync(self):
		'''Synchronize前に行う処理を記述する．オーバーライド用．'''
		# 各PanelのHold/Applyを読み取って，対応するSynchronizerをHold/Applyする．

		# -- Solid Panel
		hold = (self.object.spr_solid_props_hold==1)
		self.state_sync.hold(hold)
		# self.inertia_sync.hold(hold) # <!!>
		self.mass_sync.hold(hold)
		self.com_sync.hold(hold)
		self.dynamical_sync.hold(hold)

		if (self.object.spr_solid_props_apply==1):
			self.state_sync.apply()
			# self.inertia_sync.apply() # <!!>
			self.mass_sync.apply()
			self.com_sync.apply()
			self.dynamical_sync.apply()

	def after_sync(self):
		'''Synchronize後に行う処理を記述する．オーバーライド用．'''
		# ApplyボタンをFalseにリセットする．
		self.object.spr_solid_props_apply       = 0
		self.object.spr_solid_velocity_apply    = 0
		self.object.spr_solid_angvelocity_apply = 0
		self.object.spr_solid_force_apply       = 0
		self.object.spr_solid_torque_apply      = 0

	def build(self):
		'''sprのオブジェクトを構築する'''
		# Create Pointer
		self.fwPointer = spbapi.CreateHapticPointer()
		self.phSolid   = self.fwPointer.GetPHHapticPointer()
		# Set Name
		self.phSolid.SetName("so_"+self.object.name)

		if self.phSolid is None:
			return False
		return True		
		
	def destroy(self):
		if not self.fwPointer is None:
			spbapi.RemovePointer(self.fwPointer)
			self.fwPointer = None
			self.phSolid = None

	def spr(self):
		return self.phSolid

	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		if not type(object) is bpy.types.Object:
			return False
		noparent   = (object.parent is None)
		pointer    = (not object.spr_connect_interface=="None")
		solid_type = (object.spr_object_type=="Solid")
		return pointer and noparent and solid_type


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class PointerIfTypeSync(Synchronizer):
	def is_spr_changed(self):
		return False

	def get_bpy_value(self, last):
		return self.handler.object.spr_connect_interface

	def set_spr_value(self, value):
		if value=="SpaceNavigator":
			spcnav = spbapi.GetSpaceNavigator()
			self.handler.fwPointer.SetHumanInterface(spcnav)
			spcnav.SetMaxVelocity(30)
			spcnav.SetMaxAngularVelocity(rad(600))
			phPointer = self.handler.fwPointer.GetPHHapticPointer()
			phPointer.SetPosScale(1)          # 力覚ポインタの移動スケールの設定
			phPointer.SetReflexSpring(100.0)  # バネ係数の設定
			phPointer.SetReflexDamper(0.0)    # ダンパ係数の設定
			phPointer.EnableForce(False)      # 力を有効にするかどうか
			self.handler.hiPose = spcnav

		if value=="SPIDAR":
			spidar = spbapi.GetSPIDAR()
			self.handler.fwPointer.SetHumanInterface(spidar)
			phPointer = self.handler.fwPointer.GetPHHapticPointer()
			phPointer.SetPosScale(100)        # 力覚ポインタの移動スケールの設定
			phPointer.SetReflexSpring(1000.0) # バネ係数の設定
			phPointer.SetReflexDamper(0.0)    # ダンパ係数の設定
			phPointer.EnableForce(True)       # 力を有効にするかどうか
			self.handler.hiPose = spidar

		if value=="SPIDAR1":
			spidar = spbapi.GetSPIDAR(1)
			self.handler.fwPointer.SetHumanInterface(spidar)
			phPointer = self.handler.fwPointer.GetPHHapticPointer()
			phPointer.SetPosScale(100)        # 力覚ポインタの移動スケールの設定
			phPointer.SetReflexSpring(1000.0) # バネ係数の設定
			phPointer.SetReflexDamper(0.0)    # ダンパ係数の設定
			phPointer.EnableForce(True)       # 力を有効にするかどうか
			self.handler.hiPose = spidar

		if value=="Xbox":
			pass

		if value=="Falcon":
			falcon = spbapi.GetNovintFalcon()
			self.handler.fwPointer.SetHumanInterface(falcon)
			phPointer = self.handler.fwPointer.GetPHHapticPointer()
			phPointer.SetPosScale(100)        # 力覚ポインタの移動スケールの設定
			phPointer.SetReflexSpring(1000.0) # バネ係数の設定
			phPointer.SetReflexDamper(0.0)    # ダンパ係数の設定
			phPointer.EnableForce(True)       # 力を有効にするかどうか
			self.handler.hiPose = falcon


class PointerStateSync(SolidStateSync):
	def set_spr_value(self, value):
		SolidStateSync.set_spr_value(self, value)
		loc, rot, vel = value
		defP = to_f(self.handler.phSolid.GetDefaultPose())
		pose = Posef(to_f(loc), to_f(rot))
		if not self.handler.hiPose is None:
			if self.handler.object.spr_connect_interface=="SpaceNavigator":
				self.handler.hiPose.SetPose(defP.Inv() * pose)

			if self.handler.object.spr_connect_interface=="SPIDAR":
				spbapi.GetSPIDAR().Calibration()
				dp = self.handler.phSolid.GetDefaultPose()
				dp.setPos(to_d(loc))
				self.handler.phSolid.SetDefaultPose(dp)

			if self.handler.object.spr_connect_interface=="Falcon":
				spbapi.GetNovintFalcon().Calibration()
				dp = self.handler.phSolid.GetDefaultPose()
				dp.setPos(to_d(loc))
				self.handler.phSolid.SetDefaultPose(dp)

