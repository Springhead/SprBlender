# -*- coding: utf-8 -*-

import bpy
import spb

from   mathutils        import Vector,Quaternion
from   collections      import defaultdict
from   spb.handler      import Handler
from   spb.spbapi       import spbapi

from   Spr              import *
from   spb.synchronizer import *
from   spb.utils        import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handler
#

class IKEffHandler(Handler):
	'''Spr.PHIKEndEffectorとbpy.objectを同期するクラス．'''

	def __init__(self, object):
		Handler.__init__(self)
		self.name      = object.name

		# Bpy Object
		self.object    = object

		# Spr Object
		self.phIKEff   = None

		# -- Synchronizers
		self.targetlocalpos_sync = IKEffTargetLocalPosSync(self)
		self.targetlocaldir_sync = IKEffTargetLocalDirSync(self)
		self.enableposctl_sync   = IKEffEnablePosCtlSync(self)
		self.enableorictl_sync   = IKEffEnableOriCtlSync(self)
		self.orictlmode_sync     = IKEffOriCtlModeSync(self)
		self.targetpose_sync     = IKEffTargetPoseSync(self)
		self.pospriority_sync	 = IKEffPositionPrioritySync(self)

	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def before_sync(self):
		'''Synchronize前に行う処理を記述する．オーバーライド用．'''
		# 各PanelのHold/Applyを読み取って，対応するSynchronizerをHold/Applyする．

		# -- IKEndEffector Properties
		hold = (self.object.spr_solid_props_hold==1)
		self.targetlocalpos_sync.hold(hold)
		self.enableposctl_sync.hold(hold)
		self.enableorictl_sync.hold(hold)

		if (self.object.spr_solid_props_apply==1):
			self.targetlocalpos_sync.apply()
			self.enableposctl_sync.apply()
			self.enableorictl_sync.apply()

		# -- IKEndEffector Control
		o = self.object
		self.targetpose_sync.transition( o.spr_ik_targetpose_edit, o.spr_ik_targetpose_hold, o.spr_ik_targetpose_apply )
		'''
		self.targetpose_sync.hold( self.object.spr_ik_targetpose_hold==1 )

		if (self.object.spr_ik_targetpose_apply==1):
			self.targetpose_sync.apply()
		'''

	def after_sync(self):
		'''Synchronize後に行う処理を記述する．オーバーライド用．'''
		# ApplyボタンをFalseにリセットする．
		self.object.spr_solid_props_apply   = 0
		self.object.spr_ik_targetpose_apply = 0

	def update_dependency(self):
		'''依存関係を更新。これが変化すると再構築される。
		ビルドに必要な依存ハンドラがすべて出揃った場合のみTrueを返すこと'''
		# Solid
		try:
			self.dependency["solid"] = spb.handlers.solid_handlers[self.name]
		except (AttributeError, KeyError):
			return False

		return True

	def build(self):
		'''sprのオブジェクトを構築する'''
		# Info
		solidHnd = self.dependency["solid"]

		# Create IKEff
		phScene = spbapi.GetFWSdk().GetScene(0).GetPHScene()
		self.phIKEff = phScene.CreateIKEndEffector(PHIKEndEffectorDesc())
		self.phIKEff.Enable(True)

		# Set Solid
		self.phIKEff.AddChildObject(solidHnd.spr())
		
		# Set Name
		self.phIKEff.SetName("ike_"+self.object.name)

		if self.phIKEff is None:
			return False
		return True		

	def destroy(self):
		if not self.phIKEff is None:
			self.phIKEff.Enable(False)
			self.phIKEff.SetName("ike_removed_"+self.object.name)
			spbapi.GetFWSdk().GetScene(0).GetPHScene().GetIKEngine().DelChildObject(self.phIKEff)
			self.phIKEff = None
	
	def spr(self):
		return self.phIKEff
	
	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		if not type(object) is bpy.types.Object:
			return False
		solid_type = (object.spr_object_type=="Solid")
		no_parent  = (object.parent is None)
		ik_enable  = (object.spr_ik_enabled == 1)
		return solid_type and no_parent and ik_enable


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class IKEffTargetLocalPosSync(Synchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_ik_tip_use_obj and o.spr_ik_tip_object_name in bpy.data.objects:
			tip_obj = bpy.data.objects[o.spr_ik_tip_object_name]
			return bpy_object_pose(o).to_3x3().inverted() * (bpy_object_pose(tip_obj).translation - bpy_object_pose(o).translation)
		return Vector((o.spr_ik_target_local_pos_x,o.spr_ik_target_local_pos_y,o.spr_ik_target_local_pos_z))
	def get_spr_value(self, last):
		return self.handler.phIKEff.GetTargetLocalPosition()
	def set_bpy_value(self, value):
		self.handler.object.spr_ik_target_local_pos_x = value.x
		self.handler.object.spr_ik_target_local_pos_y = value.y
		self.handler.object.spr_ik_target_local_pos_z = value.z
	def set_spr_value(self, value):
		self.handler.phIKEff.SetTargetLocalPosition(value)

class IKEffTargetLocalDirSync(Synchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_ik_tip_use_obj and o.spr_ik_tip_object_name in bpy.data.objects:
			tip_obj = bpy.data.objects[o.spr_ik_tip_object_name]
			return bpy_object_pose(o).to_3x3().inverted() * (bpy_object_pose(tip_obj).to_3x3()*Vector((0,0,1)))
		return Vector((o.spr_ik_target_local_dir_x,o.spr_ik_target_local_dir_y,o.spr_ik_target_local_dir_z))
	def get_spr_value(self, last):
		return self.handler.phIKEff.GetTargetLocalDirection()
	def set_bpy_value(self, value):
		self.handler.object.spr_ik_target_local_dir_x = value.x
		self.handler.object.spr_ik_target_local_dir_y = value.y
		self.handler.object.spr_ik_target_local_dir_z = value.z
	def set_spr_value(self, value):
		self.handler.phIKEff.SetTargetLocalDirection(value)

class IKEffOriCtlModeSync(Synchronizer):
	def get_bpy_value(self, last):
		modes = defaultdict(lambda:0, {"Quaternion":0, "Direction":1, "LookAt":2})
		return modes[self.handler.object.spr_ik_ori_control_mode]
	def get_spr_value(self, last):
		return self.handler.phIKEff.GetOriCtlMode()
	def set_bpy_value(self, value):
		modes = defaultdict(lambda:"Quaternion", {0:"Quaternion", 1:"Direction", 2:"LookAt"})
		self.handler.object.spr_ik_ori_control_mode = modes[value]
	def set_spr_value(self, value):
		self.handler.phIKEff.SetOriCtlMode(value)

class IKEffEnablePosCtlSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.spr_ik_pos_control_enabled
	def get_spr_value(self, last):
		return self.handler.phIKEff.IsPositionControlEnabled()
	def set_bpy_value(self, value):
		self.handler.object.spr_ik_pos_control_enabled = value
	def set_spr_value(self, value):
		self.handler.phIKEff.EnablePositionControl(value)
	
class IKEffEnableOriCtlSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.spr_ik_ori_control_enabled
	def get_spr_value(self, last):
		return self.handler.phIKEff.IsOrientationControlEnabled()
	def set_bpy_value(self, value):
		self.handler.object.spr_ik_ori_control_enabled = value
	def set_spr_value(self, value):
		self.handler.phIKEff.EnableOrientationControl(value)

class IKEffPositionPrioritySync(StorableSynchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.spr_ik_position_priority
	def get_spr_value(self, last):
		return self.handler.phIKEff.GetPositionPriority()
	def set_bpy_value(self, value):
		self.handler.object.spr_ik_position_priority = value
	def set_spr_value(self, value):
		self.handler.phIKEff.SetPositionPriority(value)

class IKEffTargetPoseSync(StorableSynchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_ik_target_object_enabled==1 and (o.spr_ik_target_object_name in bpy.data.objects):
			# target objectを目標にする場合
			obj_target = bpy.data.objects[o.spr_ik_target_object_name]
			mat = bpy_object_pose(obj_target)
			loc = mat.to_translation()
			rot = mat.to_quaternion()
		else:
			# 目標を値で指定する場合
			loc = Vector((o.spr_ik_target_pos_x,o.spr_ik_target_pos_y,o.spr_ik_target_pos_z))
			ori = Quaterniond()
			# FromEulerを使うときは座標系の違いに注意 : Blender x,y,z →Springhead z,x,y
			ori.FromEuler(Vec3d(rad(o.spr_ik_target_ori_y),rad(o.spr_ik_target_ori_z),rad(o.spr_ik_target_ori_x)))
			rot = to_bpy(ori)

		return [loc, rot]

	def get_spr_value(self, last):
		pos = self.handler.phIKEff.GetTargetPosition()
		ori = self.handler.phIKEff.GetTargetOrientation()
		return [pos, ori]

	def set_bpy_value(self, value):
		loc, rot = value
		o = self.handler.object
		if o.spr_ik_target_object_enabled==1 and (o.spr_ik_target_object_name in bpy.data.objects):
			# target objectを目標にする場合
			obj_target = bpy.data.objects[o.spr_ik_target_object_name]
			if (obj_target.parent is None and (not obj_target.spr_use_matrix_world==1)):
				# Childでない場合
				# obj_target.location = loc
				# obj_target.rotation_quaternion = rot
				pass
			else:
				# Static Child, または Use Matrix Worldの場合
				# ＜Not Implemented＞ <!!>  というよりStatic Child自体がObsoleted予定なので
				pass
		else:
			# 目標を値で指定する場合
			o.spr_ik_target_pos_x = loc.x
			o.spr_ik_target_pos_y = loc.y
			o.spr_ik_target_pos_z = loc.z

			v = Vec3d()
			to_spr(rot).ToEuler(v)
			# ToEulerを使うときは座標系の違いに注意 : Blender x,y,z →Springhead z,x,y
			o.spr_ik_target_ori_y = deg(v.x)
			o.spr_ik_target_ori_z = deg(v.y)
			o.spr_ik_target_ori_x = deg(v.z)

	def set_spr_value(self, value):
		pos, ori = value
		self.handler.phIKEff.SetTargetPosition(pos)
		self.handler.phIKEff.SetTargetOrientation(ori)


	
