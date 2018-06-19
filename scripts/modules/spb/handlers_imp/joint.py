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

class JointHandler(Handler):
	'''Spr.PHJointとbpy.objectを同期するクラス．'''

	def __init__(self, object):
		Handler.__init__(self)
		self.name      = object.name

		# Bpy Object
		self.object    = object

		# Spr Object
		self.phJoint   = None

		# -- Synchronizers
		self.collision_sync      = JointCollisionSync(self)
		self.enable_sync         = JointEnableSync(self)
		self.plugsocketpose_sync = JointPlugSocketPoseSync(self)
		self.spring_sync         = JointSpringSync(self)
		self.damper_sync         = JointDamperSync(self)
		self.springori_sync      = JointSpringOriSync(self)
		self.damperori_sync      = JointDamperOriSync(self)
		self.targetposition_sync = JointTargetPositionSync(self)
		self.targetvelocity_sync = JointTargetVelocitySync(self)
		self.offsetforce_sync    = JointOffsetForceSync(self)
		self.maxforce_sync       = JointMaxForceSync(self)


	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def before_sync(self):
		'''Synchronize前に行う処理を記述する．オーバーライド用．'''
		# 各PanelのHold/Applyを読み取って，対応するSynchronizerをHold/Applyする．

		# -- Joint Panel
		hold = (self.object.spr_joint_props_hold==1)
		self.collision_sync.hold(hold)
		self.enable_sync.hold(hold)
		self.plugsocketpose_sync.hold(hold)
		self.spring_sync.hold(hold)
		self.damper_sync.hold(hold)
		self.springori_sync.hold(hold)
		self.damperori_sync.hold(hold)
		self.maxforce_sync.hold(hold)

		if (self.object.spr_joint_props_apply==1):
			self.collision_sync.apply()
			self.enable_sync.apply()
			self.plugsocketpose_sync.apply()
			self.spring_sync.apply()
			self.damper_sync.apply()
			self.springori_sync.apply()
			self.damperori_sync.apply()
			self.maxforce_sync.apply()

		# -- Joint Control Panel
		o = self.object
		self.targetposition_sync.transition( o.spr_joint_targetposition_edit, o.spr_joint_targetposition_hold, o.spr_joint_targetposition_apply )
		self.targetvelocity_sync.transition( o.spr_joint_velocity_edit,       o.spr_joint_velocity_hold,       o.spr_joint_velocity_apply       )
		self.offsetforce_sync.transition(    o.spr_joint_offsetforce_edit,    o.spr_joint_offsetforce_hold,    o.spr_joint_offsetforce_apply    )

	def after_sync(self):
		'''Synchronize後に行う処理を記述する．オーバーライド用．'''
		# ApplyボタンをFalseにリセットする．
		self.object.spr_joint_props_apply          = 0
		self.object.spr_joint_targetposition_apply = 0
		self.object.spr_joint_velocity_apply       = 0
		self.object.spr_joint_offsetforce_apply    = 0

	def update_build_info(self):
		'''Springheadオブジェクトの構築に必要な情報を更新。これが変化すると再構築される。
		ビルドに必要な情報がすべて出揃った場合のみTrueを返すこと'''

		self.build_info["jointtype"] = self.object.spr_joint_mode
		self.build_info["joint_aba"] = self.object.spr_joint_aba

		return True

	def update_dependency(self):
		'''依存関係を更新。これが変化すると再構築される。
		ビルドに必要な依存ハンドラがすべて出揃った場合のみTrueを返すこと'''

		So = spb.handlers.solid_handlers
		o  = self.object
		try:
			try:
				self.dependency["soSocket"] = So[bpy.data.objects[o.spr_joint_socket_target_name].parent.name]
			except (AttributeError, KeyError):
				self.dependency["soSocket"] = So[o.spr_joint_socket_target_name]

			self.dependency["soPlug"] = So[o.parent.name]

		except (AttributeError, KeyError):
			return False

		return True

	def build(self):
		'''対応するSpringhead側オブジェクトを構築する。'''
		# Info
		jointtype = self.build_info["jointtype"]
		socketHnd = self.dependency["soSocket" ]
		plugHnd   = self.dependency["soPlug"   ]

		# Create Joint
		self.phJoint = spbapi.CreateJoint(socketHnd.spr(), plugHnd.spr(), jointtype)

		# Set Name
		self.phJoint.SetName("jo_"+self.object.name)

		# TreeNode用 : Solidに親子関係をセットする
		if self.build_info["joint_aba"]:
			socketHnd.children.append(plugHnd)
			plugHnd.parent = socketHnd

		if self.phJoint is None:
			return False
		return True		

	def destroy(self):
		'''Springheadオブジェクトを削除する．存在しないものものを消さないように気をつけること'''
		if not self.phJoint is None:
			spbapi.RemoveJoint(self.phJoint)
			self.phJoint = None
			# <!!>ここでTreeNodeを削除する必要がある
	
	def spr(self):
		return self.phJoint
	
	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		if not type(object) is bpy.types.Object:
			return False
		joint_type  = (object.spr_object_type=="Joint")
		return joint_type


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class JointPlugSocketPoseSync(Synchronizer):
	def is_spr_changed(self):
		return False

	def is_bpy_changed(self):
		'''bpyの新しい値を取得して，変更があったかを返す'''
		new = self.get_bpy_value_mod(self.bpy)
		old = self.bpy
		for i in range(2):
			v1 = Vector([n for n in new[i]])
			v2 = Vector([n for n in old[i]])
			if (v1-v2).length > 1e-3:
				return True
		return False

	def get_bpy_value(self, last):
		# <!!> RoundConeがズレるのを防止するため
		if bpy.context.scene.spr_step_enabled:
			return last

		ho = self.handler.object

		# Socketの剛体や軸オブジェクト
		if ho.spr_joint_socket_target == "Solid Name":
			sockaxis = ho.name
		elif ho.spr_joint_socket_target == "Axis Name":
			sockaxis = ho.spr_joint_socket_target_name

		sa = bpy.data.objects[sockaxis] if (sockaxis in bpy.data.objects) else ho
		so = self.handler.dependency["soSocket"].object

		# Plugの剛体や軸オブジェクト
		plugaxis = ho.name

		pa = bpy.data.objects[plugaxis] if (plugaxis in bpy.data.objects) else ho
		po = self.handler.dependency["soPlug"].object

		# さていっちょやりますか
		# p_rel        = scale_matrix(po.scale) * bpy_object_pose(po).inverted() * bpy_object_pose(pa)
		p_rel        = bpy_object_pose(po).inverted() * bpy_object_pose(pa)
		bpy_plug_pos = p_rel.to_translation()
		bpy_plug_ori = p_rel.to_quaternion()

		# s_rel        = scale_matrix(so.scale) * bpy_object_pose(so).inverted() * bpy_object_pose(sa)
		s_rel        = bpy_object_pose(so).inverted() * bpy_object_pose(sa)
		bpy_sock_pos = s_rel.to_translation()
		bpy_sock_ori = s_rel.to_quaternion()

		pp = bpy_plug_pos; po = bpy_plug_ori
		sp = bpy_sock_pos; so = bpy_sock_ori
			
		return [pp, sp, po, so]

	def set_spr_value(self, value):
		pp, sp, po, so = value
		self.handler.phJoint.SetPlugPose(  Posed(Vec3d(pp.x,pp.y,pp.z), Quaterniond(po.w,po.x,po.y,po.z)))
		self.handler.phJoint.SetSocketPose(Posed(Vec3d(sp.x,sp.y,sp.z), Quaterniond(so.w,so.x,so.y,so.z)))


class JointCollisionSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.spr_joint_collision
	def set_spr_value(self, value):
		phScene = spbapi.GetFWSdk().GetScene(0).GetPHScene()
		if value==0:
			phScene.SetContactMode(self.handler.dependency["soPlug"].phSolid, self.handler.dependency["soSocket"].phSolid, 0)
		else:
			phScene.SetContactMode(self.handler.dependency["soPlug"].phSolid, self.handler.dependency["soSocket"].phSolid, 2)
		
class JointEnableSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.spr_joint_enabled
	def get_spr_value(self, last):
		return self.handler.phJoint.IsEnabled()
	def set_bpy_value(self, value):
		self.handler.object.spr_joint_enabled = value
	def set_spr_value(self, value):
		self.handler.phJoint.Enable(value)

class JointSpringSync(Synchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			bpy_spring = Vector((o.spr_spring_x,o.spr_spring_y,o.spr_spring_z))
		else:
			bpy_spring = o.spr_spring
		return bpy_spring
	def get_spr_value(self, last):
		return self.handler.phJoint.GetSpring()
	def set_bpy_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			o.spr_spring_x = value.x
			o.spr_spring_y = value.y
			o.spr_spring_z = value.z
		else:
			o.spr_spring = value
	def set_spr_value(self, value):
		self.handler.phJoint.SetSpring(value)

class JointDamperSync(Synchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			bpy_damper = Vector((o.spr_damper_x,o.spr_damper_y,o.spr_damper_z))
		else:
			bpy_damper = o.spr_damper
		return bpy_damper
	def get_spr_value(self, last):
		return self.handler.phJoint.GetDamper()
	def set_bpy_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			o.spr_damper_x = value.x
			o.spr_damper_y = value.y
			o.spr_damper_z = value.z
		else:
			o.spr_damper = value
	def set_spr_value(self, value):
		self.handler.phJoint.SetDamper(value)

class JointSpringOriSync(Synchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			return o.spr_spring_ori
		else:
			return None
	def get_spr_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			return self.handler.phJoint.GetSpringOri()
		else:
			return None
	def set_bpy_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			o.spr_spring_ori = value
	def set_spr_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			self.handler.phJoint.SetSpringOri(value)

class JointDamperOriSync(Synchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			return o.spr_damper_ori
		else:
			return None
	def get_spr_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			return self.handler.phJoint.GetDamperOri()
		else:
			return None
	def set_bpy_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			o.spr_damper_ori = value
	def set_spr_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Spring":
			self.handler.phJoint.SetDamperOri(value)

class JointTargetPositionSync(StorableSynchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Hinge":
			return rad(o.spr_joint_target_position)
		elif o.spr_joint_mode=="Slider":
			return o.spr_joint_target_position
		elif o.spr_joint_mode=="Ball":
			####FromEuler/ToEulerを使うときは座標系の違いに注意 Blender x,y,z →Springhead z,x,y
			tp = Quaterniond()
			tp.FromEuler(Vec3d(rad(o.spr_joint_target_position_y), rad(o.spr_joint_target_position_z), rad(o.spr_joint_target_position_x)))
			return tp
		else:
			return None
	def get_spr_value(self, last):
		o = self.handler.object
		if not o.spr_joint_mode=="Spring":
			return self.handler.phJoint.GetTargetPosition()
		else:
			return None
	def set_bpy_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Hinge":
			o.spr_joint_target_position = deg(value)
		elif o.spr_joint_mode=="Slider":
			o.spr_joint_target_position = value
		elif o.spr_joint_mode=="Ball":
			####FromEuler/ToEulerを使うときは座標系の違いに注意 Blender x,y,z →Springhead z,x,y
			v = Vec3d()
			to_spr(value).ToEuler(v)
			o.spr_joint_target_position_y = deg(v.x)
			o.spr_joint_target_position_z = deg(v.y)
			o.spr_joint_target_position_x = deg(v.z)
	def set_spr_value(self, value):
		o = self.handler.object
		if not o.spr_joint_mode=="Spring":
			pass #<!!> self.handler.phJoint.SetTargetPosition(value)

class JointTargetVelocitySync(StorableSynchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Hinge" or o.spr_joint_mode=="Slider":
			return o.spr_joint_target_velocity
		elif o.spr_joint_mode=="Ball":
			return Vec3d(o.spr_joint_target_velocity_x, o.spr_joint_target_velocity_y, o.spr_joint_target_velocity_z)
		else:
			return None
	def get_spr_value(self, last):
		o = self.handler.object
		if not o.spr_joint_mode=="Spring":
			return self.handler.phJoint.GetTargetVelocity()
		else:
			return None
	def set_bpy_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Hinge" or o.spr_joint_mode=="Slider":
			o.spr_joint_target_velocity = value
		elif o.spr_joint_mode=="Ball":
			o.spr_joint_target_velocity_x = value.x
			o.spr_joint_target_velocity_y = value.y
			o.spr_joint_target_velocity_z = value.z
	def set_spr_value(self, value):
		o = self.handler.object
		if not o.spr_joint_mode=="Spring":
			pass #<!!> self.handler.phJoint.SetTargetVelocity(value)

class JointOffsetForceSync(StorableSynchronizer):
	def get_bpy_value(self, last):
		o = self.handler.object
		if o.spr_joint_mode=="Hinge" or o.spr_joint_mode=="Slider":
			return o.spr_joint_offset_force
		elif o.spr_joint_mode=="Ball":
			return Vec3d(o.spr_joint_offset_force_x, o.spr_joint_offset_force_y, o.spr_joint_offset_force_z)
		else:
			return None
	def get_spr_value(self, last):
		o = self.handler.object
		if not o.spr_joint_mode=="Spring":
			return self.handler.phJoint.GetOffsetForce()
		else:
			return None
	def set_bpy_value(self, value):
		o = self.handler.object
		if o.spr_joint_mode=="Hinge" or o.spr_joint_mode=="Slider":
			o.spr_joint_offset_force = value
		elif o.spr_joint_mode=="Ball":
			o.spr_joint_offset_force_x = value.x
			o.spr_joint_offset_force_y = value.y
			o.spr_joint_offset_force_z = value.z
	def set_spr_value(self, value):
		o = self.handler.object
		if not o.spr_joint_mode=="Spring":
			pass #<!!> self.handler.phJoint.SetOffsetForce(value)

class JointMaxForceSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.spr_joint_max_force
	def get_spr_value(self, last):
		return self.handler.phJoint.GetMaxForce()
	def set_bpy_value(self, value):
		self.handler.object.spr_joint_max_force = value
	def set_spr_value(self, value):
		self.handler.phJoint.SetMaxForce(value)







# --- --- --- --- --- --- --- --- --- --- 
# ボタンを押した際の動作

# 関節のパラメータApplyボタンを押した際の動作
class OBJECT_OT_SprJointParametersApply(bpy.types.Operator):
	bl_idname = "spr.joint_parameters_apply"
	bl_label = "[spr]Apply Joint Parameters"
	bl_description = "[Spr]"
	
	def execute(self,context):
		joint_handler = spb.handlers.joint_handlers[context.object.name]
		if joint_handler:
			joint_handler.apply_bpy_change = True
			joint_handler.sync()
		
		return{'FINISHED'}

###Limit Infinit (limit解除ボタン)
class OBJECT_OT_SprLimitInfRangeMax(bpy.types.Operator):
	bl_idname = "spr.limit_inf_range_max"
	bl_label = "[spr]Limit Inf Range Max"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		obj.spr_limit_range_max = 3e+39
		
		return{'FINISHED'}

class OBJECT_OT_SprLimitInfRangeMin(bpy.types.Operator):
	bl_idname = "spr.limit_inf_range_min"
	bl_label = "[spr]Limit Inf Range min"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		obj.spr_limit_range_min = -3e+39
		
		return{'FINISHED'}

class OBJECT_OT_SprLimitInfSwingMax(bpy.types.Operator):
	bl_idname = "spr.limit_inf_swing_max"
	bl_label = "[spr]Limit Inf Swing Max"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		obj.spr_limit_swing_max = 3e+39
		
		return{'FINISHED'}

class OBJECT_OT_SprLimitInfSwingMin(bpy.types.Operator):
	bl_idname = "spr.limit_inf_swing_min"
	bl_label = "[spr]Limit Inf Swing min"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		obj.spr_limit_swing_min = -3e+39
		
		return{'FINISHED'}

class OBJECT_OT_SprLimitInfTwistMax(bpy.types.Operator):
	bl_idname = "spr.limit_inf_twist_max"
	bl_label = "[spr]Limit Inf twist Max"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		obj.spr_limit_twist_max = 3e+39
		
		return{'FINISHED'}

class OBJECT_OT_SprLimitInfTwistMin(bpy.types.Operator):
	bl_idname = "spr.limit_inf_twist_min"
	bl_label = "[spr]Limit Inf twist min"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		obj.spr_limit_twist_min = -3e+39
		
		return{'FINISHED'}

class OBJECT_OT_SprAddJoint(bpy.types.Operator):
	bl_idname = "spr.add_joint"
	bl_label = "[spr]Add Joint"
	bl_description = "[Spr]Add Joint as Empty, Child of This Object"
	
	def execute(self,context):
		obj = context.object
		scene = context.scene
		
		obj_joint = None
		
		i = 0
		while 1:
			if "jo"+str(i)+obj.name in bpy.data.objects:
				i += 1
			else:
				obj_joint = bpy.data.objects.new("jo"+str(i)+obj.name, None)
				scene.objects.link(obj_joint)
				obj_joint.empty_draw_type = "ARROWS"
				obj_joint.parent = obj
				obj_joint.rotation_mode = "QUATERNION"
				
				obj_joint.spr_additional_joint = 1
				obj_joint.spr_joint_mode = obj.spr_joint_mode
				
				
				break
		
		return{'FINISHED'}
