# -*- coding: utf-8 -*-

import bpy
import bgl
import blf

import spb
import spb.handlers_imp.joint

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

class CRControllerHandler(Handler):
	'''Spr.CRControllerとbpy.group.spr_controllerを同期するクラス．'''

	def __init__(self, controller):
		Handler.__init__(self)
		self.name          = controller.name

		# Bpy Object
		self.controller    = controller
		self.group         = bpy.data.groups[self.controller.creaturename]

		# Spr Object		
		self.crController  = None

		# -- Synchronizers
		# <!!>
		# self.target_sync      = CRControllerTargetSync(self)
		# self.reach_speed_sync = CRControllerReachAverageSpeedSync(self)


	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def bpy(self):
		'''このハンドラが対応する（広義の）bpyオブジェクト．削除判定に使う'''
		return self.controller


	def spr(self):
		'''自分の持つsprオブジェクトを返す'''
		return self.crController


	def must_removed(self):
		'''このハンドラはもはや消滅すべき状態なのではないだろうかと自問する'''
		if not self.name in self.group.spr_controllers:
			return True
		return False
	

	def update_build_info(self):
		'''Springheadオブジェクトの構築に必要な情報を更新。これが変化すると再構築される。
		ビルドに必要な情報がすべて出揃った場合のみTrueを返すこと'''

		self.build_info["type"] = self.controller.type

		if self.build_info["type"] == "None":
			return False
		
		return True

	def update_dependency(self):
		'''依存関係を更新。これが変化すると再構築される。
		ビルドに必要な依存ハンドラがすべて出揃った場合のみTrueを返すこと'''
		# CRCreature
		try:
			self.dependency["creature"] = spb.handlers.creature_handlers[self.controller.creaturename]
		except (AttributeError, KeyError):
			return False

		return True

	def build(self):
		'''sprのオブジェクトを構築する'''
		# Info
		ctltype     = self.build_info["type"]
		creatureHnd = self.dependency["creature"]

		# Create Controller
		if ctltype=="Reach":
			self.crController = creatureHnd.spr().CreateEngine(CRReachController().GetIfInfoStatic(), CRReachControllerDesc())

			# Set Name
			self.crController.SetName("crctl_"+self.group.name+"_"+self.name)

		else:
			return True

		if self.crController is None:
			return False
		return True

	def destroy(self):
		if not self.crController is None:
			self.dependency["creature"].spr().DelChildObject(self.crController)
			self.crController = None
		self.build_finished = False

	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		return type(object) is spb.properties.CreatureController

	def draw3d(self):
		'''描画を行う（３次元）。'''
		if (self.bpy() is None) or (not self.bpy().visualize) or (self.crController is None):
			return
		self.crController.Draw()



# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class CRControllerTargetSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.bpy().target
	def get_spr_value(self, last):
		if self.handler.spr().NChildObject()<1:
			return self.handler.bpy().target
		else:
			return self.handler.spr().GetIKEndEffector().GetName()[4:]
	def set_bpy_value(self, value):
		self.handler.bpy().target = value
	def set_spr_value(self, value):
		if value in spb.handlers.crbone_handlers:
			ikeff = spb.handlers.ikeff_handlers[value].spr()
			self.handler.spr().SetIKEndEffector(ikeff)


class CRControllerReachAverageSpeedSync(Synchronizer):
	def get_bpy_value(self, last):
		if self.handler.bpy().type=="Reach":
			return self.handler.bpy().reach_speed
		else:
			return None
	def get_spr_value(self, last):
		if self.handler.bpy().type=="Reach":
			return self.handler.spr().GetAverageSpeed()
		else:
			return None
	def set_bpy_value(self, value):
		if self.handler.bpy().type=="Reach":
			self.handler.bpy().reach_speed = value
	def set_spr_value(self, value):
		if self.handler.bpy().type=="Reach":
			self.handler.spr().SetAverageSpeed(value)
