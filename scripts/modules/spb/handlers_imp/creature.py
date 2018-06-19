# -*- coding: utf-8 -*-

import bpy
import spb

from   mathutils        import Vector,Quaternion
from   threading        import Lock
from   spb.handler      import Handler
from   spb.spbapi       import spbapi

from   Spr              import *
from   spb.synchronizer import *
from   spb.utils        import *
from   spb.scriptengine import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handler
#

class CreatureHandler(Handler):
	'''Spr.CRCreatureとbpy.groupを同期するクラス．'''

	def __init__(self, group):
		Handler.__init__(self)
		self.name       = group.name

		# Bpy Object
		self.group      = group

		# Spr Object
		self.crCreature = None

		# Linked Handlers
		pass

		# Others
		self.rule       = ScriptEngine()
		self.rule.set_name("creature_rule_"+self.group.name)
		self.first_step = True
		
		self.write_cash={}
		self.read_cash={}
		
		self.write_lock = Lock()
		self.read_lock  = Lock()
		
		self.write_param()

		# -- Synchronizers
		# (None)

	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def bpy(self):
		'''このハンドラが対応する（広義の）bpyオブジェクト．削除判定に使う'''
		# Creatureの場合，objectではなくgroupに対して作られるので．
		return self.group

	def build(self):
		'''sprのオブジェクトを構築する'''
		# Create Creature
		self.crCreature = spbapi.GetCRSdk().CreateCreature(CRCreature().GetIfInfoStatic(), CRCreatureDesc())
		self.crCreature.AddChildObject(spbapi.GetFWSdk().GetScene(0).GetPHScene())

		# Create Body
		self.crCreature.CreateBody(CRBody().GetIfInfoStatic(), CRBodyDesc())

		# Set Name
		self.crCreature.SetName("creature_"+self.group.name)
		self.crCreature.GetBody(0).SetName("body_"+self.name)

		if self.crCreature is None:
			return False
		return True

	def step(self):
		self.write_param()
		self.read_param()
		# self.rule.step_bpy() # <!!>
		
	def destroy(self):
		if not self.crCreature is None:
			self.crCreature.SetName("removed_creature_"+self.group.name)
			spbapi.GetCRSdk().DelChildObject(self.crCreature)
			self.crCreature = None
	
	def post_build(self):
		self.rule.update()
		return True

	@classmethod
	def is_target(cls, group):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		if not type(group) is bpy.types.Group:
			return False
		is_creature = (group.spr_creature_group==1)
		return is_creature
	
	def spr(self):
		return self.crCreature

	def spr_storable(self):
		return False
	
	def draw3d(self):
		'''描画を行う（３次元）'''
		if self.rule.initialized:
			self.rule.draw()

	#---------------------
	# パラメータアクセス

	@synchronized(lambda self: self.write_lock)
	def write_param(self):
		for param in self.group.spr_creature_parameters.values():
			self.write_cash[param.name] = param.value
	
	@synchronized(lambda self: self.read_lock)
	def read_param(self):
		for name in self.read_cash.keys():
			if name in self.write_cash.keys():
				self.group.spr_creature_parameters[name] = read_cash[name]
		self.read_cash = {}
	
	@synchronized(lambda self: self.write_lock)
	def get_cr_param(self,name,default = None):
		if name in self.write_cash:
			return self.write_cash[name]
		debuglog.log("EVENT", "get_cr_param : Parameter Not Found : ", self.name, name)
		return default
	
	@synchronized(lambda self: self.read_lock)
	def set_cr_param(self,name,value,default = None):
		read_cash[name] = value

	# --- --- --- --- ---
	# 追加機能

	def get_ika_tree(self):
		'''このクリーチャのBodyに属するIKActuatorに対応するbpy_objのツリー状一覧を取得する'''
		ikas = []

		# Bodyごとに
		for i in range(0,self.crCreature.NBodies()):
			body = self.crCreature.GetBody(i)

			# RootActuatorを探す
			for bone in body.GetBones():
				if (not bone.GetIKActuator() is None) and (bone.GetIKActuator().GetParent() is None):
					ika  = bone.GetIKActuator()
					name = ika.GetName()[4:]
					ikas.append([0, name])
					self.get_ika_tree_recursive(ika, ikas, 0)

		return sorted(ikas, key=lambda x: x[0])

	def get_ika_tree_recursive(self, ika, ikas, level):
		'''get_ika_treeの再帰部分実装'''
		for i in range(0,ika.NChildActuators()):
			child_ika = ika.GetChildActuator(i)
			name      = child_ika.GetName()[4:]
			ikas.append([level+1, name])
			self.get_ika_tree_recursive(child_ika, ikas, level+1)

	def get_engine(self, engine_type, desc, n=0):
		'''CREngineを見つけるか作るかして返す'''
		count = 0
		for i in range(self.spr().NEngines()):
			e = self.spr().GetEngine(i)
			if type(e) is engine_type:
				if count==n:
					return e
				else:
					count += 1
					continue
		return self.spr().CreateEngine(engine_type.GetIfInfoStatic(), desc)
		
	def get_nengine(self, engine_type):
		'''CREngineの数を返す'''
		count = 0
		for i in range(self.spr().NEngines()):
			e = self.spr().GetEngine(i)
			if type(e) is engine_type:
				count += 1
		return count
