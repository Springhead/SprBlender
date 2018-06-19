# -*- coding: utf-8 -*-

import bpy

import spb.properties_old


def register_properties():
	register_scene_properties()
	register_object_properties()
	register_solid_properties()
	register_joint_properties()
	register_ik_properties()
	register_creature_properties()

	# Old Properties : Migrationのために残してある
	spb.properties_old.register_properties()


def register_scene_properties():
	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Pitch Optimize
	# -- trajectory load object --
	bpy.types.Object.load_to_trajectory = bpy.props.EnumProperty(
	name        = "[spr]Load trajectory",
	items = [
		# ("value",        "name",           "description")
		("Trajectory1", "Trajectory1", "Trajectory1"),
		("Trajectory2", "Trajectory2", "Trajectory2"),
		("Trajectory3", "Trajectory3", "Trajectory3"),
		("Trajectory4", "Trajectory4", "Trajectory4"),
		("Trajectory5", "Trajectory5", "Trajectory5") ])
	# -- volume level check --
	bpy.types.Object.volume_level_set = bpy.props.StringProperty(
		name        = "[spr]Check for Volume Level",
		description = "[Spr]",
		default     = "-35")
	# -- trajectory scale --
	bpy.types.Scene.modify_trajectory_by_pitch = bpy.props.BoolProperty(
		name        = "[spr]Modify Trajectory by Pitch",
		description = "Modify Trajectory by Pitch",
		default     = 0 )
	
	bpy.types.Scene.trajectory_scale_enabled = bpy.props.BoolProperty(
	name        = "[spr]trajectory scale enabled",
	description ="[Spr]",
	default     = 0)
	
	bpy.types.Object.trajectory_scale = bpy.props.StringProperty(
	name        = "[spr]Set trajectory scale",
	description = "[Spr]",
	default     = "1.0")
	
	# Scene
		
	# -- BpyObject Enable --
	bpy.types.Scene.spr_use_object_wrapper = bpy.props.BoolProperty(
		name        = "[spr]Assure Availability",
		description = "Assure bpy object is available before any access, using BpyObject wrapper.",
		default     = 1 )
		
	# -- Migration Flag --
	bpy.types.Scene.spr_need_migration = bpy.props.BoolProperty(
		name        = "[spr]need migration",
		description = "Made with old version of SprBlender, and need migration to SprBlender 2.0.",
		default     = 0 )

	# -- Run Simulation --
	bpy.types.Scene.spr_step_enabled = bpy.props.BoolProperty(
		name        = "[spr]physics step enabled",
		description ="[Spr]Run Physics Simulation.",
		default     = 0)
	bpy.types.Scene.spr_minimal_sync = bpy.props.BoolProperty(
		name        = "[spr]minimal sync mode",
		description ="[Spr]Only synchronize minimal states (no edit, high-speed).",
		default     = 0)
	bpy.types.Scene.spr_no_sync = bpy.props.BoolProperty(
		name        = "[spr]no sync mode",
		description ="[Spr]no synchronize  states (no edit, high-speed).",
		default     = 0)
	bpy.types.Scene.spr_num_iteration = bpy.props.IntProperty(
		name        = "[spr]Num Iteration default=15",
		description ="[Spr]LCP Num Iteration. Default=15",
		min = 1,
		default     = 15)
	bpy.types.Scene.spr_throw_enabled = bpy.props.BoolProperty(
		name        = "[spr]throw enabled",
		description ="[Spr]Check to enable throwing objecs.(Set Velocity)",
		default     = 0)
	bpy.types.Scene.spr_impact_threshold = bpy.props.FloatProperty(
		name        = "[spr]Impact Threshold default=10.0",
		description ="[Spr]Impact Threshold default=10.0",
		min = 0,
		default     = 10.0)
	bpy.types.Scene.spr_friction_threshold = bpy.props.FloatProperty(
		name        = "[spr]Friction Threshold default=0.01",
		description ="[Spr]Friction Threshold default=0.01",
		min = 0,
		default     = 0.01)
	bpy.types.Scene.spr_contact_tolerance = bpy.props.FloatProperty(
		name        = "[spr]Contact Tolerance default=0.002",
		description ="[Spr]Contact Tolerance default=0.002",
		min = 0,
		default     = 0.002)
	bpy.types.Scene.spr_max_velocity = bpy.props.FloatProperty(
		name        = "[spr]Max Velocity default=Inf",
		description ="[Spr]Max Velocity default=Inf",
		min = 0,
		default     = 3e+39)
	bpy.types.Scene.spr_max_angular_velocity = bpy.props.FloatProperty(
		name        = "[spr]Max Angular Velocity default=100",
		description ="[Spr]Max Angular Velocity default=100",
		min = 0,
		default     = 100)

	# -- Info --
	bpy.types.Scene.spr_op_cps_count = bpy.props.FloatProperty(
		name        = "[spr]Operator CPS Count",
		description ="[Spr]Operator CPS Count",
		default     = 0)
	bpy.types.Scene.spr_phys_cps_count = bpy.props.FloatProperty(
		name        = "[spr]Physics CPS Count",
		description ="[Spr]Physics CPS Count",
		default     = 0)

	# -- Recording (Key frame)
	bpy.types.Scene.spr_record = bpy.props.BoolProperty(
		name        = "[spr]Enable Recording KeyFrame",
		description ="[Spr]Enable Recording KeyFrame",
		default     = 0)
	bpy.types.Scene.spr_record_to_cache = bpy.props.BoolProperty(
		name        = "[spr]Use Cache for Recording",
		description ="[Spr]Use Cache for Recording",
		default     = 1)
	bpy.types.Scene.spr_recording_frame = bpy.props.IntProperty(
		name        = "[spr]Recording Frame",
		description ="[Spr]Recording Frame",
		min = 0,
		default     = 0)
	bpy.types.Scene.spr_record_every_n_steps = bpy.props.IntProperty(
		name        = "[spr]Record Keyframe Every N Steps",
		description ="[Spr]Record Keyframe Every N Steps",
		min = 1,
		default     = 1)

	# -- Enable Functions (Script, IK, Creature, Pliant)
	bpy.types.Scene.spr_run_scripts_enabled = bpy.props.BoolProperty(
		name        = "[spr]run scripts enabled",
		description ="[Spr]",
		default     = 0)
	
	bpy.types.Scene.spr_ik_engine_enabled = bpy.props.BoolProperty(
		name        = "[spr]IK Engine enabled",
		description ="[Spr]",
		default     = 0)

	bpy.types.Scene.spr_creature_enabled = bpy.props.BoolProperty(
		name        = "[spr]creature enabled",
		description ="[Spr]",
		default     = 0)

	bpy.types.Scene.spr_pliant_enabled = bpy.props.BoolProperty(
		name        = "[spr]Pliant Motion enabled",
		description ="[Spr]",
		default     = 0)

	# -- Debug Draw
	bpy.types.Scene.spr_debug_draw_enabled = bpy.props.BoolProperty(
		name        = "[spr]debug draw enabled",
		description ="[Spr]",
		default     = 0)
	
	bpy.types.Scene.spr_debug_draw_solid_enabled = bpy.props.BoolProperty(
		name        = "[spr]debug draw of PHSolid enabled",
		description ="[Spr]",
		default     = 0)

	bpy.types.Scene.spr_debug_draw_limit_enabled = bpy.props.BoolProperty(
		name        = "[spr]debug draw of Limit enabled",
		description ="[Spr]",
		default     = 0)

	bpy.types.Scene.spr_debug_draw_ik_enabled = bpy.props.BoolProperty(
		name        = "[spr]debug draw of IK enabled",
		description ="[Spr]",
		default     = 0)

	bpy.types.Scene.spr_debug_draw_force_enabled = bpy.props.BoolProperty(
		name        = "[spr]debug draw of Force enabled",
		description ="[Spr]",
		default     = 0)


def register_object_properties():
	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Common for Object
	bpy.types.Object.spr_object_type = bpy.props.EnumProperty(
		name        = "[spr] Object Type",
		description = "Set Object as Springhead Solid or Joint.",
		items = [
			# ("value", "name",  "description")
			("(Select Physics Type)", "(Select Physics Type)", "(Select Physics Type)"),
			(  "Solid", "Solid", "Solid"),
			(  "Joint", "Joint", "Joint") ])

	bpy.types.Object.spr_object_id = bpy.props.StringProperty(
		name        = "[spr]Object ID",
		description = "[Spr]Object ID",
		default     = "")

	# -- Hold & Apply --
	bpy.types.Object.alive = bpy.props.BoolProperty(
		name        = "[spr]Object Alive",
		description = "Temp. Var",
		default     = 1 )

def register_solid_properties():
	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Solid

	# -- Hold & Apply --
	bpy.types.Object.spr_solid_props_hold = bpy.props.BoolProperty(
		name        = "[spr]Solid Properties Hold",
		description = "Pause applying bpy setting into Springhead solid.",
		default     = 0 )

	bpy.types.Object.spr_solid_props_apply = bpy.props.BoolProperty(
		name        = "[spr]Solid Properties Apply",
		description = "Apply bpy solid setting once, during hold state",
		default     = 0 )


	# -- Static & Shape --
	bpy.types.Object.spr_solid_static = bpy.props.BoolProperty(
		name        = "[spr]Static Solid",
		description = "Do not apply dynamics (e.g. Fixed object as a floor, Cursor, etc.)",
		default     = 0 )

	bpy.types.Object.spr_shape_type = bpy.props.EnumProperty(
		name        = "[spr]Shape Type",
		description = "Shape Type (Box/Sphere/Convex)",
		items = [
			# ("value",   "name",   "description")
			(   "None",      "None",      "None"         ),
			(   "Box",       "Box",       "Box"          ),
			(   "Sphere",    "Sphere",    "Sphere"       ),
			(   "Convex",    "Convex",    "Convex Mesh"  ),
			(   "RoundCone", "RoundCone", "Round Cone"   ) ])

	bpy.types.Object.spr_roundcone_target_name = bpy.props.StringProperty(
		name        = "[spr]roundcone shape target name",
		description = "[Spr]",
		default     = "")


	# -- CoM --
	bpy.types.Object.spr_center_x = bpy.props.FloatProperty(
		name        = "[spr]CoM x",
		description = "Center of Mass : x",
		default     = 0 )

	bpy.types.Object.spr_center_y = bpy.props.FloatProperty(
		name        = "[spr]CoM y",
		description = "Center of Mass : y",
		default     = 0 )

	bpy.types.Object.spr_center_z = bpy.props.FloatProperty(
		name        = "[spr]CoM z",
		description = "Center of Mass : z",
		default     = 0 )


	# -- Inertia -- 
	bpy.types.Object.spr_autoset_inertia = bpy.props.BoolProperty(
		name        = "[spr]Automatic Inertia Setting",
		description = "Set Solid Inertia with Automatic Calculation",
		default     = 1 )


	bpy.types.Object.spr_inertia_x  = bpy.props.FloatProperty(
		name        = "[spr]Inertia x",
		description = "Inertia : x",
		min         = 0.000001,
		default     = 1 )

	bpy.types.Object.spr_inertia_y  = bpy.props.FloatProperty(
		name        = "[spr]Inertia y",
		description = "Inertia : y",
		min         = 0.000001,
		default     = 1 )

	bpy.types.Object.spr_inertia_z  = bpy.props.FloatProperty(
		name        = "[spr]Inertia z",
		description = "Inertia : z",
		min         = 0.000001,
		default     = 1 )

	bpy.types.Object.spr_inertia_xy = bpy.props.FloatProperty(
		name        = "[spr]Inertia xy",
		description = "Inertia : xy",
		min         = 0,
		default     = 0 )

	bpy.types.Object.spr_inertia_xz = bpy.props.FloatProperty(
		name        = "[spr]Inertia xz",
		description = "Inertia : xz",
		min         = 0,
		default     = 0 )

	bpy.types.Object.spr_inertia_yx = bpy.props.FloatProperty(
		name        = "[spr]Inertia yx",
		description = "Inertia : yx",
		min         = 0,
		default     = 0 )

	bpy.types.Object.spr_inertia_yz = bpy.props.FloatProperty(
		name        = "[spr]Inertia yz",
		description = "Inertia : yz",
		min         = 0,
		default     = 0 )

	bpy.types.Object.spr_inertia_zx = bpy.props.FloatProperty(
		name        = "[spr]Inertia zx",
		description = "Inertia : zx",
		min         = 0,
		default     = 0 )

	bpy.types.Object.spr_inertia_zy = bpy.props.FloatProperty(
		name        = "[spr]Inertia zy",
		description = "Inertia : zy",
		min         = 0,
		default     = 0 )


	# -- Control -- 
	## -- Show
	bpy.types.Object.spr_show_solid_control = bpy.props.BoolProperty(
		name        = "[spr]Show Solid Control",
		description = "Show Springhead Solid Control Panel",
		default     = 0 )

	## -- Hold & Apply
	bpy.types.Object.spr_solid_velocity_hold = bpy.props.BoolProperty(
		name        = "[spr]Hold Velocity",
		description = "Hold Applying Solid Velocity Control",
		default     = 1 )
	bpy.types.Object.spr_solid_velocity_apply = bpy.props.BoolProperty(
		name        = "[spr]Apply Velocity",
		description = "Apply once Solid Velocity Control",
		default     = 0 )
	bpy.types.Object.spr_solid_velocity_edit = bpy.props.BoolProperty(
		name        = "[spr]Edit Velocity",
		description = "Edit Solid Velocity Control",
		default     = 0 )

	bpy.types.Object.spr_solid_angvelocity_hold = bpy.props.BoolProperty(
		name        = "[spr]Hold Angular Velocity",
		description = "Hold Applying Solid Angular Velocity Control",
		default     = 1 )
	bpy.types.Object.spr_solid_angvelocity_apply = bpy.props.BoolProperty(
		name        = "[spr]Apply Angular Velocity",
		description = "Apply once Solid Angular Velocity Control",
		default     = 0 )
	bpy.types.Object.spr_solid_angvelocity_edit = bpy.props.BoolProperty(
		name        = "[spr]Apply Angular Velocity",
		description = "Edit Solid Angular Velocity Control",
		default     = 0 )

	bpy.types.Object.spr_solid_force_hold = bpy.props.BoolProperty(
		name        = "[spr]Hold Force",
		description = "Hold Applying Solid Force Control",
		default     = 1 )
	bpy.types.Object.spr_solid_force_apply = bpy.props.BoolProperty(
		name        = "[spr]Apply Force",
		description = "Apply once Solid Force Control",
		default     = 0 )
	bpy.types.Object.spr_solid_force_edit = bpy.props.BoolProperty(
		name        = "[spr]Apply Force",
		description = "Edit Solid Force Control",
		default     = 0 )

	bpy.types.Object.spr_solid_torque_hold = bpy.props.BoolProperty(
		name        = "[spr]Hold Torque",
		description = "Hold Applying Solid Torque Control",
		default     = 1 )
	bpy.types.Object.spr_solid_torque_apply = bpy.props.BoolProperty(
		name        = "[spr]Apply Torque",
		description = "Apply once Solid Torque Control",
		default     = 0 )
	bpy.types.Object.spr_solid_torque_edit = bpy.props.BoolProperty(
		name        = "[spr]Apply Force",
		description = "Edit Solid Torque Control",
		default     = 0 )

	## -- Control Flags
	bpy.types.Object.spr_solid_set_force_point	= bpy.props.BoolProperty(
		name        = "[spr]Solid Set Force Point",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_velocity_local = bpy.props.BoolProperty(
		name        = "[spr]Solid Velocity Local",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_ang_velocity_local = bpy.props.BoolProperty(
		name        = "[spr]Solid Angular Velocity Local",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_force_local = bpy.props.BoolProperty(
		name        = "[spr]Solid Add Force Local",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_torque_local = bpy.props.BoolProperty(
		name        = "[spr]Solid Add Torque Local",
		description = "[Spr]",
		default     = 0)

	## -- Values
	bpy.types.Object.spr_solid_velocity_x = bpy.props.FloatProperty(
		name        = "[spr]Solid Velocity X",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_velocity_y = bpy.props.FloatProperty(
		name        = "[spr]Solid Velocity Y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_velocity_z = bpy.props.FloatProperty(
		name        = "[spr]Solid Velocity Z",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_solid_angular_velocity_x = bpy.props.FloatProperty(
		name        = "[spr]Solid Angular Velocity X",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_angular_velocity_y = bpy.props.FloatProperty(
		name        = "[spr]Solid Angular Velocity Y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_angular_velocity_z = bpy.props.FloatProperty(
		name        = "[spr]Solid Angular Velocity Z",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_solid_force_x = bpy.props.FloatProperty(
		name        = "[spr]Solid Force X",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_force_y = bpy.props.FloatProperty(
		name        = "[spr]Solid Force Y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_force_z = bpy.props.FloatProperty(
		name        = "[spr]Solid Force Z",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_solid_force_point_x = bpy.props.FloatProperty(
		name        = "[spr]Solid Force Point X",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_force_point_y = bpy.props.FloatProperty(
		name        = "[spr]Solid Force Point Y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_force_point_z = bpy.props.FloatProperty(
		name        = "[spr]Solid Force Point Z",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_solid_torque_x = bpy.props.FloatProperty(
		name        = "[spr]Solid Torque X",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_torque_y = bpy.props.FloatProperty(
		name        = "[spr]Solid Torque Y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_solid_torque_z = bpy.props.FloatProperty(
		name        = "[spr]Solid Torque Z",
		description = "[Spr]",
		default     = 0)


	# -- Material --
	bpy.types.Material.spr_friction_static = bpy.props.FloatProperty(
		name        = "[spr]Static Friction",
		description = "Static friction coefficient",
		min         = 0,
		default     = 0.5 )


	# -- Misc -- 
	bpy.types.Object.spr_use_matrix_world = bpy.props.BoolProperty(
		name        = "[spr]Use World Matrix",
		description = "Use Matrix of World coordinate",
		default     = 0 )

	bpy.types.Object.spr_connect_interface = bpy.props.EnumProperty(
		name        = "[spr]Connect Interface",
		items = [
			# ("value",        "name",           "description")
			("None",           "None",           "None"),
			("SpaceNavigator", "SpaceNavigator", "Space Navigator"),
			("SPIDAR",         "SPIDAR",         "SPIDAR"),
			("SPIDAR2",        "SPIDAR2",        "2nd SPIDAR"),
			("Xbox",           "Xbox",           "Xbox Controller"),
			("Falcon",         "Falcon",         "Novient Falcon") ])


def register_joint_properties():
	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Joint

	# -- Hold & Apply --
	bpy.types.Object.spr_joint_props_hold = bpy.props.BoolProperty(
		name        = "[spr]Joint Properties Hold Mode",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_props_apply = bpy.props.BoolProperty(
		name        = "[spr]Joint Properties Apply",
		description = "[Spr]",
		default     = 0)

	# -- Flags --
	bpy.types.Object.spr_joint_enabled = bpy.props.BoolProperty(
		name        = "[spr]Joint Enabled",
		description = "[Spr]",
		default     = 1)
	bpy.types.Object.spr_joint_collision = bpy.props.BoolProperty(
		name        = "[spr]joint collision",
		description = "[Spr]",
		default     = 1)
	bpy.types.Object.spr_joint_cyclic = bpy.props.BoolProperty(
		name        = "[spr]Joint Cyclic",
		description = "[Spr]Joint Cyclic(Hinge)",
		default     = 0)
	bpy.types.Object.spr_joint_aba = bpy.props.BoolProperty(
		name        = "[spr]Joint ABA",
		description = "[Spr]Joint ABA",
		default     = 0)

	# -- Type --
	bpy.types.Object.spr_joint_mode = bpy.props.EnumProperty(
		name        = "[spr]Joint Type",
		description = "Type of Joint",
		items = [
			# ("value", "name",   "description")
			("Ball",    "Ball",   "ball joint"),
			("Hinge",   "Hinge",  "hinge joint"),
			("Slider",  "Slider", "slider joint"),
			("Spring",  "Spring", "spring")        ])

	# -- Plug & Socket
	bpy.types.Object.spr_joint_socket_target = bpy.props.EnumProperty(
		name        = "[spr]spr joint socket target type",
		items = [
				# ("value","name","description")
				("Solid Name", "Solid Name", "Specify Name of Solid Object"), 
				("Axis Name",  "Axis Name",  "Specify Name of Axis Object") ])
	bpy.types.Object.spr_joint_socket_target_name = bpy.props.StringProperty(
		name        = "[spr]joint socket target name",
		description = "[Spr]",
		default     = "")

	bpy.types.Object.spr_joint_plug_target = bpy.props.EnumProperty(
		name        = "[spr]spr joint plug target type",
		items = [
				# ("value","name","description")
				("Parent","Parent","Parent")  ])
	bpy.types.Object.spr_joint_plug_target_name = bpy.props.StringProperty(
		name        = "[spr]joint plug target name",
		description = "[Spr]",
		default     = "")


	# -- Spring & Damper -- 
	bpy.types.Object.spr_spring = bpy.props.FloatProperty(
		name        = "[spr]spring",
		description = "[Spr]",
		min         = 0,
		#max = 9999,
		default     = 0)
	bpy.types.Object.spr_spring_x = bpy.props.FloatProperty(
		name        = "[spr]spring X",
		description = "[Spr]",
		min         = 0,
		default     = 0)
	bpy.types.Object.spr_spring_y = bpy.props.FloatProperty(
		name        = "[spr]spring Y",
		description = "[Spr]",
		min         = 0,
		default     = 0)
	bpy.types.Object.spr_spring_z = bpy.props.FloatProperty(
		name        = "[spr]spring Z",
		description = "[Spr]",
		min         = 0,
		default     = 0)
	bpy.types.Object.spr_spring_ori = bpy.props.FloatProperty(
		name        = "[spr]Spring Ori",
		description = "[Spr]",
		min         = 0,
		default     = 0)

	bpy.types.Object.spr_damper = bpy.props.FloatProperty(
		name        = "[spr]damper",
		description = "[Spr]",
		min         = 0,
		#max = 9999,
		default     = 0)
	bpy.types.Object.spr_damper_x = bpy.props.FloatProperty(
		name        = "[spr]damper X",
		description = "[Spr]",
		min         = 0,
		default     = 0)
	bpy.types.Object.spr_damper_y = bpy.props.FloatProperty(
		name        = "[spr]damper Y",
		description = "[Spr]",
		min         = 0,
		default     = 0)
	bpy.types.Object.spr_damper_z = bpy.props.FloatProperty(
		name        = "[spr]damper Z",
		description = "[Spr]",
		min         = 0,
		default     = 0)
	bpy.types.Object.spr_damper_ori = bpy.props.FloatProperty(
		name        = "[spr]Damper Ori",
		description = "[Spr]",
		min         = 0,
		default     = 0)


	# -- Max Force -- 
	bpy.types.Object.spr_joint_max_force = bpy.props.FloatProperty(
		name        = "[spr]joint max force",
		description = "[Spr]",
		default     = 3e+39,
		min         = 0)


	# -- Limit -- 
	bpy.types.Object.spr_joint_limit_enable = bpy.props.BoolProperty(
		name        = "[spr]Springhead Joint Limit Enabled",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_limit_spring = bpy.props.FloatProperty(
		name        = "[spr]Joint Limit Spring",
		description = "[Spr]",
		min         = 0,
		default     = 10000)
	bpy.types.Object.spr_limit_damper = bpy.props.FloatProperty(
		name        = "[spr]Joint Limit Damper",
		description = "[Spr]",
		min         = 0,
		default     = 10000)

	bpy.types.Object.spr_limit_range_max = bpy.props.FloatProperty(
		name        = "[spr]joint limit range Max",
		description = "[Spr]",
		default     = 3e+39)
	bpy.types.Object.spr_limit_range_min = bpy.props.FloatProperty(
		name        = "[spr]joint limit range min",
		description = "[Spr]",
		default     = -3e+39)

	bpy.types.Object.spr_limit_swing_max = bpy.props.FloatProperty(
		name        = "[spr]joint limit swing Max",
		description = "[Spr]",
		default     = 3e+39)
	bpy.types.Object.spr_limit_swing_min = bpy.props.FloatProperty(
		name        = "[spr]joint limit swing min",
		description = "[Spr]",
		default     = -3e+39)

	bpy.types.Object.spr_limit_twist_max = bpy.props.FloatProperty(
		name        = "[spr]joint limit twist Max",
		description = "[Spr]",
		default     = 3e+39)
	bpy.types.Object.spr_limit_twist_min = bpy.props.FloatProperty(
		name        = "[spr]joint limit twist min",
		description = "[Spr]",
		default     = -3e+39)


	# -- Elastic Joint -- 
	## SprBlender的には未実装．将来使うための予約
	bpy.types.Object.spr_second_damper = bpy.props.FloatProperty(
		name        = "[spr]Joint Second Damper",
		description = "[Spr]",
		min         = 0.001,
		default     = 1.0)
	bpy.types.Object.spr_second_damper_x = bpy.props.FloatProperty(
		name        = "[spr]Ball Joint Second Damper x",
		description = "[Spr]",
		min         = 0.001,
		default     = 1.0)
	bpy.types.Object.spr_second_damper_y = bpy.props.FloatProperty(
		name        = "[spr]Joint Second Damper y",
		description = "[Spr]",
		min         = 0.001,
		default     = 1.0)
	bpy.types.Object.spr_second_damper_z = bpy.props.FloatProperty(
		name        = "[spr]Joint Second Damper z",
		description = "[Spr]",
		min         = 0.001,
		default     = 1.0)
	bpy.types.Object.spr_yield_stress = bpy.props.FloatProperty(
		name        = "[spr]joint yield stress",
		description = "[Spr]",
		min         = 0,
		default     = 10**10)
	bpy.types.Object.spr_hardness_rate = bpy.props.FloatProperty(
		name        = "[spr]joint hardness rate",
		description = "[Spr]",
		min         = 0.001,
		default     = 1.0)
	

	# -- Control -- 
	## -- Show
	bpy.types.Object.spr_show_joint_control = bpy.props.BoolProperty(
		name        = "[spr]Show Springhead Joint Control Panel",
		description = "[Spr]",
		default     = 0)

	## -- Hold & Apply
	bpy.types.Object.spr_joint_targetposition_hold = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Hold Target Position",
		description = "[Spr]",
		default     = 1)
	bpy.types.Object.spr_joint_targetposition_apply = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Apply Target Position",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_targetposition_edit = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Edit Target Position",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_joint_velocity_hold = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Hold Velocity",
		description = "[Spr]",
		default     = 1)
	bpy.types.Object.spr_joint_velocity_apply = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Apply Velocity",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_velocity_edit = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Edit Target Velocity",
		description = "[Spr]",
		default     = 0)
		
	bpy.types.Object.spr_joint_offsetforce_hold = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Hold Offset Force",
		description = "[Spr]",
		default     = 1)
	bpy.types.Object.spr_joint_offsetforce_apply = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Apply Offset Force",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_offsetforce_edit = bpy.props.BoolProperty(
		name        = "[spr]Joint Control Edit Offset Force",
		description = "[Spr]",
		default     = 0)
		
	## -- Values
	bpy.types.Object.spr_joint_target_position = bpy.props.FloatProperty(
		name        = "[spr]joint target position",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_target_position_x = bpy.props.FloatProperty(
		name        = "[spr]joint target position x(deg)",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_target_position_y = bpy.props.FloatProperty(
		name        = "[spr]joint target position y(deg)",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_target_position_z = bpy.props.FloatProperty(
		name        = "[spr]joint target position z(deg)",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_joint_target_velocity = bpy.props.FloatProperty(
		name        = "[spr]joint target velocity",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_target_velocity_x = bpy.props.FloatProperty(
		name        = "[spr]joint target velocity x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_target_velocity_y = bpy.props.FloatProperty(
		name        = "[spr]joint target velocity y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_target_velocity_z = bpy.props.FloatProperty(
		name        = "[spr]joint target velocity z",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_joint_offset_force = bpy.props.FloatProperty(
		name        = "[spr]joint offset force",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_offset_force_x = bpy.props.FloatProperty(
		name        = "[spr]joint offset force x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_offset_force_y = bpy.props.FloatProperty(
		name        = "[spr]joint offset force y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_joint_offset_force_z = bpy.props.FloatProperty(
		name        = "[spr]joint offset force z",
		description = "[Spr]",
		default     = 0)


def register_ik_properties():
	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Engine
	bpy.types.Object.spr_ik_enabled = bpy.props.BoolProperty(
		name        = "[spr]IK enabled",
		description = "[Spr]",
		default     = 0)

	bpy.types.Scene.spr_ik_iteration_num = bpy.props.IntProperty(
		name        = "[spr]IK Iteration Num",
		description = "[Spr]",
		min = 1,
		default     = 1)
	bpy.types.Scene.spr_ik_max_velocity = bpy.props.FloatProperty(
		name        = "[spr]IK Max Velocity default=20",
		description = "[Spr]IK Max Velocity default=20",
		min = 0,
		default     = 20)
	bpy.types.Scene.spr_ik_max_angular_velocity = bpy.props.FloatProperty(
		name        = "[spr]IK Max Angular Velocity default=10",
		description = "[Spr]IK Max Angular Velocity default=10",
		min = 0,
		default     = 10)
	bpy.types.Scene.spr_ik_regularize_param = bpy.props.FloatProperty(
		name        = "[spr]IK Regularization Parameter default=0.7",
		description = "[Spr]IK Regularization Parameter default=0.7",
		min = 0,
		default     = 0.7)
	bpy.types.Scene.spr_ik_iter_cutoff_angvel = bpy.props.FloatProperty(
		name        = "[spr]IK Iter Cutoff default=0.01",
		description = "[Spr]IK Iter Cutoff default=0.01",
		min = 0,
		default     = 0.01)

	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# IK Actuator
	bpy.types.Object.spr_ik_bias = bpy.props.FloatProperty(
		name        = "[spr]IK bias",
		description = "[Spr]",
		min         = 0.001,	#ゼロダメ
		default     = 1.0)
	bpy.types.Object.spr_ik_pullback_rate = bpy.props.FloatProperty(
		name        = "[spr]IK Pullback Rate",
		description = "[Spr]",
		min         = 0.0,
		max         = 1.0,
		default     = 0.1)

	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# IK EndEffector

	# -- Flags --
	bpy.types.Object.spr_ik_pos_control_enabled = bpy.props.BoolProperty(
		name        = "[spr]IK Position Control enabled",
		description = "[Spr]",
		default     = 1)

	bpy.types.Object.spr_ik_ori_control_enabled = bpy.props.BoolProperty(
		name        = "[spr]IK Orientation Control enabled",
		description = "[Spr]",
		default     = 0)

	# -- Ori Control Mode --
	bpy.types.Object.spr_ik_ori_control_mode = bpy.props.EnumProperty(
		name        = "[spr]IK Orientation Control Mode",
		items = [
			("Quaternion", "Quaternion", "Quaternion"),
			("Direction",  "Direction",  "Direction"),
			("LookAt",     "LookAt",     "LookAt") ])

	# -- Target Local Position --
	bpy.types.Object.spr_ik_tip_use_obj = bpy.props.BoolProperty(
		name        = "[spr]IK : Use object to specify Tip Pos/Dir",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_ik_target_local_pos_x = bpy.props.FloatProperty(
		name        = "[spr]IK target local position x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_ik_target_local_pos_y = bpy.props.FloatProperty(
		name        = "[spr]IK target local position y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_ik_target_local_pos_z = bpy.props.FloatProperty(
		name        = "[spr]IK target local position z",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_ik_target_local_dir_x = bpy.props.FloatProperty(
		name        = "[spr]IK target local direction x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_ik_target_local_dir_y = bpy.props.FloatProperty(
		name        = "[spr]IK target local direction y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_ik_target_local_dir_z = bpy.props.FloatProperty(
		name        = "[spr]IK target local direction z",
		description = "[Spr]",
		default     = 1)

	bpy.types.Object.spr_ik_tip_object_name = bpy.props.StringProperty(
		name        = "[spr]IK Tip Object Name",
		description = "[Spr]",
		default     = "")

	# -- Position Priority --
	bpy.types.Object.spr_ik_position_priority = bpy.props.FloatProperty(
		name		= "[spr]IK position priority",
		description	= "[Spr]",
		default		= 1)
		

	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# IK EndEffector Control

	# -- Show --
	bpy.types.Object.spr_show_ik_control = bpy.props.BoolProperty(
		name        = "[spr]Show IK Control",
		description = "Show Springhead IK Control Panel",
		default     = 0)

	# -- Hold & Apply --
	bpy.types.Object.spr_ik_targetpose_hold = bpy.props.BoolProperty(
		name        = "[spr]IK TargetPose Hold",
		description = "Hold Applying IK TargetPose",
		default     = 1)
	bpy.types.Object.spr_ik_targetpose_apply = bpy.props.BoolProperty(
		name        = "[spr]IK TargetPose Apply",
		description = "Apply once IK TargetPose",
		default     = 0)
	bpy.types.Object.spr_ik_targetpose_edit = bpy.props.BoolProperty(
		name        = "[spr]IK TargetPose Edit",
		description = "Edit IK TargetPose",
		default     = 0)

	# -- Target Object --
	bpy.types.Object.spr_ik_target_object_enabled = bpy.props.BoolProperty(
		name        = "[spr]IK Target Object enabled",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_ik_target_object_name = bpy.props.StringProperty(
		name        = "[spr]IK Target Object Name",
		description = "[Spr]",
		default     = "")

	# -- Value --
	bpy.types.Object.spr_ik_target_pos_x = bpy.props.FloatProperty(
		name        = "[spr]IK target position x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_ik_target_pos_y = bpy.props.FloatProperty(
		name        = "[spr]IK target position y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_ik_target_pos_z = bpy.props.FloatProperty(
		name        = "[spr]IK target position z",
		description = "[Spr]",
		default     = 0)

	bpy.types.Object.spr_ik_target_ori_x = bpy.props.FloatProperty(
		name        = "[spr]IK target orientation x",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_ik_target_ori_y = bpy.props.FloatProperty(
		name        = "[spr]IK target orientation y",
		description = "[Spr]",
		default     = 0)
	bpy.types.Object.spr_ik_target_ori_z = bpy.props.FloatProperty(
		name        = "[spr]IK target orientation z",
		description = "[Spr]",
		default     = 0)


def register_creature_properties():
	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# Creature

	# -- Enable --
	bpy.types.Group.spr_creature_group = bpy.props.BoolProperty(
		name        = "[spr]creature group",
		description = "[Spr]",
		default     = 0)
	
	# -- Spring & Damper Ratio --
	bpy.types.Group.spr_creature_spring_damper_ratio = bpy.props.FloatProperty(
		name        = "[spr]creature spring/damper ratio",
		description = "[Spr]",
		min         = 0.1,
		max         = 500,
		default     = 1)

	bpy.types.Group.spr_creature_spring_ratio = bpy.props.FloatProperty(
		name        = "[spr]creature spring ratio",
		description = "[Spr]",
		min         = 0,
		max         = 500,
		default     = 1)

	bpy.types.Group.spr_creature_damper_ratio = bpy.props.FloatProperty(
		name        = "[spr]creature damper ratio",
		description = "[Spr]",
		min         = 0,
		max         = 500,
		default     = 1)

	# -- Parameters --
	bpy.types.Group.spr_creature_parameters = bpy.props.CollectionProperty(
		name        = "[spr]creature parameters",
		description = "[Spr]",
		type=CreatureParameter)

	# -- Controllers --
	bpy.types.Group.spr_controllers = bpy.props.CollectionProperty(
		name        = "[spr]creature controllers",
		description = "[Spr]",
		type=CreatureController)

	# -- Visualizers --
	bpy.types.Group.spr_visualizers = bpy.props.CollectionProperty(
		name        = "[spr]creature visualizers",
		description = "[Spr]",
		type=CreatureVisualizer)

	# -- Onomatopoeia --
	bpy.types.Group.spr_creature_onomatopoeia = bpy.props.StringProperty(
		name        = "[spr]Onomatopoeia",
		description = "[Spr]creature impression",
		default     = "")

	# -- MappingOnomatopoeia --
	bpy.types.Group.spr_creature_selected_onomatopoeia = bpy.props.StringProperty(
		name        = "[spr]Onomatopoeia",
		description = "[Spr]creature mapping impression",
		default     = "")

	# -- SavingFileName --
	bpy.types.Group.spr_creature_save_filename = bpy.props.StringProperty(
		name        = "[spr]FileName",
		description = "[Spr]name mapping impression",
		default     = "")

	# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
	# CRBone
	bpy.types.Object.spr_crbone_label = bpy.props.StringProperty(
		name        = "[spr]Label for Creature Bone",
		description = "[Spr]",
		default     = "None")


# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
# Creature Parameter
class CreatureParameter(bpy.types.PropertyGroup):
	creaturename = bpy.props.StringProperty(name="Creature Name", default="")
	name         = bpy.props.StringProperty(name="Property Name", default="")
	value        = bpy.props.FloatProperty(name="Property Value", default=0, min=0, max=200)
bpy.utils.register_class(CreatureParameter)


# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
# Creature Controllers
class CreatureController(bpy.types.PropertyGroup):
	creaturename = bpy.props.StringProperty(name="Creature Name",   default="")
	name         = bpy.props.StringProperty(name="Controller Name", default="")
	type         = bpy.props.EnumProperty(
		name="Controller Type", 
		items=[("None","None","None"),
			   ("Reach","Reach","Reach")] )
	visualize    = bpy.props.BoolProperty(  name="Visualize",             default=1)
	target       = bpy.props.StringProperty(name="Control Target Object", default="")

	# for Reach Controller
	reach_speed  = bpy.props.FloatProperty( name="Average Speed",         default=0.2)
bpy.utils.register_class(CreatureController)


# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
# Visualizer
class CreatureVisualizer(bpy.types.PropertyGroup):
	creaturename = bpy.props.StringProperty(name="Creature Name", default="")
	name         = bpy.props.StringProperty(name="Visualizer Name", default="")
	type         = bpy.props.EnumProperty(
		name="Property Value", 
		items=[("None","None","None"),
			   ("FOV","FOV","FOV"),
			   ("Attention","Attention","Attention"),
			   ("Magnitude","Magnitude","Magnitude"),
			   ("Axis","Axis","Axis"),
			   ("Graph","Graph","Graph")] )
	target       = bpy.props.StringProperty(name="Target Object Name", default="")
	show         = bpy.props.BoolProperty(name="Show", default=1)
	# for FOV
	fov_param_name_horiz = bpy.props.StringProperty(name="Parameter Name for Horizontal FOV", default="")
	fov_param_name_vert  = bpy.props.StringProperty(name="Parameter Name for Vertical FOV",   default="")
bpy.utils.register_class(CreatureVisualizer)


