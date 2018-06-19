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
# Utility Functions
# 

def get_roundcone_param(obj1):
	child = False
	if obj1.spr_roundcone_target_name in bpy.data.objects:
		obj2 = bpy.data.objects[obj1.spr_roundcone_target_name]
	elif len(obj1.children) > 0:
		obj2 = obj1.children[0]
		child = True
	else:
		return None

	s1 = obj1.scale
	r1 = (s1[0]+s1[1]+s1[2])/3

	s2 = obj2.scale
	if child:
		s2 = obj2.matrix_parent_inverse.to_3x3() * s2
	r2 = (s2[0]+s2[1]+s2[2])/3
	if child:
		r2 = r1 * r2

	relpos = bpy_object_pose(obj2).translation - bpy_object_pose(obj1).translation
	center = relpos * 0.5
	length = relpos.length

	if (center.length > 1e-3):
		qtn = Quaterniond()
		qtn.RotationArc(Vec3d(0,0,1), to_spr(center).unit())
		mat = to_bpy(Posed(Vec3d(), qtn))
	else:
		mat = Matrix()

	return [r1, r2, length, mat, center]


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handler
#

class ShapeHandler(Handler):
	'''Spr.CDShapeとbpy.objectを同期するクラス．'''

	def __init__(self, object):
		Handler.__init__(self)
		self.name     = object.name

		# Bpy Object
		self.object   = object

		# Spr Object
		self.cdShape  = None

		# -- Synchronizers
		self.pose_sync           = ShapePoseSync(self)
		self.dimension_sync      = ShapeDimensionSync(self)
		self.elasticity_sync     = ShapeElasticitySync(self)
		self.friction_sync       = ShapeFrictionSync(self)
		self.staticfriction_sync = ShapeStaticFrictionSync(self)

	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def before_sync(self):
		'''Synchronize前に行う処理を記述する．オーバーライド用．'''
		# 各PanelのHold/Applyを読み取って，対応するSynchronizerをHold/Applyする．

		# -- Solid Panel
		hold = (self.object.spr_solid_props_hold==1)
		self.elasticity_sync.hold(hold)
		self.friction_sync.hold(hold)
		self.staticfriction_sync.hold(hold)

		if (self.object.spr_solid_props_apply==1):
			self.elasticity_sync.apply()
			self.friction_sync.apply()
			self.staticfriction_sync.apply()

	def after_sync(self):
		'''Synchronize後に行う処理を記述する．オーバーライド用．'''
		# ApplyボタンをFalseにリセットする．
		self.object.spr_solid_props_apply = 0

	def update_build_info(self):
		'''Springheadオブジェクトの構築に必要な情報を更新。これが変化すると再構築される。
		ビルドに必要な情報がすべて出揃った場合のみTrueを返すこと'''

		self.build_info["shapetype"] = self.object.spr_shape_type

		return True

	def update_dependency(self):
		'''依存関係を更新。これが変化すると再構築される。
		ビルドに必要な依存ハンドラがすべて出揃った場合のみTrueを返すこと'''
		try:
			# 形状適用先Solid ： 親階層を辿って最後に見つかったSolidHandler
			o = self.object
			target = o
			while (not o.parent is None):
				o = o.parent
				if not spb.handlers.solid_handlers[o.name] is None:
					target = o
			self.dependency["solid"] = spb.handlers.solid_handlers[target.name]

		except (AttributeError, KeyError):
			return False

		return True

	def build(self):
		'''対応するSpringhead側オブジェクトを構築する．依存ハンドラの取得も行う．'''
		# Info
		shapetype = self.build_info["shapetype"]
		solid     = self.dependency["solid"    ]

		# Create Shape
		if shapetype == "Sphere":
			sphereDesc = CDSphereDesc()
			dim = self.object.dimensions
			radius = (dim.x + dim.y + dim.z) / 3 / 2
			sphereDesc.radius = float(radius)
			self.cdShape = spbapi.GetFWSdk().GetPHSdk().CreateShape(CDSphere.GetIfInfoStatic(), sphereDesc)

		if shapetype == "Box":
			boxDesc = CDBoxDesc()
			dim = self.object.dimensions
			boxDesc.boxsize = Vec3d(dim.x, dim.y, dim.z)
			self.cdShape = spbapi.GetFWSdk().GetPHSdk().CreateShape(CDBox.GetIfInfoStatic(), boxDesc)

		if shapetype == "RoundCone":
			rcDesc = CDRoundConeDesc()
			rv = get_roundcone_param(self.object)
			if rv:
				r1, r2, length, mat, center = rv
				rcDesc.length = length
				rcDesc.radius = Vec2f(r1, r2)
				self.cdShape = spbapi.GetFWSdk().GetPHSdk().CreateShape(CDRoundCone.GetIfInfoStatic(), rcDesc)

		if shapetype == "Convex":
			convexDesc = CDConvexMeshDesc()
			v_vec3d = []
			for v in self.object.data.vertices:
				scale = self.object.scale
				v_vec3d.append(Vec3d(v.co.x*scale.x, v.co.y*scale.y, v.co.z*scale.z))
			convexDesc.vertices = v_vec3d
			self.cdShape = spbapi.GetFWSdk().GetPHSdk().CreateShape(CDConvexMesh.GetIfInfoStatic(), convexDesc)

		if self.cdShape is None:
			debuglog.log("ERROR", "Error : Error on Creating Shape <!!> "+self.name+" ... "+str(self.build_info)+", "+str(self.dependency))
			return

		# Set Shape to Solid
		debuglog.log("MINOR_EVENT", "Set Shape : ", self.name)
		solid.spr().AddShape(self.cdShape)

		# Set Name
		self.cdShape.SetName("cd_"+self.object.name)

		if self.cdShape is None:
			return False
		return True		


	def destroy(self):
		if (not self.cdShape is None) and (not self.dependency["solid"].spr() is None):
			#self.cdShape.SetName("cd_removed_shape_"+self.object.name)
			self.dependency["solid"].spr().RemoveShape(self.cdShape)
			spbapi.GetFWSdk().GetPHSdk().DelChildObject(self.cdShape)
			self.cdShape = None


	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		if not type(object) is bpy.types.Object:
			return False
		solid_type  = (object.spr_object_type=="Solid")
		has_shape   = (not object.spr_shape_type=="None")
		return solid_type and has_shape

	def spr(self):
		return self.cdShape

	def spr_storable(self):
		return False


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class ShapePoseSync(Synchronizer):
	def __init__(self, handler):
		Synchronizer.__init__(self, handler)
		self.bpy = to_bpy([None, None])
		self.spr = to_spr([None, None])

	def is_bpy_changed(self):
		last_relative = self.bpy
		mat_relative  = self.get_bpy_value_mod(self.bpy)

		if mat_relative is None or last_relative is None:
			return True

		mat_diff     = mat_relative - last_relative
		mat_diff_abs = 0
		for i in range(0,4):
			for j in range(0,4):
				mat_diff_abs += abs(mat_diff[i][j])

		return mat_diff_abs > 1e-5

	def is_spr_changed(self):
		# あとで実装
		return False

	def get_bpy_value(self, last):
		# -- 親子それぞれのWorld座標から，相対変換を求める --
		mat_child    = bpy_object_pose(self.handler.object)
		mat_parent   = bpy_object_pose(self.handler.dependency["solid"].object)
		mat_relative = mat_parent.inverted() * mat_child

		# RoundConeの場合はちょっと特殊処理
		if self.handler.build_info["shapetype"] == "RoundCone":
			rv = get_roundcone_param(self.handler.object)
			if rv:
				r1, r2, length, mat, center = rv
				mat_relative = mat_relative * mat
				mat_relative.translation += center

			# <!!>
			if bpy.context.scene.spr_step_enabled:
				mat_relative = last

		return mat_relative

	def get_spr_value(self, last):
		# あとで実装
		return None

	def set_bpy_value(self, value):
		# あとで実装
		pass

	def set_spr_value(self, value):
		solidHnd = self.handler.dependency["solid"]
		if solidHnd is None or solidHnd.phSolid is None:
			return
		
		# Shape番号を探してきてSetShapePoseする
		mat_relative = value
		for i in range(0, solidHnd.phSolid.NShape()):
			if solidHnd.phSolid.GetShape(i)==self.handler.cdShape:
				solidHnd.phSolid.SetShapePose(i, mat_relative)

		# Solidハンドラに形状に変化があったことを伝える　→　慣性テンソルの再計算が行われる．
		solidHnd.shape_changed = True
		

class ShapeDimensionSync(Synchronizer):
	def is_bpy_changed(self):
		'''bpyの新しい値を取得して，変更があったかを返す'''
		if self.handler.build_info["shapetype"] == "Convex": # <!!>
			old = self.bpy
			new = self.get_bpy_value_mod(self.bpy)
			if not len(old)==len(new):
				return True
			for i in range(0, len(new)):
				if (old[i]-new[i]).length > 1e-4:
					debuglog.log("EVENT", "Shape Changed! : ", self.handler.name)
					return True
			return False
		else:
			old = self.bpy
			new = self.get_bpy_value_mod(self.bpy)
			return( (old-new).length > 1e-4 )

	def is_spr_changed(self):
		# あとで実装
		return False

	def get_bpy_value(self, last):
		if self.handler.build_info["shapetype"] == "Convex": # <!!>
			vert = []
			for v in self.handler.object.data.vertices:
				vert.append(v.co)
			return vert
		elif self.handler.build_info["shapetype"] == "RoundCone":
			rv = get_roundcone_param(self.handler.object)
			if rv:
				r1, r2, length, mat, center = rv
				# <!!>
				if bpy.context.scene.spr_step_enabled:
					return last
				else:
					return Vector((r1,r2,length))
			else:
				return last
		else:
			return self.handler.object.dimensions

	def set_spr_value(self, value):
		changed = False
		if self.handler.build_info["shapetype"] == "Sphere":
			radius = (value.x + value.y + value.z) / 3 / 2
			self.handler.cdShape.SetRadius(radius)
			changed = True
		if self.handler.build_info["shapetype"] == "Box":
			boxsize = Vec3d(value.x, value.y, value.z)
			self.handler.cdShape.SetBoxSize(boxsize)
			changed = True
		if self.handler.build_info["shapetype"] == "Convex": # <!!>
			self.handler.destroy()
			self.handler.build()
			self.handler.pose_sync.sync_bpy_to_spr()
			changed = True
		if self.handler.build_info["shapetype"] == "RoundCone":			
			self.handler.cdShape.SetLength(value.z)
			self.handler.cdShape.SetRadius(Vec2f(value.x, value.y))
			changed = True

		# 形状に変更があった場合
		if changed:
			# Solidハンドラに形状に変化があったことを伝える　→　慣性テンソルの再計算が行われる．
			solidHnd = self.handler.dependency["solid"]
			if solidHnd is None or solidHnd.phSolid is None:
				return
			solidHnd.shape_changed = True
			# BoundingBoxを再計算する
			solidHnd.phSolid.GetBBox(Vec3d(0.001,0.001,0.001), Vec3d(9999,9999,9999), True)

class ShapeElasticitySync(Synchronizer):
	def get_bpy_value(self, last):
		mat = self.handler.object.material_slots.id_data.active_material
		return mat.physics.elasticity if (not mat is None) else self.handler.cdShape.GetElasticity()
	def get_spr_value(self, last):
		return self.handler.cdShape.GetElasticity()
	def set_bpy_value(self, value):
		mat = self.handler.object.material_slots.id_data.active_material
		if not mat is None:
			mat.physics.elasticity = value
	def set_spr_value(self, value):
		self.handler.cdShape.SetElasticity(value)


class ShapeFrictionSync(Synchronizer):
	def get_bpy_value(self, last):
		mat = self.handler.object.material_slots.id_data.active_material
		return mat.physics.friction if (not mat is None) else self.handler.cdShape.GetDynamicFriction()
	def get_spr_value(self, last):
		return self.handler.cdShape.GetDynamicFriction()
	def set_bpy_value(self, value):
		mat = self.handler.object.material_slots.id_data.active_material
		if not mat is None:
			mat.physics.friction = value
	def set_spr_value(self, value):
		self.handler.cdShape.SetDynamicFriction(value)


class ShapeStaticFrictionSync(Synchronizer):
	def get_bpy_value(self, last):
		mat = self.handler.object.material_slots.id_data.active_material
		return mat.spr_friction_static if (not mat is None) else self.handler.cdShape.GetStaticFriction()
	def get_spr_value(self, last):
		return self.handler.cdShape.GetStaticFriction()
	def set_bpy_value(self, value):
		mat = self.handler.object.material_slots.id_data.active_material
		if not mat is None:
			mat.spr_friction_static = value
	def set_spr_value(self, value):
		self.handler.cdShape.SetStaticFriction(value)
