# -*- coding: utf-8 -*-

import bpy

# Obsolete Properties : Migrationのために残してある．

def register_properties():
	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Scene
	bpy.types.Scene.spr_sub_step = bpy.props.IntProperty(
		name        = "[spr]physics sub step",
		description = "[Spr]Physics sub step",
		min         = 1,
		default     = 1)
	bpy.types.Scene.spr_step_speed_factor = bpy.props.FloatProperty(
		name        = "[spr]Step Speed Factor default=1",
		description = "[Spr]Change Step Speed. 0~1 to Slow, 1~ to Fast",
		min         = 0,
		default     = 1)

	bpy.types.Scene.spr_step_frame = bpy.props.BoolProperty(
		name        = "[spr]Enable Steping KeyFrame",
		description = "[Spr]Enable Steping KeyFrame",
		default     = 0)
	bpy.types.Scene.spr_sync_current_frame = bpy.props.BoolProperty(
		name        = "[spr]Sync Recording Frame and Current Frame",
		description = "[Spr]Sync Recording Frame and Current Frame",
		default     = 0)

	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Solid
	bpy.types.Object.spr_physics_type = bpy.props.EnumProperty(
		name        = "[spr]spr physics type",
		description = "[Spr]",
		#items = [("value","name","description")]
		items = [("Static","Static","Static"),
			("Dynamic","Dynamic","Dynamic")])

	bpy.types.Object.spr_inertia_manual_setting_enabled = bpy.props.BoolProperty(
		name        = "[spr]inertia manual setting",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_solid_realtime_editing = bpy.props.BoolProperty(
		name        = "[spr]solid real-time editing mode",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_compound_child = bpy.props.BoolProperty(
		name        = "[spr]set child object to compound solid",
		description = "[Spr]",
		default     = 0)

	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Solid Control
	bpy.types.Object.spr_solid_info_enabled = bpy.props.BoolProperty(
		name        = "[spr]Solid Info Enabled",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_velocity_realtime_control_enabled = bpy.props.BoolProperty(
		name        = "[spr]Solid Velocity Realtime Control enabled",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_ang_velocity_realtime_control_enabled = bpy.props.BoolProperty(
		name        = "[spr]Solid Angular Velocity Realtime Control enabled",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_force_realtime_control_enabled = bpy.props.BoolProperty(
		name        = "[spr]Solid Add Force Realtime Control enabled",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_torque_realtime_control_enabled = bpy.props.BoolProperty(
		name        = "[spr]Solid Add Torque Realtime Control enabled",
		description = "[Spr]",
		default     = 0)

	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Joint
	bpy.types.Object.spr_joint_realtime_editing = bpy.props.BoolProperty(
		name        = "[spr]Joint Realtime Editing",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_joint_type = bpy.props.EnumProperty(
		name        = "[spr]spr joint type",
		#items = [("value","name","description")]
		items = [("None","None","None"),
			("Ball","Ball","ball joint"),
			("Hinge","Hinge","hinge joint"),
			("Slider","Slider","slider joint"),
			("Spring","Spring","spring")])

	bpy.types.Object.spr_joint_target = bpy.props.StringProperty(
		name        = "[spr]joint target",
		description = "[Spr]",
		default     = "")
	bpy.types.Object.spr_additional_joint = bpy.props.BoolProperty(
		name        = "[spr]additional joint",
		description = "[Spr]Set This Object as Additional Joint",
		default     = 0)
	bpy.types.Object.spr_joint_plug_handle = bpy.props.BoolProperty(
		name        = "[spr]joint plug handle",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_pos_x = bpy.props.FloatProperty(
		name        = "[spr]joint plug pos x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_pos_y = bpy.props.FloatProperty(
		name        = "[spr]joint plug pos y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_pos_z = bpy.props.FloatProperty(
		name        = "[spr]joint plug pos z",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_ori_w = bpy.props.FloatProperty(
		name        = "[spr]joint plug ori w",
		description = "[Spr]",
		default     = 1)
	bpy.types.Object.spr_joint_plug_ori_x = bpy.props.FloatProperty(
		name        = "[spr]joint plug ori x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_ori_y = bpy.props.FloatProperty(
		name        = "[spr]joint plug ori y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_ori_z = bpy.props.FloatProperty(
		name        = "[spr]joint plug ori z",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_offset_x = bpy.props.FloatProperty(
		name        = "[spr]joint plug ori offset x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_offset_y = bpy.props.FloatProperty(
		name        = "[spr]joint plug ori offset y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_plug_offset_z = bpy.props.FloatProperty(
		name        = "[spr]joint plug ori offset z",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_socket_enabled = bpy.props.BoolProperty(
		name        = "[spr]joint socket enabled",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_socket_handle = bpy.props.BoolProperty(
		name        = "[spr]joint socket handle",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_socket_pos_x = bpy.props.FloatProperty(
		name        = "[spr]joint socket pos x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_socket_pos_y = bpy.props.FloatProperty(
		name        = "[spr]joint socket pos y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_socket_pos_z = bpy.props.FloatProperty(
		name        = "[spr]joint socket pos z",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_socket_ori_w = bpy.props.FloatProperty(
		name        = "[spr]joint socket ori w",
		description = "[Spr]",
		default     = 1)
	bpy.types.Object.spr_joint_socket_ori_x = bpy.props.FloatProperty(
		name        = "[spr]joint socket ori x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_socket_ori_y = bpy.props.FloatProperty(
		name        = "[spr]joint socket ori y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_socket_ori_z = bpy.props.FloatProperty(
		name        = "[spr]joint socket ori z",
		description = "[Spr]",
		default     = 0)


	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# IK
	bpy.types.Object.spr_ik_end_effector = bpy.props.BoolProperty(
		name        = "[spr]Set IK EndEffector",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_ik_realtime_editing = bpy.props.BoolProperty(
		name        = "[spr]IK Realtime Editing",
		description = "[Spr]",
		default     = 0)


	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# CRBone
	bpy.types.Object.spr_CRIKSolid_label = bpy.props.StringProperty(
		name        = "[spr]CRIKSolid label",
		description = "[Spr]",
		default     = "None")


	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Creature
	bpy.types.Group.spr_creature_view_angle_alt = bpy.props.FloatProperty(
		name        = "[spr]creature view angle Alt",
		description = "[Spr]",
		min         = 0,
		max = 90,
		default     = 45)
	bpy.types.Group.spr_creature_view_angle_az = bpy.props.FloatProperty(
		name        = "[spr]creature view angle Az",
		description = "[Spr]",
		min         = 0,
		max = 90,
		default     = 60)

	bpy.types.Group.spr_creature_visualize_enabled = bpy.props.BoolProperty(
		name        = "[spr]creature visualization enabled",
		description = "[Spr]",
		default     = 0)

	bpy.types.Group.spr_creature_rule_parameter_0 = bpy.props.FloatProperty(
		name        = "[spr]creature rule parameter 0",
		description = "[Spr]",
		default     = 1)
	bpy.types.Group.spr_creature_rule_parameter_1 = bpy.props.FloatProperty(
		name        = "[spr]creature rule parameter 1",
		description = "[Spr]",
		default     = 1)
	bpy.types.Group.spr_creature_rule_parameter_2 = bpy.props.FloatProperty(
		name        = "[spr]creature rule parameter 2",
		description = "[Spr]",
		default     = 1)
	bpy.types.Group.spr_creature_rule_parameter_3 = bpy.props.FloatProperty(
		name        = "[spr]creature rule parameter 3",
		description = "[Spr]",
		default     = 1)
	bpy.types.Group.spr_creature_rule_parameter_4 = bpy.props.FloatProperty(
		name        = "[spr]creature rule parameter 4",
		description = "[Spr]",
		default     = 1)
	bpy.types.Group.spr_creature_rule_parameter_5 = bpy.props.FloatProperty(
		name        = "[spr]creature rule parameter 5",
		description = "[Spr]",
		default     = 1)

	bpy.types.Group.spr_visualizer_scale_base = bpy.props.FloatProperty(
		name        = "[spr]creature visualizer scale base",
		description = "[Spr]",
		min         = 0,
		default     = 1)

	bpy.types.Group.spr_visualizer_scale_max = bpy.props.FloatProperty(
		name        = "[spr]creature visualizer scale max(absolute)",
		description = "[Spr]",
		min         = 0,
		default     = 5)
	bpy.types.Group.spr_visualizer_attv_scale_f = bpy.props.FloatProperty(
		name        = "[spr]creature visualizer attv scale factor(default:3.0)",
		description = "[Spr]",
		min         = 0,
		default     = 3)
	bpy.types.Group.spr_visualizer_attt_scale_f = bpy.props.FloatProperty(
		name        = "[spr]creature visualizer attt scale factor(default:0.0001)",
		description = "[Spr]",
		min         = 0,
		default     = 0.0001)

	bpy.types.Group.spr_creature_realtime_editing = bpy.props.BoolProperty(
		name        = "[spr]creature real-time editing mode",
		description = "[Spr]",
		default     = 0)




