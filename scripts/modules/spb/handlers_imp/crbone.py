# -*- coding: utf-8 -*-

import bpy
import spb
import spb.handlers_imp.joint

from   spb.handlers_imp.solid import SolidHandler

from   mathutils        import Vector,Quaternion
from   spb.handler      import Handler
from   spb.spbapi       import spbapi

from   Spr              import *
from   spb.synchronizer import *
from   spb.utils        import *

from   spb.handlers_imp.solid import SolidHandler


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handler
#

class CRBoneHandler(Handler):
	'''Spr.CRBoneとbpy.objectを同期するクラス．'''

	def __init__(self, object):
		Handler.__init__(self)
		self.name        = object.name

		# Bpy Object
		self.object      = object

		# Spr Object
		self.crBone      = None

		# -- Synchronizers
		self.label_sync = CRBoneLabelSync(self)

	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def update_dependency(self):
		'''依存関係を更新。これが変化すると再構築される。
		ビルドに必要な依存ハンドラがすべて出揃った場合のみTrueを返すこと'''
		# CRCreature
		try:
			for crHnd in spb.handlers.creature_handlers.values():
				if self.name in crHnd.group.objects:
					self.dependency["creature"] = crHnd
			if not "creature" in self.dependency:
				return False
		except (AttributeError, KeyError):
			return False

		# Solid
		try:
			if self.name in spb.handlers.solid_handlers:
				self.dependency["solid"] = spb.handlers.solid_handlers[self.name]
		except (AttributeError, KeyError):
			return False # Solidは必須

		# EndEffector
		try:
			if self.name in spb.handlers.ikeff_handlers:
				self.dependency["ikeff"] = spb.handlers.ikeff_handlers[self.name]
		except (AttributeError, KeyError):
			pass # なくても良いので気にせず通過

		# Joint
		try:
			for jh in spb.handlers.joint_handlers.values():
				if (not jh.dependency["soPlug"] is None) and (jh.dependency["soPlug"].object.name==self.object.name):
					self.dependency["joint"] = jh
		except (AttributeError, KeyError):
			pass # なくても良いので気にせず通過

		# Actuator
		try:
			if ("joint" in self.dependency) and (self.dependency["joint"].name in spb.handlers.ikact_handlers):
				self.dependency["ikact"] = spb.handlers.ikact_handlers[self.dependency["joint"].name]
		except (AttributeError, KeyError):
			pass # なくても良いので気にせず通過

		return True

	def build(self):
		'''sprのオブジェクトを構築する'''
		# Info
		creatureHnd = self.dependency["creature"]

		# Create Bone
		crBody = creatureHnd.spr().GetBody(0)
		self.crBone = crBody.CreateObject(CRBone().GetIfInfoStatic(), CRBoneDesc())

		# Set Name
		self.crBone.SetName("crbone_"+self.object.name)

		# Add Solid
		if "solid" in self.dependency:
			self.crBone.AddChildObject(self.dependency["solid"].spr())

		# Add EndEffector
		if "ikeff" in self.dependency:
			self.crBone.AddChildObject(self.dependency["ikeff"].spr())

		# Add Joint
		if "joint" in self.dependency:
			self.crBone.AddChildObject(self.dependency["joint"].spr())

		# Add Actuator
		if "ikact" in self.dependency:
			self.crBone.AddChildObject(self.dependency["ikact"].spr())

			# Joint Handlerの Spring/Damper Syncにmodifierを登録(Spring/Damper Ratio用)
			try:
				jointHnd = self.dependency["ikact"].dependency["joint"]
				for sync in jointHnd.synchronizers:
					if type(sync) is spb.handlers_imp.joint.JointSpringSync:
						sync.modifiers[self] = [self.modify_bpy_joint_spring, self.modify_spr_joint_spring]
					if type(sync) is spb.handlers_imp.joint.JointDamperSync:
						sync.modifiers[self] = [self.modify_bpy_joint_damper, self.modify_spr_joint_damper]
			except (AttributeError, KeyError):
				pass

		if self.crBone is None:
			return False
		return True

	def destroy(self):
		if not self.crBone is None:
			self.crBone.SetName("crbone_removed_"+self.name)
			if "creature" in self.dependency:
				self.dependency["creature"].spr().GetBody(0).DelChildObject(self.crBone)
			self.crBone = None

			# 仕掛けたmodifierを去り際に撤去していく
			try:
				jointHnd = self.dependency["ikact"].dependency["joint"]
				for sync in jointHnd.synchronizers:
					if self in sync.modifiers:
						sync.modifiers.pop(self)

			except (AttributeError, KeyError):
				pass

		self.build_finished = False

	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		if not type(object) is bpy.types.Object:
			return False
		if not SolidHandler.is_target(object):
			return False
		for grp in object.users_group:
			if grp.spr_creature_group==1:
				return True
		return False

	def spr(self):
		return self.crBone

	def spr_storable(self):
		return False
	
	# --- --- --- --- ---

	# Spring/Damper Ratioを実現するためのmodifier
	def modify_bpy_joint_spring(self, value):
		sr = self.dependency["creature"].group.spr_creature_spring_ratio * self.dependency["creature"].group.spr_creature_spring_damper_ratio
		return value * sr
	def modify_spr_joint_spring(self, value):
		return value
	def modify_bpy_joint_damper(self, value):
		dr = self.dependency["creature"].group.spr_creature_damper_ratio * self.dependency["creature"].group.spr_creature_spring_damper_ratio
		return value * dr
	def modify_spr_joint_damper(self, value):
		return value




# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class CRBoneLabelSync(Synchronizer):
	def get_bpy_value(self, last):
		self.handler.object.spr_crbone_label = self.handler.object.spr_CRIKSolid_label # <!!> 移行措置
		return self.handler.object.spr_crbone_label
	def get_spr_value(self, last):
		return self.handler.crBone.GetLabel()
	def set_bpy_value(self, value):
		self.handler.object.spr_crbone_label = value
	def set_spr_value(self, value):
		self.handler.crBone.SetLabel(value)

