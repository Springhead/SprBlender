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

class SolidHandler(Handler):
	'''Spr.PHSolidとbpy.objectを同期するクラス．'''

	def __init__(self, object):
		Handler.__init__(self)
		self.name       = object.name

		# Bpy Object
		self.object     = object

		# Spr Object
		self.phSolid    = None
		self.phTreeNode = None

		# Linked Handlers		
		self.parent     = None
		self.children   = []

		# -- Synchronizers
		self.state_sync           = SolidStateSync(self)
		self.inertia_sync         = SolidInertiaSync(self)
		self.mass_sync            = SolidMassSync(self)
		self.com_sync             = SolidCoMSync(self)
		self.dynamical_sync       = SolidDynamicalSync(self)
		self.velocity_sync        = SolidVelocitySync(self)
		self.angularvelocity_sync = SolidAngularVelocitySync(self)
		self.force_sync           = SolidForceSync(self)
		self.torque_sync          = SolidTorqueSync(self)

		# Inertiaの変更用
		self.shape_changed = False

	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def before_sync(self):
		'''Synchronize前に行う処理を記述する．オーバーライド用．'''
		# 各PanelのHold/Applyを読み取って，対応するSynchronizerをHold/Applyする．

		# -- Solid Panel
		hold = (self.object.spr_solid_props_hold==1)
		self.state_sync.hold(hold)
		self.inertia_sync.hold(hold)
		self.mass_sync.hold(hold)
		self.com_sync.hold(hold)
		self.dynamical_sync.hold(hold)

		if (self.object.spr_solid_props_apply==1):
			self.state_sync.apply()
			self.inertia_sync.apply()
			self.mass_sync.apply()
			self.com_sync.apply()
			self.dynamical_sync.apply()

		# -- Solid Control Panel
		
		self.velocity_sync.transition(			self.object.spr_solid_velocity_edit,	self.object.spr_solid_velocity_hold,	self.object.spr_solid_velocity_apply)
		self.angularvelocity_sync.transition(	self.object.spr_solid_angvelocity_edit,	self.object.spr_solid_angvelocity_hold,	self.object.spr_solid_angvelocity_apply)
		self.force_sync.transition(				self.object.spr_solid_force_edit,		self.object.spr_solid_force_hold,		self.object.spr_solid_force_apply)
		self.torque_sync.transition(			self.object.spr_solid_torque_edit,		self.object.spr_solid_torque_hold,		self.object.spr_solid_torque_apply)
		
	def after_sync(self):
		'''Synchronize後に行う処理を記述する．オーバーライド用．'''
		# ApplyボタンをFalseにリセットする．
		self.object.spr_solid_props_apply       = 0
		self.object.spr_solid_velocity_apply    = 0
		self.object.spr_solid_angvelocity_apply = 0
		self.object.spr_solid_force_apply       = 0
		self.object.spr_solid_torque_apply      = 0

	def build(self):
		'''対応するSpringhead側オブジェクトを構築する'''
		# Create Solid
		self.phSolid = spbapi.CreateSolid()
		# Set Name
		self.phSolid.SetName("so_"+self.object.name)

		if self.phSolid is None:
			return False
		return True		

	def post_build(self):
		'''sprオブジェクト構築後に行う必要のある後処理'''
		if (self.parent is None) and (len(self.children)):
			self.phTreeNode = spbapi.GetFWSdk().GetScene(0).GetPHScene().CreateRootNode(self.phSolid);
			debuglog.log("EVENT", "Create Root Node", self.phSolid.GetName())
			for soHnd in self.children:
				soHnd.create_tree_node()
			self.phTreeNode.Enable(False) # デフォルトではABA有効にはしないでおく。<!!>あとで全体設定で変えられるようにする
		return True

	def create_tree_node(self):
		'''再帰的にTreeNodeを作成する'''
		if (not self.parent is None):
			self.phTreeNode = spbapi.GetFWSdk().GetScene(0).GetPHScene().CreateTreeNode(self.parent.phTreeNode, self.phSolid);
			debuglog.log("EVENT", "Create Tree Node", self.phSolid.GetName())
			for soHnd in self.children:
				soHnd.create_tree_node()

	def destroy(self):
		'''Springheadオブジェクトを削除する．存在しないものものを消さないように気をつけること'''
		if not self.phSolid is None:
			spbapi.RemoveSolid(self.phSolid)
			self.phSolid = None

	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		if not type(object) is bpy.types.Object:
			return False

		solid_type  = (object.spr_object_type=="Solid")
		if not solid_type:
			return False

		noparent    = (object.parent is None)
		not_pointer = (object.spr_connect_interface=="None")
		has_shape   = (not object.spr_shape_type=="None")

		if noparent:
			return not_pointer and noparent
		elif has_shape:
			name = object.name
			while not object.parent is None:
				object = object.parent
				# 剛体になるべき親が先祖のどこかにいれば，ただのShapeになるべきなのでreturn False．
				if object.spr_object_type=="Solid":
					return False
			# 親はいるがどの先祖も剛体ではない　→　Static Child
			return True

	def record(self, frame):
		'''キーフレームへの記録を行う．'''
		spb.handlers.keys.insert(self.object, frame, location=True, rotation=True)
	
	def spr(self):
		return self.phSolid
		

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class SolidStateSync(Synchronizer):
	def __init__(self, handler):
		Synchronizer.__init__(self, handler)
		self.last_stepcount = 0
		self.bpy = to_bpy([Vec3d(),Quaterniond(),Vec3d()])
		self.spr = to_spr([Vec3d(),Quaterniond(),Vec3d()])

	def is_bpy_changed(self):
		# 速度は考慮に入れない
		curr_loc, curr_rot, curr_vel = self.get_bpy_value_mod(self.bpy)
		last_loc, last_rot, last_vel = self.bpy
		return( not (curr_loc==last_loc and curr_rot==last_rot) )

	def is_spr_changed(self):
		# Sprはシミュレーションが進行していたら変更とみなす
		curr_stepcount = spbapi.GetFWSdk().GetScene(0).GetPHScene().GetCount()
		rv = (not self.last_stepcount==curr_stepcount)
		last_stepcount = curr_stepcount
		static_child = (not self.handler.object.parent is None) # Static Childはただbpyに追従するのみ．
		return (not static_child) and rv

	def get_bpy_value(self, last):
		# 回転モードをQUATERNIONに変えておく
		if (not self.handler.object.rotation_mode=="QUATERNION"):
			self.handler.object.rotation_mode = "QUATERNION"

		if ((self.handler.object.parent is None) and (not self.handler.object.spr_use_matrix_world==1)):
			# 他のobjectの子でない，かつUseMatrixWorldでない場合
			bpy_loc = self.handler.object.location
			bpy_rot = self.handler.object.rotation_quaternion
		else:
			# 他のobjectの子である(Static Child)か，UseMatrixWorldである場合
			bpy_mat = self.handler.object.matrix_world
			bpy_loc = bpy_mat.to_translation()
			bpy_rot = bpy_mat.to_quaternion()

		# Throw Mode用に速度を作っておく
		last_loc, last_rot, last_vel = last
		bpy_delta = Vector((bpy_loc.x-last_loc.x, bpy_loc.y-last_loc.y, bpy_loc.z-last_loc.z))
		if bpy_delta.x>1 or bpy_delta.y>1 or bpy_delta.z>1:
			bpy_delta = Vector((0,0,0))
		dtinv = bpy.context.scene.game_settings.frequency
		bpy_vel = Vector((bpy_delta.x*dtinv, bpy_delta.y*dtinv, bpy_delta.z*dtinv))

		return [bpy_loc, bpy_rot, bpy_vel]

	def get_spr_value(self, last):
		pose = self.handler.phSolid.GetPose()
		spr_loc = pose.getPos()
		spr_rot = pose.getOri()
		spr_vel = self.handler.phSolid.GetVelocity()
		return [spr_loc, spr_rot, spr_vel]

	def set_bpy_value(self, value):
		loc, rot, vel = value
		self.handler.object.location = loc
		self.handler.object.rotation_quaternion = rot

	def set_spr_value(self, value):
		loc, rot, vel = value
		self.handler.phSolid.SetFramePosition(loc)
		self.handler.phSolid.SetOrientation(rot)

		if bpy.context.scene.spr_throw_enabled==1 and self.handler.object.spr_solid_static==0:
			self.handler.phSolid.SetVelocity(vel)
		else:
			self.handler.phSolid.SetVelocity(Vec3d(0,0,0))

		self.handler.phSolid.SetAngularVelocity(Vec3d(0,0,0))



class SolidInertiaSync(Synchronizer):
	def is_bpy_changed(self):
		if self.handler.object.spr_autoset_inertia==1:
			return self.handler.shape_changed
		else:
			return( not self.bpy==self.get_bpy_value_mod(self.bpy) )

	def get_bpy_value(self, last):
		if self.handler.object.spr_autoset_inertia==1:
			# 慣性テンソルの自動計算
			solid = self.handler.phSolid
			volume_sum   = 0
			volume_list  = []
			center_list  = []
			inertia_list = []
			
			for i in range(0, solid.NShape()):
				shape     = solid.GetShape(i)
				shapePose = solid.GetShapePose(i)
				volume    = shape.CalcVolume()
				volume_sum += volume
				volume_list.append(volume)
				center_list.append(shapePose.getOri() * shape.CalcCenterOfMass() + shapePose.getPos())

			for i in range(0, solid.NShape()):
				shape = solid.GetShape(i)
				inertia_list.append(shape.CalcMomentOfInertia()) 
				
			if not volume_sum==0:
				density = self.handler.object.game.mass / volume_sum
				inertia = Matrix3d.Zero()
				for i in range(0, solid.NShape()):
					inertia_i = Matrix3d()
					inertia_c = inertia_list[i]
					center	  = center_list[i]
					volume	  = volume_list[i]

					inertia_i.xx = inertia_c.xx + (center.y * center.y + center.z * center.z) * volume
					inertia_i.xy = inertia_c.xy - center.x * center.y * volume
					inertia_i.xz = inertia_c.xz - center.x * center.z * volume
					inertia_i.yx = inertia_c.yx - center.y * center.x * volume
					inertia_i.yy = inertia_c.yy + (center.z * center.z + center.x * center.x) * volume
					inertia_i.yz = inertia_c.yz - center.y * center.z * volume
					inertia_i.zx = inertia_c.zx - center.z * center.x * volume
					inertia_i.zy = inertia_c.zy - center.z * center.y * volume
					inertia_i.zz = inertia_c.zz + (center.x * center.x + center.y * center.y) * volume
					inertia += inertia_i * density

			else:
				return Matrix3d() # 単位行列：体積0の場合．

		else:
			# 慣性テンソル手動設定
			inertia = Matrix3d()
			inertia.xx = self.handler.object.spr_inertia_x
			inertia.xy = self.handler.object.spr_inertia_xy
			inertia.xz = self.handler.object.spr_inertia_xz
			inertia.yx = self.handler.object.spr_inertia_yx
			inertia.yy = self.handler.object.spr_inertia_y
			inertia.yz = self.handler.object.spr_inertia_yz
			inertia.zx = self.handler.object.spr_inertia_zx
			inertia.zy = self.handler.object.spr_inertia_zy
			inertia.zz = self.handler.object.spr_inertia_z

		return inertia

	def get_spr_value(self, last):
		return self.handler.phSolid.GetInertia()

	def set_bpy_value(self, value):
		if self.handler.object.spr_autoset_inertia==1:
			self.handler.object.spr_inertia_x  = value.xx
			self.handler.object.spr_inertia_xy = value.xy
			self.handler.object.spr_inertia_xz = value.xz
			self.handler.object.spr_inertia_yx = value.yx
			self.handler.object.spr_inertia_y  = value.yy
			self.handler.object.spr_inertia_yz = value.yz
			self.handler.object.spr_inertia_zx = value.zx
			self.handler.object.spr_inertia_zy = value.zy
			self.handler.object.spr_inertia_z  = value.zz

	def set_spr_value(self, value):
		if self.handler.object.spr_autoset_inertia==1:
			self.handler.object.spr_inertia_x  = value.xx
			self.handler.object.spr_inertia_xy = value.xy
			self.handler.object.spr_inertia_xz = value.xz
			self.handler.object.spr_inertia_yx = value.yx
			self.handler.object.spr_inertia_y  = value.yy
			self.handler.object.spr_inertia_yz = value.yz
			self.handler.object.spr_inertia_zx = value.zx
			self.handler.object.spr_inertia_zy = value.zy
			self.handler.object.spr_inertia_z  = value.zz
		self.handler.phSolid.SetInertia(value)


class SolidMassSync(Synchronizer):
	def get_bpy_value(self, last):
		return self.handler.object.game.mass
	def get_spr_value(self, last):
		return self.handler.phSolid.GetMass()
	def set_bpy_value(self, value):
		self.handler.object.game.mass = value
	def set_spr_value(self, value):
		self.handler.phSolid.SetMass(value)


class SolidCoMSync(Synchronizer):
	def get_bpy_value(self, last):
		bpy_com = Vector((self.handler.object.spr_center_x, self.handler.object.spr_center_y, self.handler.object.spr_center_z))
		return bpy_com
	def get_spr_value(self, last):
		return self.handler.phSolid.GetCenterOfMass()
	def set_bpy_value(self, value):
		self.handler.object.spr_center_x = value.x
		self.handler.object.spr_center_y = value.y
		self.handler.object.spr_center_z = value.z
	def set_spr_value(self, value):
		self.handler.phSolid.SetCenterOfMass(value)


class SolidDynamicalSync(Synchronizer):
	def get_bpy_value(self, last):
		# parentがいる場合Static Childなので強制的にStatic
		bpy_dynamical = (self.handler.object.spr_solid_static==0) and (self.handler.object.parent is None)  
		return bpy_dynamical
	def get_spr_value(self, last):
		return self.handler.phSolid.IsDynamical()
	def set_bpy_value(self, value):
		if value:
			self.handler.object.spr_solid_static = 0
		else:
			self.handler.object.spr_solid_static = 1
	def set_spr_value(self, value):
		self.handler.phSolid.SetDynamical(value)


class SolidVelocitySync(Synchronizer): #<!!>
	'''
	def is_spr_changed(self):
		return False
	'''
	def get_bpy_value(self, last):
		obj = self.handler.object
		velocity = Vec3d(obj.spr_solid_velocity_x, obj.spr_solid_velocity_y, obj.spr_solid_velocity_z)
		local    = obj.spr_solid_velocity_local
		return [velocity, local]
	def get_spr_value(self,last): #<!!> Localの実装がまだ
		return self.handler.phSolid.GetVelocity()
		
	def set_spr_value(self, value):
		velocity, local = value
		return #<!!>
		if local==1:
			self.handler.phSolid.SetVelocity(self.handler.phSolid.GetPose().getOri() * velocity)
		else:
			self.handler.phSolid.SetVelocity(velocity)
	def set_bpy_value(self, value):
		self.handler.object.spr_solid_velocity_x = value.x
		self.handler.object.spr_solid_velocity_y = value.y
		self.handler.object.spr_solid_velocity_z = value.z
		

class SolidAngularVelocitySync(Synchronizer): #<!!>
	'''
	def is_spr_changed(self):
		return False
	'''
	def get_bpy_value(self, last):
		obj = self.handler.object
		angvel = Vec3d(obj.spr_solid_angular_velocity_x, obj.spr_solid_angular_velocity_y, obj.spr_solid_angular_velocity_z)
		local  = obj.spr_solid_ang_velocity_local
		return [angvel, local]
	
	def get_spr_value(self, last):
		return self.handler.phSolid.GetAngularVelocity()
		
	def set_spr_value(self, value):
		angvel, local = value
		return #<!!>
		if local==1:
			self.handler.phSolid.SetAngularVelocity(self.handler.phSolid.GetPose().getOri() * angvel)
		else:
			self.handler.phSolid.SetAngularVelocity(angvel)
	
	def set_bpy_value(self, value):
		self.handler.object.spr_solid_angular_velocity_x = value.x
		self.handler.object.spr_solid_angular_velocity_y = value.y
		self.handler.object.spr_solid_angular_velocity_z = value.z


class SolidForceSync(Synchronizer):	#<!!>
	'''
	def is_spr_changed(self):
		return False
	'''
	def get_bpy_value(self, last):
		obj = self.handler.object
		force     = Vec3d(obj.spr_solid_force_x, obj.spr_solid_force_y, obj.spr_solid_force_z)
		local     = obj.spr_solid_force_local
		point     = Vec3d(obj.spr_solid_force_point_x, obj.spr_solid_force_point_y, obj.spr_solid_force_point_z)
		use_point = obj.spr_solid_set_force_point
		return [force,local,point,use_point]
	
	def get_spr_value(self,last):	#<!!>
		return self.handler.phSolid.GetForce()
		
	def set_spr_value(self, value):
		force,local,point,use_point = value
		ori = self.handler.phSolid.GetPose().getOri()
		return #<!!>
		if use_point==1:
			if local==1:
				self.handler.phSolid.AddForce(ori*force, ori*point)
			else:
				self.handler.phSolid.AddForce(force, point)
		else:
			if local==1:
				self.handler.phSolid.AddForce(ori*force)
			else:
				self.handler.phSolid.AddForce(force)

	def set_bpy_value(self, value):
		self.handler.object.spr_solid_force_x = value.x
		self.handler.object.spr_solid_force_y = value.y
		self.handler.object.spr_solid_force_z = value.z


class SolidTorqueSync(Synchronizer):	#<!!>
	'''
	def is_spr_changed(self):
		return False
	'''
	def get_bpy_value(self, last):
		obj = self.handler.object
		torque     = Vec3d(obj.spr_solid_torque_x, obj.spr_solid_torque_y, obj.spr_solid_torque_z)
		local     = obj.spr_solid_torque_local
		return [torque,local]
	
	def get_spr_value(self, last):
		return self.handler.phSolid.GetTorque()
		
	def set_spr_value(self, value):
		torque,local = value
		ori = self.handler.phSolid.GetPose().getOri()
		return #<!!>
		if local==1:
			self.handler.phSolid.AddTorque(ori*torque)
		else:
			self.handler.phSolid.AddTorque(torque)

	def set_bpy_value(self, value):
		self.handler.object.spr_solid_torque_x = value.x
		self.handler.object.spr_solid_torque_y = value.y
		self.handler.object.spr_solid_torque_z = value.z

