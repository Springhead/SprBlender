# -*- coding: utf-8 -*-

import bpy
import spb

from   Spr              import *
from   spb.synchronizer import *
from   spb.utils        import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# SprOperatorパネルのレイアウト
#

class SprBlenderInfoPanel(bpy.types.Panel):
	bl_label = "SprBlender Info"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"

	def draw(self, context):
		layout = self.layout
		scene = context.scene

		layout.label("Frame Rate")
		layout.prop(scene, "spr_op_cps_count",     text="Operator", emboss=False)
		layout.prop(scene, "spr_phys_cps_count",   text="Physics",  emboss=False)


class SprOperatorPanel(bpy.types.Panel):
	bl_label = "SprBlender"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		
		col = layout.column(align=True)
		col.label(text="Simulation:")

		row = col.row(align=True)
		if scene.spr_step_enabled==0:
			if spb.simulation_started:
				text = "ReStart"
				row.alert = True
			else:
				row.alert = False
				text = "Start"
			icon = "PLAY"
		else:
			row.alert = True
			text = "Pause"
			icon = "PAUSE"
		row.prop(scene, "spr_step_enabled", text=text, icon=icon)
		col.operator("spr.stop_simulation", text="Stop", icon = "MESH_PLANE")

		row = col.row(align=True)
		row.operator("spr.quickrestore_to_started", text="Back", icon = "REW")
		row.operator("spr.quickrestore_to_ended",   text="End", icon = "FF")

		col.operator("spr.one_step",text = "One Step" ,icon="FRAME_NEXT")
		
		col = layout.column(align=True)
		col.prop(scene, "spr_record", text = "Record", icon="REC")
		if scene.spr_record:
			col.prop(scene, "spr_recording_frame", text = "Frame")
			col.prop(scene, "spr_record_every_n_steps", text = "Rec Per Step")

			row = col.row(align=True)
			row.prop(scene, "spr_record_to_cache", text = "Use Cache", toggle=True)
			if scene.spr_record_to_cache:
				row.operator("spr.bake_keyframes",text = "Bake")

			# col.prop(scene, "spr_step_frame", text = "Step Frame No.")
			# col.prop(scene, "spr_sync_current_frame", text = "Sync Current Frame")

		# --
		
		col = layout.column(align=True)
		col.label(text="Restore / Store:")
		col.operator("spr.restore",text = "Restore Scene", icon="RECOVER_LAST")

		col = layout.column(align=True)
		col.operator("spr.store",text = "Store Scene")
		
		# --
		
		col = layout.column(align=True)
		col.label(text="Rebuild:")
		col.operator("spr.rebuild",text = "Rebuild Scene", icon="SCENE_DATA")

		# --
		
		col = layout.column(align=True)
		col.label(text = "Enable Functions:")

		row = col.row(align=True)
		row.prop(scene, "spr_minimal_sync",      text = "Minimal Sync")
		row.operator("spr.synchronize",text = "Sync")

		col.prop(scene, "spr_throw_enabled",     text = "Throw")
		col.prop(scene, "spr_ik_engine_enabled", text = "IK Engine")
		col.prop(scene, "spr_pliant_enabled",    text = "Pliant")

		row = col.row(align=True)
		row.prop(scene, "spr_run_scripts_enabled", text = "Script")
		row.operator("spr.update_scripts",text = "Update")

		row = col.row(align=True)
		row.prop(scene, "spr_creature_enabled",     text = "Creature")
		row.operator("spr.update_creature_scripts", text = "Update")

		# show_icons(layout)


class SprBlenderAdvancedPanel(bpy.types.Panel):
	bl_label = "SprBlender Advanced"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		col = layout.column()
		col.prop(scene, "spr_use_object_wrapper", text = "Assure Availability")
		col.operator("spr.calibrate_spidar",      text = "Calibrate SPIDAR")
		col.operator("spr.generate_creature",     text = "Generate Creature")
		col.operator("spr.link_solid_and_bone",   text = "Link Solid & Bone")
		if scene.spr_need_migration==1:
			col.operator("spr.migration",text = "Migration 2.0")
		# col.operator("spr.migration_limit",text = "Migration Limit")
		col.prop(scene, "spr_debug_draw_enabled", text = "Debug Draw")
		if scene.spr_debug_draw_enabled:
			col.prop(scene, "spr_debug_draw_solid_enabled", text = "Solid")
			col.prop(scene, "spr_debug_draw_limit_enabled", text = "Joint")
			col.prop(scene, "spr_debug_draw_ik_enabled",    text = "IK")
			col.prop(scene, "spr_debug_draw_force_enabled", text = "Force")

class SprBlenderOptimizePanel(bpy.types.Panel):
	bl_label = "Pitch Optimize"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	def draw(self,context):
		layout = self.layout
		scene = context.scene
		obj = context.object
		
		col = layout.column(align=True)
		col.label(text = "Input Pitch:")
		row = col.row(align=True)
		row.operator("spr.pitch_optimization", text="START", icon="REC")
		
		split = layout.split()
		row = split.row()
		row.prop(obj, "load_to_trajectory", text="")
		
		layout.prop(obj,"volume_level_set", text="Set Volume level")
		layout.prop(scene,"modify_trajectory_by_pitch", text="Pitch Trajectory")
		
		split = layout.split()
		row = split.row()
		row.prop(scene, "trajectory_scale_enabled",     text = "trajectory_scale:")
		row.prop(obj,"trajectory_scale", text="")
		
# --- --- --- --- --- --- --- --- --- --- 
# ボタンを押した際の動作

class OBJECT_OT_PitchOptimization(bpy.types.Operator):
	bl_idname = "spr.pitch_optimization"
	bl_label  = "[spr]Call Recording Pitch"
	bl_description = "[spr]Call Recording."
	
	def execute(self,context):
		
		#stop→back→recording(optimization→update→start)
		#stop
		spb.simulation_started = False
		bpy.context.scene.spr_step_enabled = 0
		#back
		spb.handlers.restore("quickstore_on_start")
		#optimize
		rec = spb.pitch.spectrum_analyzer.Thread_record(context.object.volume_level_set)
		rec.start()
		
		return{'FINISHED'}

class OBJECT_OT_SprOneStep(bpy.types.Operator):
	bl_idname = "spr.one_step"
	bl_label = "[spr]Call One Step"
	bl_description = "[Spr]Call ONE physics step."
	
	def execute(self,context):
		spb.spbapi.OneStep()
		spb.handlers.creature_bpy_rule()
		spb.handlers.store("quickstore_on_end")
		spb.handlers.minimal_sync()
		
		return{'FINISHED'}

class OBJECT_OT_SprStopSimulation(bpy.types.Operator):
	bl_idname = "spr.stop_simulation"
	bl_label = "[spr]Stop Simulation"
	bl_description = "[Spr]Stop Simulation."
	
	def execute(self,context):
		spb.simulation_started = False
		context.scene.spr_step_enabled = 0
		
		return{'FINISHED'}

class OBJECT_OT_SprBakeKeyframes(bpy.types.Operator):
	bl_idname = "spr.bake_keyframes"
	bl_label = "[spr]Bake Keyframes"
	bl_description = "[Spr]Bake Cached Keyframes into Blender Keys."
	
	def execute(self,context):
		spb.handlers.bake_frame = 0
		spb.handlers.bake_mode  = True
		
		return{'FINISHED'}

class OBJECT_OT_SprStore(bpy.types.Operator):
	bl_idname = "spr.store"
	bl_label = "[spr]Store scene"
	bl_description = "[Spr]Store pose of objects in the scene."
	
	def execute(self,context):
		spb.handlers.store("default")
		
		return{'FINISHED'}

class OBJECT_OT_SprRestore(bpy.types.Operator):
	bl_idname = "spr.restore"
	bl_label = "[spr]Restore scene"
	bl_description = "[Spr]Restore pose of objects in the scene to stored state."
	
	def execute(self,context):
		spb.handlers.restore("default")
		
		return{'FINISHED'}
		
class OBJECT_OT_SprQuickRestoreToStarted(bpy.types.Operator):
	bl_idname = "spr.quickrestore_to_started"
	bl_label = "[spr] Quick Restore (started)"
	bl_description = "[Spr]Restore Scene to the state before simulation started."
	
	def execute(self,context):
		spb.handlers.restore("quickstore_on_start")
		
		return{'FINISHED'}

class OBJECT_OT_SprQuickRestoreToEnded(bpy.types.Operator):
	bl_idname = "spr.quickrestore_to_ended"
	bl_label = "[spr] Quick Restore (stopped)"
	bl_description = "[Spr]Restore Scene to the state after simulation stopped."
	
	def execute(self,context):
		spb.handlers.restore("quickstore_on_end")
		
		return{'FINISHED'}

class OBJECT_OT_SprRebuild(bpy.types.Operator):
	bl_idname = "spr.rebuild"
	bl_label = "[spr]Rebuild scene"
	bl_description = "Clear Springhead Scene and Rebuild from bpy scene."
	
	def execute(self,context):
		spb.handlers.operation = False

		# ハンドラの初期化
		spb.handlers.clear()
		# Springheadの初期化
		spb.spbapi.Init()

		spb.handlers.operation = True
		
		return{'FINISHED'}

class OBJECT_OT_SPBSynchronize(bpy.types.Operator):
	bl_idname = "spr.synchronize"
	bl_label = "[spr]Synchronize Step"
	bl_description = "[Spr]Synchronize Step"
	
	def execute(self,context):
		spb.handlers.full_step()
		
		return{'FINISHED'}

class OBJECT_OT_UpdateCreatureScripts(bpy.types.Operator):
	bl_idname = "spr.update_creature_scripts"
	bl_label = "[spr]Update Creature Scripts"
	bl_description = "[Spr]Update creature scripts."
	
	def execute(self,context):
		for creature_handler in spb.handlers.creature_handlers.values():
			creature_handler.rule.update()
			creature_handler.rule.init()
		
		return{'FINISHED'}

class OBJECT_OT_UpdateScripts(bpy.types.Operator):
	bl_idname = "spr.update_scripts"
	bl_label = "[spr]Update Scripts"
	bl_description = "[Spr]Update user scripts."
	
	def execute(self,context):
		spb.handlers.scene_handler.rule.update()
		spb.handlers.scene_handler.rule.init()
		
		return{'FINISHED'}

class OBJECT_OT_SprCalibrateSpidar(bpy.types.Operator):
	bl_idname = "spr.calibrate_spidar"
	bl_label = "[spr]Calibrate SPIDAR"
	bl_description = "[Spr]Calibrate SPIDAR."
	
	def execute(self,context):
		spbapi.GetSPIDAR(0).Calibration()
		spbapi.GetSPIDAR(1).Calibration()
		
		return{'FINISHED'}

class OBJECT_OT_SprGenerateCreature(bpy.types.Operator):
	bl_idname = "spr.generate_creature"
	bl_label = "[spr]Generate Creature"
	bl_description = "[Spr]Generate Creature."
	
	def execute(self,context):
		if not type(bpy.context.object.data) is bpy.types.Armature:
			return{'FINISHED'}

		armature = bpy.context.object

		for root in [x for x in armature.data.bones if x.parent is None]:
			so, jo = create_solid_joint(armature, root)
			so.spr_solid_static = True

		return{'FINISHED'}


class OBJECT_OT_SprLinkSolidAndBone(bpy.types.Operator):
	bl_idname = "spr.link_solid_and_bone"
	bl_label = "[spr]Link Solid And Bone."
	bl_description = "[Spr]Link Solid And Bone.."
	
	def execute(self,context):
		if not type(bpy.context.object.data) is bpy.types.Armature:
			return{'FINISHED'}

		armature = bpy.context.object
		link_solid_and_bone(armature)

		return{'FINISHED'}


class OBJECT_OT_SprMigration(bpy.types.Operator):
	bl_idname = "spr.migration_limit"
	bl_label = "[spr]Migration Joint Limit Range"
	bl_description = "Migrate Joint Limit"
	
	def execute(self,context):
		for obj in bpy.data.objects:
			if obj.spr_limit_range_min > 3e+30:
				obj.spr_limit_range_min = -3e+39
			if obj.spr_limit_swing_min > 3e+30:
				obj.spr_limit_swing_min = -3e+39
			if obj.spr_limit_twist_min > 3e+30:
				obj.spr_limit_twist_min = -3e+39

		return{'FINISHED'}

class OBJECT_OT_SprMigration(bpy.types.Operator):
	bl_idname = "spr.migration"
	bl_label = "[spr]Migration to SprBlender 2.0"
	bl_description = "Migrate Properties Definition into SprBlender 2.0 style."
	
	def execute(self,context):
		for obj in bpy.data.objects:
			# Make Joint
			# Jointなのにchildに p_ が存在しない場合は，追加してrotation_quaternion, locationをコピっておく
			if (not obj.spr_joint_type=="None" and obj.spr_additional_joint==0):
				found=False
				for child in obj.children:
					if child.name==("p_"+obj.name):
						found=True
				if not found:
					obj_jo = bpy.data.objects.new("p_"+obj.name, None)
					context.scene.objects.link(obj_jo)
					obj_jo.empty_draw_type = "ARROWS"
					obj_jo.parent = obj
					obj_jo.show_x_ray = True
					bpy.ops.object.select_all(action='DESELECT')
					obj_jo.select = True
					bpy.ops.object.parent_clear(type="CLEAR_INVERSE")
					obj_jo.rotation_mode="QUATERNION"
					##plugオブジェクトが無くても機能してるjointは存在するので
					#obj_jo.rotation_quaternion = Quaternion((1,0,0,0))
					#obj_jo.location = Vector((0,0,0))
					obj_jo.location = Vector((obj.spr_joint_plug_pos_x, obj.spr_joint_plug_pos_y, obj.spr_joint_plug_pos_z))
					obj_jo.rotation_quaternion = Quaternion((obj.spr_joint_plug_ori_w, obj.spr_joint_plug_ori_x, obj.spr_joint_plug_ori_y, obj.spr_joint_plug_ori_z))

		for obj in bpy.data.objects:
			# Solid
			if obj.spr_physics_type=="Dynamic" or (not obj.spr_shape_type=="None"):
				obj.spr_object_type     = "Solid"
				obj.spr_solid_static    = 1 if (obj.spr_physics_type=="Static") else 0
				obj.spr_autoset_inertia = (not obj.spr_inertia_manual_setting_enabled)

			# Joint
			if (not obj.parent is None) and (("p_" + obj.parent.name) == obj.name) or (obj.spr_additional_joint==1):
				obj.spr_object_type         = "Joint"
				obj.spr_joint_socket_target = "Solid Name"

				if obj.spr_additional_joint==0:
					object = obj.parent
				else:
					object = obj

				# オブジェクトが違う（かもしれない）のでJointのプロパティは全部コピる必要がある
				obj.spr_joint_mode      = object.spr_joint_type
				obj.spr_joint_enabled   = object.spr_joint_enabled
				obj.spr_spring          = object.spr_spring
				obj.spr_damper          = object.spr_damper
				obj.spr_joint_max_force = object.spr_joint_max_force
				obj.spr_joint_collision = object.spr_joint_collision

				obj.spr_joint_socket_target_name = object.spr_joint_target
				obj.hide_select = False

				if object.spr_joint_type=="Ball":
					if (object.spr_limit_swing_min < 3e+38) or (object.spr_limit_swing_max < 3e+38):
						obj.spr_joint_limit_enable = True
						obj.spr_limit_swing_min = object.spr_limit_swing_min
						obj.spr_limit_swing_max = object.spr_limit_swing_max
					if (object.spr_limit_twist_min < 3e+38) or (object.spr_limit_twist_max < 3e+38):
						obj.spr_joint_limit_enable = True
						obj.spr_limit_twist_min = object.spr_limit_twist_min
						obj.spr_limit_twist_max = object.spr_limit_twist_max

				if object.spr_joint_type=="Hinge" or object.spr_joint_type=="Slider":
					if (object.spr_limit_range_min < 3e+38) or (object.spr_limit_range_max < 3e+38):
						obj.spr_joint_limit_enable = True
						obj.spr_limit_range_min = object.spr_limit_range_min
						obj.spr_limit_range_max = object.spr_limit_range_max

				obj.spr_limit_spring = object.spr_limit_spring
				obj.spr_limit_damper = object.spr_limit_damper

				obj.spr_joint_target_position   = object.spr_joint_target_position
				obj.spr_joint_target_position_x = object.spr_joint_target_position_x
				obj.spr_joint_target_position_y = object.spr_joint_target_position_y
				obj.spr_joint_target_position_z = object.spr_joint_target_position_z

				obj.spr_joint_target_velocity   = object.spr_joint_target_velocity
				obj.spr_joint_target_velocity_x = object.spr_joint_target_velocity_x
				obj.spr_joint_target_velocity_y = object.spr_joint_target_velocity_y
				obj.spr_joint_target_velocity_z = object.spr_joint_target_velocity_z

				obj.spr_joint_offset_force      = object.spr_joint_offset_force
				obj.spr_joint_offset_force_x    = object.spr_joint_offset_force_x
				obj.spr_joint_offset_force_y    = object.spr_joint_offset_force_y
				obj.spr_joint_offset_force_z    = object.spr_joint_offset_force_z

				obj.spr_ik_enabled              = object.spr_ik_enabled
				obj.spr_ik_bias                 = object.spr_ik_bias

		for obj in bpy.data.objects:
			# Solid
			if obj.spr_physics_type=="Dynamic" or (not obj.spr_shape_type=="None"):
				obj.spr_ik_enabled      = obj.spr_ik_end_effector

		return{'FINISHED'}



# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# SprSceneパネルのレイアウト
#

class SprScenePanel(bpy.types.Panel):
	bl_label       = "Springhead Scene Settings"
	bl_space_type  = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context     = "scene"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		
		layout.prop(scene, "gravity")
		
		split = layout.split()
		split.label(text="Physics Frame Rate")
		split.prop(scene.game_settings, "frequency", text="FPS", slider=False)

		split = layout.split()
		split.label(text="LCP Num Iteration (default=15)")
		split.prop(scene, "spr_num_iteration", text="NumIteration", slider=False)
		
		split = layout.split()
		split.label(text="Impact Threshold (default=10.0)")
		split.prop(scene, "spr_impact_threshold", text="ImpactThreshold")
		
		split = layout.split()
		split.label(text="Friction Threshold (default=0.01)")
		split.prop(scene, "spr_friction_threshold", text="FrictionThreshold")
		
		split = layout.split()
		split.label(text="Contact Tolerance (default=0.002)")
		split.prop(scene, "spr_contact_tolerance", text="ContactTolerance")
		
		split = layout.split()
		split.label(text="Max Velocity (default=Inf)")
		split.prop(scene, "spr_max_velocity", text="MaxVelocity")
		
		split = layout.split()
		split.label(text="Max Angular Velocity (default=100)")
		split.prop(scene, "spr_max_angular_velocity", text="MaxAngularVelocity")

		# --- IK

		split = layout.split()
		split.label(text="IK Num Iteration (default=1)")
		split.prop(scene, "spr_ik_iteration_num", text="IKNumIteration")

		split = layout.split()
		split.label(text="IK Max Velocity (default=20)")
		split.prop(scene, "spr_ik_max_velocity", text="IKMaxVelocity")
		
		split = layout.split()
		split.label(text="IK Max Angular Velocity (default=10)")
		split.prop(scene, "spr_ik_max_angular_velocity", text="IKMaxAngularVelocity")

		split = layout.split()
		split.label(text="IK Regularize Parameter (default=0.7)")
		split.prop(scene, "spr_ik_regularize_param", text="IKRegularizeParam")

		split = layout.split()
		split.label(text="IK Iter Cutoff (default=0.01)")
		split.prop(scene, "spr_ik_iter_cutoff_angvel", text="IKIterCutOffAngvel")

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# SprObjectパネルのレイアウト
#

class SprPhysicsPanel(bpy.types.Panel):
	bl_label	   = "Springhead Physics"
	bl_space_type  = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context	   = "object"

	def draw(self, context):
		layout = self.layout
		obj	   = context.object
		mat	   = obj.material_slots.id_data.active_material

		# -- 
		split = layout.split()
		row = split.row()
		row.prop(obj, "spr_object_type", text="")

		if obj.spr_object_type=="Solid":
			row = split.row(align=True)
			row.prop(obj, "spr_solid_props_hold", text="Hold", icon=("PINNED" if obj.spr_solid_props_hold else "UNPINNED"))
			if obj.spr_solid_props_hold==1:
				row.prop(obj, "spr_solid_props_apply", text="Apply", toggle=True)

			self.draw_solid(context)

		elif obj.spr_object_type=="Joint":
			row = split.row(align=True)
			row.prop(obj, "spr_joint_props_hold", text="Hold", icon=("PINNED" if obj.spr_joint_props_hold else "UNPINNED"))
			if obj.spr_joint_props_hold==1:
				row.prop(obj, "spr_joint_props_apply", text="Apply", toggle=True)

			self.draw_joint(context)
		

	def draw_solid(self, context):
		layout = self.layout
		obj	   = context.object
		mat	   = obj.material_slots.id_data.active_material

		# -- 
		split = layout.split()
		row1 = split.column()
		row1.prop(obj, "spr_shape_type",   text="Shape")
		if obj.spr_shape_type=="RoundCone":
			row1.prop(obj, "spr_roundcone_target_name", text="Target")
		row2 = split.row()
		row2.operator("spr.shape_renew",   text="Renew")
		row2.prop(obj, "spr_solid_static", text="Static Solid")
		
		# -- 
		split = layout.split()
		col = split.column()
		col.prop(obj.game, "mass",             text="Mass")

		col2 = col.column(align=True)
		col2.label(text="Center of Mass")
		col2.prop(obj, "spr_center_x", text="x")
		col2.prop(obj, "spr_center_y", text="y")
		col2.prop(obj, "spr_center_z", text="z")
		col2.operator("spr.solid_center_from_cursor", "From Cursor")
				
		# -- 
		col = split.column()
		col.label(text="Material:")
		if (not mat==None):
			col.prop(mat.physics, "elasticity",          text="Elasticity")
			col.prop(mat.physics, "friction",            text="Friction")
			col.prop(mat,         "spr_friction_static", text="Static Friction")
		else:
			col.label(text="<Please Add Material>")

		# -- 
		split = layout.split()
		col = split.column(align=True)
		col.prop(obj, "spr_autoset_inertia", text="Automatic Inertia Setting")
		if obj.spr_autoset_inertia==0:
			row = col.row()
			row.prop(obj, "spr_inertia_x",  text="X")
			row.prop(obj, "spr_inertia_xy", text="xy")
			row.prop(obj, "spr_inertia_xz", text="xz")
			row = col.row()
			row.prop(obj, "spr_inertia_yx", text="yx")
			row.prop(obj, "spr_inertia_y",  text="Y")
			row.prop(obj, "spr_inertia_yz", text="yz")
			row = col.row()
			row.prop(obj, "spr_inertia_zx", text="zx")
			row.prop(obj, "spr_inertia_zy", text="zy")
			row.prop(obj, "spr_inertia_z",  text="Z")
			row = col.row()
			row.operator("spr.solid_inertia_calc", "Auto")
			row.operator("spr.solid_inertia_zero", "Zero")
			row.operator("spr.solid_inertia_unit", "Unit")

		# --
		split = layout.split()
		row = split.row()
		row.prop(obj, "spr_connect_interface",   text="Human Interface")

		# --- --- --- --- ---
		# Solid Control Panel
		box   = layout.box()
		split = box.split()
		col = split.column()
		col.prop(obj, "spr_show_solid_control", text="Show Solid Control Panel")

		if obj.spr_show_solid_control==1:
			box2 = box.box()
			split = box2.split()
			col1 = split.column()
			col1.label(text="Velocity")
			col2 = split.column()
			row = col2.row(align=True)
			row.prop(obj, "spr_solid_velocity_edit", icon_only=True, text="", icon=("UNLOCKED" if obj.spr_solid_velocity_edit else "LOCKED")) #<!!>
			row.prop(obj, "spr_solid_velocity_hold", text="Hold", icon=("PINNED" if obj.spr_solid_velocity_hold else "UNPINNED"))
			if obj.spr_solid_velocity_hold==1:
				row.prop(obj, "spr_solid_velocity_apply", text="Apply", toggle=True)
			split = box2.split()
			row = split.row(align=True)
			if obj.spr_solid_velocity_edit:
				row.prop(obj, "spr_solid_velocity_local", text="Local")
			row.prop(obj, "spr_solid_velocity_x", text="x")
			row.prop(obj, "spr_solid_velocity_y", text="y")
			row.prop(obj, "spr_solid_velocity_z", text="z")
			if obj.spr_solid_velocity_edit == 0:
				row.enabled = False
			
			# --
			box2 = box.box()
			split = box2.split()
			col1 = split.column()
			col1.label(text="Angular Velocity")
			col2 = split.column()
			row = col2.row(align=True)
			row.prop(obj, "spr_solid_angvelocity_edit", icon_only=True, text="", icon=("UNLOCKED" if obj.spr_solid_angvelocity_edit else "LOCKED"), toggle=True)
			row.prop(obj, "spr_solid_angvelocity_hold", text="Hold", icon=("PINNED" if obj.spr_solid_angvelocity_hold else "UNPINNED"))
			if obj.spr_solid_angvelocity_hold==1:
				row.prop(obj, "spr_solid_angvelocity_apply", text="Apply", toggle=True)
			split = box2.split()
			row = split.row(align=True)
			if obj.spr_solid_angvelocity_edit:
				row.prop(obj, "spr_solid_ang_velocity_local", text="Local")
			row.prop(obj, "spr_solid_angular_velocity_x", text="x")
			row.prop(obj, "spr_solid_angular_velocity_y", text="y")
			row.prop(obj, "spr_solid_angular_velocity_z", text="z")
			if obj.spr_solid_angvelocity_edit == 0:
				row.enabled = False

			# --
			box2 = box.box()
			split = box2.split()
			col1 = split.column()
			col1.label(text="Force")
			col2 = split.column()
			row = col2.row(align=True)
			row.prop(obj, "spr_solid_force_edit", icon_only=True, text="", icon=("UNLOCKED" if obj.spr_solid_force_edit else "LOCKED"), toggle=True)
			row.prop(obj, "spr_solid_force_hold", text="Hold", icon=("PINNED" if obj.spr_solid_force_hold else "UNPINNED"))
			if obj.spr_solid_force_hold==1:
				row.prop(obj, "spr_solid_force_apply", text="Apply", toggle=True)
			split = box2.split()
			row = split.row(align=True)
			if obj.spr_solid_force_edit:
				row.prop(obj, "spr_solid_force_local", text="Local")
			row.prop(obj, "spr_solid_force_x", text="x")
			row.prop(obj, "spr_solid_force_y", text="y")
			row.prop(obj, "spr_solid_force_z", text="z")
			if obj.spr_solid_force_edit == 0:
				row.enabled = False

			split = box2.split()
			row = split.row(align=True)
			if obj.spr_solid_force_edit == 0:
				row.enabled = False
			else:
				row.prop(obj, "spr_solid_set_force_point", text="Set Apply Point")
				if obj.spr_solid_set_force_point:
					row.prop(obj, "spr_solid_force_point_x", text="x")
					row.prop(obj, "spr_solid_force_point_y", text="y")
					row.prop(obj, "spr_solid_force_point_z", text="z")

			# --
			box2 = box.box()
			split = box2.split()
			col1 = split.column()
			col1.label(text="Torque")
			col2 = split.column()
			row = col2.row(align=True)
			row.prop(obj, "spr_solid_torque_edit", icon_only=True, text="", icon=("UNLOCKED" if obj.spr_solid_torque_edit else "LOCKED"), toggle=True)
			row.prop(obj, "spr_solid_torque_hold", text="Hold", icon=("PINNED" if obj.spr_solid_torque_hold else "UNPINNED"))
			if obj.spr_solid_torque_hold==1:
				row.prop(obj, "spr_solid_torque_apply", text="Apply", toggle=True)
			split = box2.split()
			row = split.row(align=True)
			if obj.spr_solid_torque_edit:
				row.prop(obj, "spr_solid_torque_local", text="Local")
			row.prop(obj, "spr_solid_torque_x", text="x")
			row.prop(obj, "spr_solid_torque_y", text="y")
			row.prop(obj, "spr_solid_torque_z", text="z")
			if obj.spr_solid_torque_edit == 0:
				row.enabled = False
				


		# --- --- --- --- ---
		# IK Endeffector
		box   = layout.box()
		split = box.split()
		col = split.column()
		col.prop(obj, "spr_ik_enabled", text="IK Endeffector")

		if obj.spr_ik_enabled==1:
			split = box.split()
			col = split.column()
			if (obj.spr_ik_tip_use_obj):
				col.label("Tip Object Name")
			else:
				col.label("Tip Position / Direction")
			row = col.row(align=True)
			row.prop(obj, "spr_ik_tip_use_obj", text="", icon=('RESTRICT_SELECT_OFF' if obj.spr_ik_tip_use_obj==1 else 'RESTRICT_SELECT_ON'))
			if (obj.spr_ik_tip_use_obj):
				row.prop(obj, "spr_ik_tip_object_name", text="")
			else:
				row.prop(obj, "spr_ik_target_local_pos_x", text="x")
				row.prop(obj, "spr_ik_target_local_pos_y", text="y")
				row.prop(obj, "spr_ik_target_local_pos_z", text="z")
				row.prop(obj, "spr_ik_target_local_dir_x", text="x")
				row.prop(obj, "spr_ik_target_local_dir_y", text="y")
				row.prop(obj, "spr_ik_target_local_dir_z", text="z")
				row.operator("spr.ik_target_local_from_cursor",text="", icon='CURSOR')

			split = box.split()
			row = split.row()
			row.prop(obj, "spr_ik_pos_control_enabled", text="Position Control")
			row.prop(obj, "spr_ik_ori_control_enabled", text="Orientation Control")
			if obj.spr_ik_ori_control_enabled:
				row.prop(obj, "spr_ik_ori_control_mode", text="")

			split = box.split()
			row = split.row()
			row.prop(obj, "spr_ik_position_priority", text="Position Priority")
			
			# --- --- --- --- ---
			# IK Control
			box   = layout.box()
			split = box.split()
			row = split.row()
			row.prop(obj, "spr_show_ik_control", text="Show IK Control Panel")

			if obj.spr_show_ik_control==1:
				row2 = row.row(align=True)
				row2.prop(obj, "spr_ik_targetpose_edit", icon_only=True, text="", icon=("UNLOCKED" if obj.spr_ik_targetpose_edit else "LOCKED"), toggle=True)
				row2.prop(obj, "spr_ik_targetpose_hold", text="Hold", icon=("PINNED" if obj.spr_ik_targetpose_hold else "UNPINNED"))
				if obj.spr_ik_targetpose_hold==1:
					row2.prop(obj, "spr_ik_targetpose_apply", text="Apply", toggle=True)

				split = box.split()
				row = split.row()
				row.prop(obj, "spr_ik_target_object_enabled", "Use Target Object")
				row.active = (obj.spr_ik_targetpose_edit==1)
				row2 = row.row()
				row2.active = (obj.spr_ik_target_object_enabled==1 and obj.spr_ik_targetpose_edit==1)
				row2.prop(obj, "spr_ik_target_object_name", text="")

				if obj.spr_ik_target_object_enabled==0:
					split = box.split()
					col  = split.column()

					col2 = col.column(align=True)
					col2.label(text="Target Position:")
					col2.prop(obj, "spr_ik_target_pos_x", text="x")
					col2.prop(obj, "spr_ik_target_pos_y", text="y")
					col2.prop(obj, "spr_ik_target_pos_z", text="z")
					col2.active = (obj.spr_ik_targetpose_edit==1)

					col = split.column()
					col2 = col.column(align=True)
					col2.label(text="Target Orientation (Deg):")
					col2.prop(obj, "spr_ik_target_ori_x", text="x")
					col2.prop(obj, "spr_ik_target_ori_y", text="y")
					col2.prop(obj, "spr_ik_target_ori_z", text="z")
					col2.active = (obj.spr_ik_targetpose_edit==1)


	def draw_joint(self, context):
		layout = self.layout
		
		obj = context.object
		scene = context.scene
		
		# -- 
		split = layout.split()
		row = split.row()
		row.prop(obj, "spr_joint_mode",    text="Type")
		row.prop(obj, "spr_joint_enabled", text="Enable Joint")
		
		# -- 
		box = layout.box()
		split = box.split()
		row = split.row(align=True)
		row.prop(obj, "spr_joint_socket_target",       text="Socket")
		row2 = row.row()
		row2.active = (obj.spr_joint_socket_target=="Solid Name" or obj.spr_joint_socket_target=="Axis Name")
		row2.prop(obj, "spr_joint_socket_target_name", text="Target")

		split = box.split()
		row = split.row(align=True)
		row.prop(obj, "spr_joint_plug_target",         text="Plug")
		row2 = row.row()
		row2.active=(obj.spr_joint_plug_target=="Solid Name")
		row2.prop(obj, "spr_joint_plug_target_name",   text="Target")

		# -- 
		split = layout.split()
		col = split.column()
		if (obj.spr_joint_mode=="Spring"):
			col2 = col.column(align=True)
			col2.label(text ="Spring:")
			col2.prop(obj, "spr_spring_x",   text="x")
			col2.prop(obj, "spr_spring_y",   text="y")
			col2.prop(obj, "spr_spring_z",   text="z")
			col2.prop(obj, "spr_spring_ori", text="ori")

			col2 = col.column(align=True)
			col2.label(text ="Damper:")
			col2.prop(obj, "spr_damper_x",   text="x")
			col2.prop(obj, "spr_damper_y",   text="y")
			col2.prop(obj, "spr_damper_z",   text="z")
			col2.prop(obj, "spr_damper_ori", text="ori")
		else:
			col.prop(obj,  "spr_spring",     text="Spring")
			col.prop(obj,  "spr_damper",     text="Damper")

		col.prop(obj, "spr_joint_max_force", text="Max Force")
				
		# -- 
		col = split.column()
		col.prop(obj,      "spr_joint_collision", text="Collision")
		row = col.row()
		row.active = (obj.spr_joint_mode=="Hinge")
		row.prop(obj,      "spr_joint_cyclic",    text="Cyclic")
		col.prop(obj,      "spr_joint_aba",       text="ABA")

		# --- --- --- --- ---
		# Joint Limit
		box   = layout.box()
		split = box.split()
		col = split.column()
		col.prop(obj, "spr_joint_limit_enable", text="Limit")

		if obj.spr_joint_limit_enable==1:
			if obj.spr_joint_mode=="Hinge" or obj.spr_joint_mode=="Slider":
				split = box.split()
				row = split.row(align=True)
				row.prop(obj, "spr_limit_range_min",   text="min")
				row.operator("spr.limit_inf_range_min",text="-inf")
				row.prop(obj, "spr_limit_range_max",   text="Max")
				row.operator("spr.limit_inf_range_max",text="inf")

			elif obj.spr_joint_mode=="Ball":
				split = box.split()
				row = split.row(align=True)
				row.label(text="Swing")
				row.prop(obj, "spr_limit_swing_min",   text="min")
				row.operator("spr.limit_inf_swing_min",text="-inf")
				row.prop(obj, "spr_limit_swing_max",   text="Max")
				row.operator("spr.limit_inf_swing_max",text="inf")
				
				split = box.split()
				row = split.row(align=True)
				row.label(text="Twist")
				row.prop(obj, "spr_limit_twist_min",   text="min")
				row.operator("spr.limit_inf_twist_min",text="-inf")
				row.prop(obj, "spr_limit_twist_max",   text="Max")
				row.operator("spr.limit_inf_twist_max",text="inf")

			split = box.split()
			row = split.row(align=True)
			row.prop(obj, "spr_limit_spring", text="Spring")
			row.prop(obj, "spr_limit_damper", text="Damper")

		# --- --- --- --- ---
		# Joint Control Panel
		box   = layout.box()
		# --- --- --- --- ---
		
		split = box.split()
		col = split.column()
		col.prop(obj, "spr_show_joint_control", text="Show Joint Control Panel")

		if obj.spr_show_joint_control==1:
			split = box.split()
			
			row = split.row(align=True)
			row.label(text="Target Position")
			row.prop(obj, "spr_joint_targetposition_edit", icon_only=True, text="", icon=("UNLOCKED" if obj.spr_joint_targetposition_edit else "LOCKED"), toggle=True)
			row.prop(obj, "spr_joint_targetposition_hold", text="Hold", icon=("PINNED" if obj.spr_joint_targetposition_hold else "UNPINNED"))
			if obj.spr_joint_targetposition_hold==1:
				row.prop(obj, "spr_joint_targetposition_apply", text="Apply", toggle=True)

			if obj.spr_joint_mode == "Ball":
				'''BallJoint'''
				split = box.split()
				row = split.row(align=True)
				row.prop(obj, "spr_joint_target_position_x", text="x")
				row.prop(obj, "spr_joint_target_position_y", text="y")
				row.prop(obj, "spr_joint_target_position_z", text="z")	
				if obj.spr_joint_targetposition_edit == 0:
					row.enabled = False
			
			else:
				'''Else'''
				split = box.split()
				row = split.row()
				row.prop(obj, "spr_joint_target_position", text = "Target Position")
				if obj.spr_joint_targetposition_edit == 0:
					row.enabled = False
			
			# ---
			split = box.split()

			row = split.row(align=True)
			row.label(text="Target Velocity")
			row.prop(obj, "spr_joint_velocity_edit", icon_only=True, text="", icon=("UNLOCKED" if obj.spr_joint_velocity_edit else "LOCKED"), toggle=True)
			row.prop(obj, "spr_joint_velocity_hold", text="Hold", icon=("PINNED" if obj.spr_joint_velocity_hold else "UNPINNED"))
			if obj.spr_joint_velocity_hold==1:
				row.prop(obj, "spr_joint_velocity_apply", text="Apply", toggle=True)

			if obj.spr_joint_mode == "Ball":
				'''Ball Joint'''
				split = box.split()
				row = split.row(align=True)
				row.prop(obj, "spr_joint_target_velocity_x", text="x")
				row.prop(obj, "spr_joint_target_velocity_y", text="y")
				row.prop(obj, "spr_joint_target_velocity_z", text="z")	
				if obj.spr_joint_velocity_edit == 0:
					row.enabled = False
			
			else:
				'''Else'''
				split = box.split()
				row = split.row()
				row.prop(obj, "spr_joint_target_velocity", text = "Target Velocity")
				if obj.spr_joint_velocity_edit == 0:
					row.enabled = False
			
			# ---
			split = box.split()

			row = split.row(align=True)
			row.label(text="Offset Force")
			row.prop(obj, "spr_joint_offsetforce_edit", icon_only=True, text="", icon=("UNLOCKED" if obj.spr_joint_offsetforce_edit else "LOCKED"), toggle=True)
			row.prop(obj, "spr_joint_offsetforce_hold", text="Hold", icon=("PINNED" if obj.spr_joint_offsetforce_hold else "UNPINNED"))
			if obj.spr_joint_offsetforce_hold==1:
				row.prop(obj, "spr_joint_offsetforce_apply", text="Apply", toggle=True)

			if obj.spr_joint_mode == "Ball":
				'''BallJoint'''
				split = box.split()
				row = split.row(align=True)
				row.prop(obj, "spr_joint_offset_force_x", text="x")
				row.prop(obj, "spr_joint_offset_force_y", text="y")
				row.prop(obj, "spr_joint_offset_force_z", text="z")	
				if obj.spr_joint_offsetforce_edit == 0:
					row.enabled = False
			
			else:
				'''Else'''
				split = box.split()
				row = split.row()
				row.prop(obj, "spr_joint_offset_force", text = "Offset Force")
				if obj.spr_joint_offsetforce_edit == 0:
					row.enabled = False
			
		# --- --- --- --- ---
		# IK Actuator
		box   = layout.box()
		split = box.split()
		col = split.column()
		col.prop(obj, "spr_ik_enabled", text="IK Actuator")

		if obj.spr_ik_enabled==1:
			split = box.split()
			row = split.column()
			row.prop(obj, "spr_ik_bias",          "Bias")
			row.prop(obj, "spr_ik_pullback_rate", "Pullback")


# --- --- --- --- --- --- --- --- --- --- 
# ボタンを押した際の動作

# 剛体のShapeのRenewボタンを押した際の動作
class OBJECT_OT_SprShapeRenew(bpy.types.Operator):
	bl_idname      = "spr.shape_renew"
	bl_label       = "[spr]Shape Renew"
	bl_description = "Apply update on bpy shape into spr shape"
	
	def execute(self,context):
		obj = context.object
		
		handler = spb.handlers.shape_handlers[obj.name]
		if not handler is None:
			handler.destroy()
			handler.build()
		
		return{'FINISHED'}


# 剛体CenterのFrom Cursorボタンを押した際の動作
class OBJECT_OT_SprSolidCenterFromCursor(bpy.types.Operator):
	bl_idname      = "spr.solid_center_from_cursor"
	bl_label       = "[spr]Set Center to Cursor Position"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		
		handler = spb.handlers.solid_handlers[obj.name]
		if not handler is None:
			cursor_pos = bpy.context.scene.cursor_location
			cursor_pos = Vec3d(cursor_pos.x, cursor_pos.y, cursor_pos.z)
			local_pos  = handler.phSolid.GetPose().Inv().transform(cursor_pos)
			handler.object.spr_center_x = local_pos.x
			handler.object.spr_center_y = local_pos.y
			handler.object.spr_center_z = local_pos.z
		
		return{'FINISHED'}


# 剛体のInertia Autoボタンを押した際の動作
class OBJECT_OT_SprSolidInertiaCalc(bpy.types.Operator):
	bl_idname      = "spr.solid_inertia_calc"
	bl_label       = "[spr]Calc Inertia Tensor"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		
		handler = spb.handlers.solid_handlers[obj.name]
		if not handler is None:
			pass
		
		return{'FINISHED'}


# 剛体のInertia Zeroボタンを押した際の動作
class OBJECT_OT_SprSolidInertiaZero(bpy.types.Operator):
	bl_idname      = "spr.solid_inertia_zero"
	bl_label       = "[spr]Set Inertia Tensor to Zero"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		obj.spr_inertia_x  = 0
		obj.spr_inertia_xy = 0
		obj.spr_inertia_xz = 0
		obj.spr_inertia_yx = 0
		obj.spr_inertia_y  = 0
		obj.spr_inertia_yz = 0
		obj.spr_inertia_zx = 0
		obj.spr_inertia_zy = 0
		obj.spr_inertia_z  = 0
		
		return{'FINISHED'}


# 剛体のInertia Unitボタンを押した際の動作
class OBJECT_OT_SprSolidInertiaUnit(bpy.types.Operator):
	bl_idname      = "spr.solid_inertia_unit"
	bl_label       = "[spr]Set Inertia Tensor to Unit Matrix"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object
		obj.spr_inertia_x  = 1
		obj.spr_inertia_xy = 0
		obj.spr_inertia_xz = 0
		obj.spr_inertia_yx = 0
		obj.spr_inertia_y  = 1
		obj.spr_inertia_yz = 0
		obj.spr_inertia_zx = 0
		obj.spr_inertia_zy = 0
		obj.spr_inertia_z  = 1
		
		return{'FINISHED'}


# IK EndeffectorのFrom Cursorボタンを押した時の動作
class OBJECT_OT_SprIKTargetLocalFromCursor(bpy.types.Operator):
	bl_idname = "spr.ik_target_local_from_cursor"
	bl_label = "[spr]Set IK Target Local Position from Cursor"
	bl_description = "[Spr]"
	
	def execute(self,context):
		obj = context.object

		ikeff_hnd = spb.handlers.ikeff_handlers[obj.name]
		if ikeff_hnd:
			cursor_pos = to_spr(bpy.context.scene.cursor_location)
			local_pos  = ikeff_hnd.solidHnd.phSolid.GetPose().Inv().transform(cursor_pos)
			ikeff_hnd.object.spr_ik_target_local_pos_x = local_pos.x
			ikeff_hnd.object.spr_ik_target_local_pos_y = local_pos.y
			ikeff_hnd.object.spr_ik_target_local_pos_z = local_pos.z
		
		return{'FINISHED'}



# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# SprMaterialパネルのレイアウト
#

#Spr Object Panelでも設定できるがMaterialパネルにも表示する
class SprMaterialPanel(bpy.types.Panel):
	bl_label = "Springhead Material"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "material"

	def draw(self, context):
		layout = self.layout

		obj = context.object
		mat = obj.material_slots.id_data.active_material

		split = layout.split()
		row = split.row(align=True)
		row.prop(obj, "spr_solid_props_hold", text="Hold", icon=("PINNED" if obj.spr_solid_props_hold else "UNPINNED"))
		if obj.spr_solid_props_hold==1:
			row.prop(obj, "spr_solid_props_apply", text="Apply", toggle=True)

		split = layout.split()
		col = split.column()
		if(mat!=None):
			col.prop(mat.physics, "elasticity",  text="Elasticity")
			col.prop(mat.physics, "friction",    text="Friction")
			col.prop(mat, "spr_friction_static", text="Static Friction")



# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Creatureパネルのレイアウト
#

class SprCreaturePanel(bpy.types.Panel):
	bl_label = "Springhead Creature"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	def draw(self, context):
		layout = self.layout

		obj = context.object
		group = None
		if len(obj.users_group):
			for g in obj.users_group:
				if(g.spr_creature_group==1):
					group = g
		
		if((not group is None) and (obj.name in spb.handlers.solid_handlers)):
			layout.label(text = "Name: " + group.name)
			
			layout.prop(obj,"spr_crbone_label", text="Bone Label")

			row = layout.row()
			row.prop(group,"spr_creature_spring_damper_ratio", text="Spring & Damper Scaling")

			row = layout.row(align=True)
			row.prop(group,"spr_creature_spring_ratio", text="Spring Scaling")
			row.prop(group,"spr_creature_damper_ratio", text="Damper Scaling")
			
			# ---

			# <!!> Selectボタンつけたい
			split = layout.split()
			col = split.column(align=True)
			col.label(text="Bone Parameters: ")
			creature_hnd = spb.handlers.creature_handlers[group.name]
			col2 = col.box().column()
			for i, obj_name in creature_hnd.get_ika_tree():
				ika_hnd = spb.handlers.ikact_handlers[obj_name]
				if obj_name in bpy.data.objects:
					obj = bpy.data.objects[obj_name]

					row = col2.row()
					# row.alignment='LEFT'
					col3 = row.column(align=True)
					col3.label(text=("Depth["+str(i)+"] : "+obj.name))
					row2 = col3.row(align=True)
					row2.prop(obj, "spr_spring",           text="K")
					row2.prop(obj, "spr_damper",           text="D")
					row2.prop(obj, "spr_ik_bias",          text="B")
					row2.prop(obj, "spr_ik_pullback_rate", text="P")

			# ---

			split = layout.split()
			col = split.column(align=True)
			col.label(text="Parameters: ")
			row = col.row(align=True)
			for param in group.spr_creature_parameters:
				row = col.row(align=True)
				row.context_pointer_set("object", param)
				row.prop(param, "name",  text="")
				row.prop(param, "value", text="", slider=True)
				row.operator("spr.cr_del_parameter", text="", icon='X')
			col.operator("spr.cr_add_parameter", text="Add Parameter", icon='ZOOMIN')

			# ---編集中
			
			col = layout.column()
			col.prop(group,"spr_creature_onomatopoeia", text="Impression")
			col.operator("spr.cr_store_impress", text ="Store Impression <=> Parameter Pair")
			row = col.row(align=True)
			row.operator("spr.cr_review_impress_data", text ="Review")
			row.operator("spr.cr_load_impress_data", text ="Load DB")

			col = layout.column()
			# col.label(text="Mapping(Otitukanai,Awatenbou,Karui,Nonbiri,Yukkuri,Omoi,Kinchou):")
			col.prop(group,"spr_creature_selected_onomatopoeia", text="Impression Word for Mapping")
			col.operator("spr.cr_mapping_impress", text ="Generate Impression Map")
			row = col.row(align=True)
			row.prop(group,"spr_creature_save_filename", text="file name")
			row.operator("spr.cr_load_impress_map", text ="Load Map")
			row.operator("spr.cr_save_impress_map", text ="Save")


			# ---

			split = layout.split()
			col = split.column(align=True)
			col.label(text="Controllers: ")
			row = col.row(align=True)

			for controller in group.spr_controllers:
				box = col.box()
				row = box.row(align=True)
				row.context_pointer_set("object", controller)
				row.prop(controller, "name", text="")
				row.prop(controller, "type", text="")
				row.prop(controller, "visualize", text="", icon=('RESTRICT_VIEW_OFF' if controller.visualize==1 else 'RESTRICT_VIEW_ON'))
				row.operator("spr.cr_del_controller", text="", icon='X')

				c = box.column()

				if controller.type=="Reach":
					c.prop(controller, "target",      text="Target")
					# c.prop(controller, "reach_speed", text="Speed")

			col.operator("spr.cr_add_controller", text="Add Controller", icon='ZOOMIN')

			# ---

			split = layout.split()
			col = split.column(align=True)
			col.label(text="Visualizers: ")
			row = col.row(align=True)
			for visualizer in group.spr_visualizers:
				box = col.box()
				row = box.row(align=True)
				row.context_pointer_set("object", visualizer)
				row.prop(visualizer, "name",   text="")
				row.prop(visualizer, "type",   text="")
				row.prop(visualizer, "show",   text="", icon=('RESTRICT_VIEW_OFF' if visualizer.show==1 else 'RESTRICT_VIEW_ON'))
				row.operator("spr.cr_del_visualizer", text="", icon='X')

				vis_hnd = spb.handlers.visualizer_handlers[visualizer.name]

				c = box.column()

				if visualizer.type=="FOV":
					pass
					# c.prop(visualizer, "target", text="Target")
					# c.prop(visualizer, "fov_param_name_horiz", text="Horiz Param Name")
					# c.prop(visualizer, "fov_param_name_vert",  text="Vert Param Name")
					# if (not vis_hnd is None) and (vis_hnd.visualizer.matname in bpy.data.materials):
					# 	mat = bpy.data.materials[vis_hnd.visualizer.matname]
					# 	d = c.row()
					# 	d.prop(mat, "diffuse_color", text="")
					# 	d.prop(mat, "alpha", text="alpha")

				if visualizer.type=="Magnitude":
					pass
					# if (not vis_hnd is None) and (vis_hnd.visualizer.matname in bpy.data.materials):
					# 	mat = bpy.data.materials[vis_hnd.visualizer.matname]
					# 	d = c.row()
					# 	d.prop(mat, "diffuse_color", text="")
					# 	d.prop(mat, "alpha", text="alpha")

			col.operator("spr.cr_add_visualizer", text="Add Visualizer", icon='ZOOMIN')

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# Groupパネルの上書き
# Override bl_ui/properties_object.py

# <!!> blenderのバージョンアップに伴い仕様変更が必要！！！
'''
class OBJECT_PT_groups(bpy.types.Panel):
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "object"
	bl_label = "Groups"

	def draw(self, context):
		layout = self.layout

		ob = context.object

		row = layout.row(align=True)
		row.operator("object.group_link", text="Add to Group")
		row.operator("object.group_add", text="", icon='ZOOMIN')

		index = 0
		for group in bpy.data.groups:
			if ob.name in group.objects:
				col = layout.column(align=True)

				col.context_pointer_set("group", group)
				
				
				row = col.box().row()
				
				row.prop(group, "name", text="")
				row.operator("object.group_remove", text="", icon='X', emboss=False)

				split = col.box().split()

				col2 = split.column()
				col2.prop(group, "layers", text="Dupli")

				col2 = split.column()
				col2.prop(group, "dupli_offset", text="")

				props = col2.operator("object.dupli_offset_from_cursor", text="From Cursor")
				props.group = index
				index += 1
				
				#for Spr Creature
				split = col.box().split()
				cr_group = None
				if len(ob.users_group):
					for g in ob.users_group:
						if(g.spr_creature_group==1):
							cr_group = g
				if (cr_group is None) or (cr_group == group):
					split.prop(group,"spr_creature_group", text="Spr Creature")
'''


## Creature Panelのボタン動作
class OBJECT_OT_SprCrAddParameter(bpy.types.Operator):
	bl_idname = "spr.cr_add_parameter"
	bl_label = "[spr]Add Creature Parameter"
	bl_description = "[Spr]"
	
	def execute(self,context):
		
		obj = context.object
		group = None
		if len(obj.users_group):
			for g in obj.users_group:
				if(g.spr_creature_group==1):
					group = g
		
		if(not group is None):
			param = group.spr_creature_parameters.add()
			param.creaturename = group.name
		
		return{'FINISHED'}

class OBJECT_OT_SprCrDelParameter(bpy.types.Operator):
	bl_idname = "spr.cr_del_parameter"
	bl_label = "[spr]Remove Creature Parameter"
	bl_description = "[Spr]"
	
	def execute(self,context):
		param = context.object
		parameters = bpy.data.groups[param.creaturename].spr_creature_parameters
		for i in range(0, len(parameters)):
			if parameters[i]==param:
				parameters.remove(i)
				return{'FINISHED'}
		
		return{'FINISHED'}


class OBJECT_OT_SprCrAddController(bpy.types.Operator):
	bl_idname = "spr.cr_add_controller"
	bl_label = "[spr]Add Creature Controller"
	bl_description = "[Spr]"
	
	def execute(self,context):
		
		obj = context.object
		group = None
		if len(obj.users_group):
			for g in obj.users_group:
				if(g.spr_creature_group==1):
					group = g
		
		if(not group is None):
			controller = group.spr_controllers.add()
			controller.creaturename = group.name
		
		return{'FINISHED'}

class OBJECT_OT_SprCrDelController(bpy.types.Operator):
	bl_idname = "spr.cr_del_controller"
	bl_label = "[spr]Remove Creature Controller"
	bl_description = "[Spr]"
	
	def execute(self,context):
		controller  = context.object
		controllers = bpy.data.groups[controller.creaturename].spr_controllers
		for i in range(0, len(controllers)):
			if controllers[i]==controller:
				controllers.remove(i)
				return{'FINISHED'}
		
		return{'FINISHED'}


class OBJECT_OT_SprCrAddVisualizer(bpy.types.Operator):
	bl_idname = "spr.cr_add_visualizer"
	bl_label = "[spr]Add Creature Visualizer"
	bl_description = "[Spr]"
	
	def execute(self,context):
		
		obj = context.object
		group = None
		if len(obj.users_group):
			for g in obj.users_group:
				if(g.spr_creature_group==1):
					group = g
		
		if(not group is None):
			visualizer = group.spr_visualizers.add()
			visualizer.creaturename = group.name
		
		return{'FINISHED'}

class OBJECT_OT_SprCrDelVisualizer(bpy.types.Operator):
	bl_idname = "spr.cr_del_visualizer"
	bl_label = "[spr]Remove Creature Visualizer"
	bl_description = "[Spr]"
	
	def execute(self,context):
		visualizer  = context.object
		visualizers = bpy.data.groups[visualizer.creaturename].spr_visualizers
		for i in range(0, len(visualizers)):
			if visualizers[i]==visualizer:
				visualizers.remove(i)
				return{'FINISHED'}
		
		return{'FINISHED'}


class OBJECT_OT_SprCrVisualizeDisplay(bpy.types.Operator):
	bl_idname = "spr.cr_visualize_display"
	bl_label = "[spr]Creature Visualize Display"
	bl_description = "[Spr]"
	
	def execute(self,context):
		
		obj = context.object
		group = None
		if len(obj.users_group):
			for g in obj.users_group:
				if(g.spr_creature_group==1):
					group = g
		
		return{'FINISHED'}

class OBJECT_OT_SprCrVisualizeHide(bpy.types.Operator):
	bl_idname = "spr.cr_visualize_hide"
	bl_label = "[spr]Creature Visualize Hide"
	bl_description = "[Spr]"
	
	def execute(self,context):
		
		obj = context.object
		group = None
		if len(obj.users_group):
			for g in obj.users_group:
				if(g.spr_creature_group==1):
					group = g
		
		return{'FINISHED'}

class OBJECT_OT_SprCrRulesApply(bpy.types.Operator):
	bl_idname = "spr.cr_rules_apply"
	bl_label = "[spr]Creature Apply Rules"
	bl_description = "[Spr]"
	
	def execute(self,context):
		
		obj = context.object
		group = None
		if len(obj.users_group):
			for g in obj.users_group:
				if(g.spr_creature_group==1):
					group = g
		
		if(not group is None):
			creature_handler = spb.handlers.creature_handlers[group.name]
			if creature_handler:
				creature_handler.rule.update()
		
		return{'FINISHED'}

class OBJECT_OT_SprCrParametersApply(bpy.types.Operator):
	bl_idname = "spr.cr_parameters_apply"
	bl_label = "[spr]Creature Apply Parameters"
	bl_description = "[Spr]"
	
	def execute(self,context):
		
		obj = context.object
		group = None
		if len(obj.users_group):
			for g in obj.users_group:
				if(g.spr_creature_group==1):
					group = g
		
		if(not group is None):
			creature_handler = spb.handlers.creature_handlers[group.name]
			if creature_handler:
				creature_handler.apply_bpy_change = True
				creature_handler.sync()
		
		return{'FINISHED'}

class OBJECT_OT_SprCrStoreImpress(bpy.types.Operator):#外部テキストファイルに追記する形に追加変更
	bl_idname = "spr.cr_store_impress"
	bl_label = "[spr]"
	bl_description = "[Spr]"
	
	def execute(self,context):

		spring = bpy.data.groups['Koguma'].spr_creature_parameters[2].value
		damper =  bpy.data.groups['Koguma'].spr_creature_parameters[3].value
		bias_top =  bpy.data.groups['Koguma'].spr_creature_parameters[4].value
		bias_f =  bpy.data.groups['Koguma'].spr_creature_parameters[5].value

		b_apperarm =  bpy.data.groups['Koguma'].spr_creature_parameters[6].value
		b_lowerarm =  bpy.data.groups['Koguma'].spr_creature_parameters[7].value
		b_hand =  bpy.data.groups['Koguma'].spr_creature_parameters[8].value
		b_head =  bpy.data.groups['Koguma'].spr_creature_parameters[9].value

		r_speed =  bpy.data.groups['Koguma'].spr_creature_parameters[10].value
		b_speed =  bpy.data.groups['Koguma'].spr_creature_parameters[11].value

		name = bpy.data.groups['Koguma'].spr_creature_onomatopoeia

		f = open("exam.txt", "a")
		try:
			f.write(str(spring))
			f.write("  ")
			f.write(str(damper))
			f.write("  ")
			f.write(str(bias_top))
			f.write("  ")
			f.write(str(bias_f))
			f.write("  ")
			f.write(str(b_apperarm))
			f.write("  ")
			f.write(str(b_lowerarm))
			f.write("  ")
			f.write(str(b_hand))
			f.write("  ")
			f.write(str(b_head))
			f.write("  ")
			f.write(str(r_speed))
			f.write("  ")
			f.write(str(b_speed))
			f.write("  ")
			f.write(name)
			f.write("\n")
		finally:
			f.close()

		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Write Data

		f = open("data.csv", "a")
		try:
			f.write(name)
			f.write(",")
			f.write(str(spring))
			f.write(",")
			f.write(str(damper))
			f.write(",")
			f.write(str(bias_top))
			f.write(",")
			f.write(str(bias_f))
			f.write(",")
			f.write(str(b_apperarm))
			f.write(",")
			f.write(str(r_speed))
			f.write(",")
			f.write(str(b_speed))
			f.write("\n")
		finally:
			f.close()

		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Write Map Positoin Data

		if not spb.som == None:
			f = open("posi.csv", "a")
			f.write(name)
			f.write(",")
			f.write(str(spb.posi_x))
			f.write(",")
			f.write( str(spb.posi_y) )
			f.write("\n")
			
		return{'FINISHED'}

class OBJECT_OT_SprCrReviewImpressData(bpy.types.Operator):#外部テキストファイルを読み込む
	bl_idname = "spr.cr_review_impress_data"
	bl_label = "[spr]"
	bl_description = "[Spr]"
	
	def execute(self,context):

		f = open("exam.txt", "r")
		datas = f.read()
		f.close

		bpy.data.texts["Text.Console"].from_string(datas)

		lines1 = datas.split('\n')
		for line in lines1:
			print(line)

		return{'FINISHED'}

class OBJECT_OT_SprCrLoadImpressData(bpy.types.Operator):#外部テキストファイルから読み込んでセット
	bl_idname = "spr.cr_load_impress_data"
	bl_label = "[spr]"
	bl_description = "[Spr]"
	
	def execute(self,context):
		name = bpy.data.groups['Koguma'].spr_creature_onomatopoeia

		f = open("exam.txt", "r")
		datas = f.read()
		f.close
#		i = -1
		cnt = False
		print(name)

		lines1 = datas.split('\n')
		for line in lines1:
			values = line.split('  ')
			if name == values[-1]:
				i = 0
				for value in values:
					print(value)
					bpy.data.groups['Koguma'].spr_creature_parameters[i+2].value = float(value)
					if i == 11-2:
						break
					i=i+1
				cnt = True
		if cnt == False:
			print("no data")

		return{'FINISHED'}

class OBJECT_OT_SprCrMappingImpress(bpy.types.Operator):#SOMによる印象マッピング
	bl_idname = "spr.cr_mapping_impress"
	bl_label = "[spr]"
	bl_description = "[Spr]"
	
	def execute(self,context):
		words = bpy.data.groups['Koguma'].spr_creature_selected_onomatopoeia
		labels = words.rstrip().split(",")
		print(labels)

		vertex_colors = bpy.data.objects['Grid_Map'].data.vertex_colors['Col']

		N   = 7#対象とするパラメータは７つ
		INF = 1e+38

		value_range = []
		for i in range(0,N):
			value_range.append([INF,-INF])
		spb.data = []

		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Read Data
		bnlen = len(bpy.path.basename(bpy.data.filepath))
		dir   = bpy.data.filepath[0:-bnlen]

		ifp = open(dir+"data.csv", "r")
		for line in ifp:
			line   = line.rstrip().split(",")
			label  = line[0]
			if label in labels:
				vector = Vector([float(x) for x in line[1:]])
				line   = (label, vector)
				for i in range(0,len(vector)):
					value_range[i][0] = min(vector[i], value_range[i][0])
					value_range[i][1] = max(vector[i], value_range[i][1])
				spb.data.append(line)
		ifp.close

		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Prepare
		dim = 30
		spb.som = [[None for j in range(0,dim)] for i in range(0,dim)]
		for i in range(0,dim):
			for j in range(0,dim):
				spb.som[i][j] = Vector([random.uniform(value_range[n][0], value_range[n][1]) for n in range(0,N)])

		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Learn
		n_iteration = 50
		for times in range(0,n_iteration):
			for item in spb.data:
				# ----- ----- ----- ----- -----
				# Find BMU
				bmu = [0,0,INF]
				for i in range(0,dim):
					for j in range(0,dim):
						norm = (spb.som[i][j]-item[1]).length#これがベクトル同士のノルム(距離)
						if norm < bmu[2]:
							bmu = [i,j,norm]

				# ----- ----- ----- ----- -----
				# Update Weight
				max_r = 30.0
				min_r =  3.0
				r = (min_r - max_r)*(times/n_iteration) + max_r
				for i in range(0,dim):
					for j in range(0,dim):
						distance = ( Vector((i,j))-Vector((bmu[0],bmu[1])) ).length
						if distance < r:
							theta = (r-distance)/r
							alpha = 0.1
							spb.som[i][j] += theta * alpha * (item[1] - spb.som[i][j])
				
		# ----- ----- ----- ----- -----
		# Visualize
		for i in range(0,3364):
			vertex_colors.data[i].color = [0,0,0]

		for i in range(0,dim):
			for j in range(0,dim):
				bmu = [" ",INF]
				for item in spb.data:
					norm = (spb.som[i][j] - item[1]).length
					if norm < bmu[1]:
						bmu = (item[0], norm)

				color_map = {
					"Otitukanai":[1,0,0],
					"Awatenbou":[0,1,0],
					"Karui":[0,0,1],
					"Nonbiri":[1,1,0],
					"Yukkuri":[0,1,1],
					"Omoi":[1,0,1],
					"Kinchou":[1,1,1]
				}
				color = [v for v in (Vector(color_map[bmu[0]]) * 2**(-bmu[1]/10.0) )]

				idx1 = 4*j+(30-1)*4*i - 0 -  0
				if 0<=idx1 and idx1<len(vertex_colors.data):
					vertex_colors.data[idx1].color = color
				idx3 = 4*j+(30-1)*4*i + 3 - (30-1)*4
				if 0<=idx3 and idx3<len(vertex_colors.data):
					vertex_colors.data[idx3].color = color
				if not j==0:
					idx2 = 4*j+(30-1)*4*i - 3 -  0
					if 0<=idx2 and idx2<len(vertex_colors.data):
						vertex_colors.data[idx2].color = color
					idx4 = 4*j+(30-1)*4*i - 2 - (30-1)*4
					if 0<=idx4 and idx4<len(vertex_colors.data):
						vertex_colors.data[idx4].color = color
		print(spb.som)
		print("som終了")

		return{'FINISHED'}

class OBJECT_OT_SprCrLoadImpressMap(bpy.types.Operator):#外部テキストファイルから読み込んでマップをセット
	bl_idname = "spr.cr_load_impress_map"
	bl_label = "[spr]"
	bl_description = "[Spr]"
	
	def execute(self,context):
		name = bpy.data.groups['Koguma'].spr_creature_save_filename
		f = open(name, "r")
		datas = f.read()
		f.close()
		i = 0
		j = 0
		for line in datas.split("\n"):
			para = line.split(",")[1:8]
			if len(para) > 1:
				print(para)
				spb.som[i][j] = Vector([float(x) for x in para])
			j = j+1
			if j == 30:
				i = i+1
				j = 0
		print(spb.som)
		print("som終了")

		#----- ----- ----- ----- ----- ----- ----- ---- ----- -----
		#Mapping

		words = bpy.data.groups['Koguma'].spr_creature_selected_onomatopoeia
		labels = words.rstrip().split(",")
		print(labels)

		vertex_colors = bpy.data.objects['Grid_Map'].data.vertex_colors['Col']

		N   = 7#対象とするパラメータは７つ
		INF = 1e+38

		value_range = []
		for i in range(0,N):
			value_range.append([INF,-INF])

		spb.data = []

		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Prepare
		dim = 30

		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Read Data
		bnlen = len(bpy.path.basename(bpy.data.filepath))
		dir   = bpy.data.filepath[0:-bnlen]

		ifp = open(dir+"data.csv", "r")
		for line in ifp:
			line   = line.rstrip().split(",")
			label  = line[0]
			if label in labels:
				vector = Vector([float(x) for x in line[1:]])
				line   = (label, vector)
				for i in range(0,len(vector)):
					value_range[i][0] = min(vector[i], value_range[i][0])
					value_range[i][1] = max(vector[i], value_range[i][1])
				spb.data.append(line)
		ifp.close

		# ----- ----- ----- ----- -----
		# Visualize
		for i in range(0,3364):
			vertex_colors.data[i].color = [0,0,0]

		for i in range(0,dim):
			for j in range(0,dim):
				bmu = [" ",INF]
				for item in spb.data:
					norm = (spb.som[i][j] - item[1]).length
					if norm < bmu[1]:
						bmu = (item[0], norm)

				color_map = {
					"Otitukanai":[1,0,0],
					"Awatenbou":[0,1,0],
					"Karui":[0,0,1],
					"Nonbiri":[1,1,0],
					"Yukkuri":[0,1,1],
					"Omoi":[1,0,1],
					"Kinchou":[1,1,1]
				}
				color = [v for v in (Vector(color_map[bmu[0]]) * 2**(-bmu[1]/10.0) )]

				idx1 = 4*j+(30-1)*4*i - 0 -  0
				if 0<=idx1 and idx1<len(vertex_colors.data):
					vertex_colors.data[idx1].color = color
				idx3 = 4*j+(30-1)*4*i + 3 - (30-1)*4
				if 0<=idx3 and idx3<len(vertex_colors.data):
					vertex_colors.data[idx3].color = color
				if not j==0:
					idx2 = 4*j+(30-1)*4*i - 3 -  0
					if 0<=idx2 and idx2<len(vertex_colors.data):
						vertex_colors.data[idx2].color = color
					idx4 = 4*j+(30-1)*4*i - 2 - (30-1)*4
					if 0<=idx4 and idx4<len(vertex_colors.data):
						vertex_colors.data[idx4].color = color

		return{'FINISHED'}

class OBJECT_OT_SprCrSaveImpressMap(bpy.types.Operator):#外部テキストファイルにマップを保存
	bl_idname = "spr.cr_save_impress_map" 
	bl_label = "[spr]"
	bl_description = "[Spr]"
	
	def execute(self,context):
		name = bpy.data.groups['Koguma'].spr_creature_save_filename

		f = open(name, "w")
		for i in range(0,30):
			for j in range(0,30):
				for n in range(0,7):
					f.write(str(spb.som[i][j][n]))
					f.write(",")
				f.write("\n")
		f.close

		return{'FINISHED'}




