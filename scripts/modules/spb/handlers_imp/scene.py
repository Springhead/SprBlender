# -*- coding: utf-8 -*-

import bpy
import spb
import bgl

from   mathutils        import Vector,Quaternion,Color
from   spb.handler      import Handler
from   spb.spbapi       import spbapi

from   Spr              import *
from   spb.synchronizer import *
from   spb.utils        import *
from   spb.scriptengine import *
from   math             import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handler
#

class SceneHandler(Handler):
	'''Spr.PHSceneとbpy.sceneを同期するクラス．'''

	def __init__(self, scene):
		Handler.__init__(self)
		self.name       = scene.name

		# Bpy Object
		self.scene      = scene

		# Spr Object
		self.fwScene    = None

		# Linked Handlers
		pass

		# Others
		self.rule       = ScriptEngine()
		self.rule.set_name("spr_script")
		self.first_step = True

		self.displist   = [5001, 5002]
		bgl.glNewList(self.displist[0], bgl.GL_COMPILE)
		bgl.glEndList()

		# -- Synchronizers
		self.gravity_sync              = SceneGravitySync(self)
		self.numiteration_sync         = SceneNumIterationSync(self)
		self.timestep_sync             = SceneTimeStepSync(self)
		self.impactthreshold_sync      = SceneImpactThresholdSync(self)
		self.frictionthreshold_sync    = SceneFrictionThresholdSync(self)
		self.contacttolerance_sync     = SceneContactToleranceSync(self)
		self.maxvelocity_sync          = SceneMaxVelocitySync(self)
		self.maxangularvelocity_sync   = SceneMaxAngularVelocitySync(self)
		self.ikisenabled_sync          = SceneIKIsEnabledSync(self)
		self.iknumiter_sync            = SceneIKNumIterSync(self)
		self.ikmaxvelocity_sync        = SceneIKMaxVelocitySync(self)
		self.ikmaxangularvelocity_sync = SceneIKMaxAngularVelocitySync(self)
		self.ikregularizeparam_sync    = SceneIKRegularizeParamSync(self)
		self.ikitercutoff_sync         = SceneIKIterCutoffSync(self)
		self.pliantisenabled_sync      = ScenePliantIsEnabledSync(self)
		self.drawsolid_sync            = SceneDrawSolidEnabledSync(self)
		self.drawlimit_sync            = SceneDrawLimitEnabledSync(self)
		self.drawik_sync               = SceneDrawIKEnabledSync(self)
		self.drawforce_sync            = SceneDrawForceEnabledSync(self)

	# --- --- --- --- ---
	# 基本クラスのオーバーライド

	def bpy(self):
		'''このハンドラが対応する（広義の）bpyオブジェクト．削除判定に使う'''
		# Sceneの場合，objectではなくsceneに対して作られるので．
		return bpy.context.scene

	def must_removed(self):
		'''このハンドラはもはや消滅すべき状態なのではないだろうかと自問する'''
		# Scene Handlerは不滅である！
		return False

	def build(self):
		self.fwScene = spbapi.GetFWSdk().GetScene(0)
		if self.fwScene is None:
			return False
		return True		

	def step(self):
		'''1ステップごとに実行する内容を記述する．Ruleの実行など'''
		if bpy.context.scene.spr_run_scripts_enabled==1 and bpy.context.scene.spr_step_enabled==1:
			self.rule.step()

		# <!!>
		for solid in self.fwScene.GetPHScene().GetSolids():
			if "Leap" in solid.GetName() and solid.NShape()>0:
				r = solid.GetShape(0).GetRadius().x
				l = solid.GetShape(0).GetLength()
				if solid.GetName() in bpy.data.objects:
					obj = bpy.data.objects[solid.GetName()]
				else:
					bpy.ops.mesh.primitive_uv_sphere_add()
					obj = bpy.context.object
					obj.name = solid.GetName()
					obj.scale = Vector((r, r, r+(l*0.5)))
					obj.rotation_mode = "QUATERNION"
					for p in obj.data.polygons:
						p.use_smooth = True
					if "Leap" in bpy.data.materials:
						obj.data.materials.append(bpy.data.materials["Leap"])
				obj.location = to_bpy(solid.GetPose().getPos())
				obj.rotation_quaternion = to_bpy(solid.GetPose().getOri())

				#for solid2 in self.fwScene.GetPHScene().GetSolids():
				#	if "Apple" in solid2.GetName():
				#		self.fwScene.GetPHScene().SetContactMode(solid, solid2, 0)

				#for wall in ["Wall1", "Wall2", "Wall3", "Wall4", "Basket1", "Basket2", "Basket3", "Basket4", "Basket5", "Basket6"]:
				#	if wall in spb.handlers.solid_handlers:
				#		soWall = spb.handlers.solid_handlers[wall].spr()
				#		self.fwScene.GetPHScene().SetContactMode(solid, soWall, 0)



	def record(self, frame):
		'''キーフレームへの記録を行う．'''
		pass
		# <!!> Virtual Baby用の一時コード
		# objects = [
		# 		bpy.data.objects['baby_Armature'].pose.bones['upper_jaw'],
		# 		bpy.data.objects['baby_Armature'].pose.bones['lower_jaw'],
		# 		]
		# for obj in objects:
		# 	spb.handlers.keys.insert(obj, frame, location=True, rotation=True)
		# 	# obj.keyframe_insert(data_path="location", frame=frame)
		# 	# if (not obj.rotation_mode=="QUATERNION"):
		# 	# 	obj.rotation_mode = "QUATERNION"
		# 	# obj.keyframe_insert(data_path="rotation_quaternion", frame=frame)

	def spr(self):
		return self.fwScene.GetPHScene() if not self.fwScene is None else None

	def spr_storable(self):
		'''Springheadの機能を利用したStore/Restoreが可能かを返す。'''
		# Leap等で剛体数が変動するのでStateによるStore/Restoreは無理
		return False

	def store_special(self, key):
		'''SpringheadのState以外に独自のStore/Restoreを定義する場合にオーバーライドする'''
		self.store_data[key] = self.fwScene.GetPHScene().GetCount()
	
	def restore_special(self, key):
		'''SpringheadのState以外に独自のStore/Restoreを定義する場合にオーバーライドする'''
		if key in self.store_data:
			count = self.store_data[key]
			self.fwScene.GetPHScene().SetCount(count)

	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		return type(object) is bpy.types.Scene

	def draw3d(self):
		'''描画を行う（３次元）'''
		if (self.fwScene is None) or (self.fwScene.GetPHScene() is None):
			return

		# --- <!!> ---
		if bpy.context.scene.spr_debug_draw_enabled==1:
			render = spbapi_cpp.GetGRRender()
			if not render is None:
				bgl.glPushAttrib(bgl.GL_ALL_ATTRIB_BITS)
				self.fwScene.DrawPHScene(render)
				bgl.glPopAttrib()
			# bgl.glCallList(self.displist[0])


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Synchronizer
#

class SceneGravitySync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.gravity
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetGravity()
	def set_bpy_value(self, value):
		bpy.context.scene.gravity = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().SetGravity(value)

class SceneNumIterationSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_num_iteration
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetNumIteration()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_num_iteration = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().SetNumIteration(value)

class SceneTimeStepSync(Synchronizer):
	def is_bpy_changed(self):
		return (abs(self.bpy - self.get_bpy_value_mod(self.bpy)) > 1e-4) if (not self.bpy is None) else True
	def is_spr_changed(self):
		return (abs(self.spr - self.get_spr_value_mod(self.bpy)) > 1e-4) if (not self.spr is None) else True
	def get_bpy_value(self, last):
		return 1/( bpy.context.scene.game_settings.frequency )
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetTimeStep()
	def set_bpy_value(self, value):
		bpy.context.scene.game_settings.frequency = 1/value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().SetTimeStep(value)

class SceneImpactThresholdSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_impact_threshold
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetImpactThreshold()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_impact_threshold = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().SetImpactThreshold(value)
		spbapi.GetPhysicsTimer().SetInterval(self.scene_handler.spr().GetTimeStep() * 1000)		

class SceneFrictionThresholdSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_friction_threshold
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetFrictionThreshold()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_friction_threshold = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().SetFrictionThreshold(value)

class SceneContactToleranceSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_contact_tolerance
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetContactTolerance()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_contact_tolerance = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().SetContactTolerance(value)

class SceneMaxVelocitySync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_max_velocity
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetMaxVelocity()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_max_velocity = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().SetMaxVelocity(value)

class SceneMaxAngularVelocitySync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_max_angular_velocity
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetMaxAngularVelocity()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_max_angular_velocity = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().SetMaxAngularVelocity(value)

class SceneIKIsEnabledSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_ik_engine_enabled
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetIKEngine().IsEnabled()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_ik_engine_enabled = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().GetIKEngine().Enable(value)

class SceneIKNumIterSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_ik_iteration_num
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().GetIKEngine().SetNumIter(value)

class SceneIKMaxVelocitySync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_ik_max_velocity
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetIKEngine().GetMaxVelocity()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_ik_max_velocity = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().GetIKEngine().SetMaxVelocity(value)

class SceneIKMaxAngularVelocitySync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_ik_max_angular_velocity
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetIKEngine().GetMaxAngularVelocity()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_ik_max_angular_velocity = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().GetIKEngine().SetMaxAngularVelocity(value)

class SceneIKRegularizeParamSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_ik_regularize_param
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetIKEngine().GetRegularizeParam()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_ik_regularize_param = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().GetIKEngine().SetRegularizeParam(value)

class SceneIKIterCutoffSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_ik_iter_cutoff_angvel
	def get_spr_value(self, last):
		return self.handler.fwScene.GetPHScene().GetIKEngine().GetIterCutOffAngVel()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_ik_iter_cutoff_angvel = value
	def set_spr_value(self, value):
		self.handler.fwScene.GetPHScene().GetIKEngine().SetIterCutOffAngVel(value)

class ScenePliantIsEnabledSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_pliant_enabled
	def get_spr_value(self, last):
		return spbapi.IsPliantEnabled()
	def set_bpy_value(self, value):
		bpy.context.scene.spr_pliant_enabled = value
	def set_spr_value(self, value):
		spbapi.EnablePliant(value)


class SceneDrawSolidEnabledSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_debug_draw_solid_enabled
	def set_spr_value(self, value):
		self.handler.fwScene.SetRenderMode(False, value)

class SceneDrawLimitEnabledSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_debug_draw_limit_enabled
	def set_spr_value(self, value):
		self.handler.fwScene.EnableRenderLimit(value)

class SceneDrawIKEnabledSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_debug_draw_ik_enabled
	def set_spr_value(self, value):
		self.handler.fwScene.EnableRenderIK(value)

class SceneDrawForceEnabledSync(Synchronizer):
	def get_bpy_value(self, last):
		return bpy.context.scene.spr_debug_draw_force_enabled
	def set_spr_value(self, value):
		self.handler.fwScene.EnableRenderForce(False, value)
