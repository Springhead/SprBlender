import spb

from Spr                   import *
from spb.abbrev            import *
from spb.utils             import *
from random                import *

from spb.ai.animationgenerator       import *
from spb.ai.walktrajectorycontroller import *
from spb.ai.perception               import *
from spb.ai.lookcontroller           import *
from spb.ai.eatcontroller            import *
from spb.ai.touchcontroller          import *
from spb.ai.footstepcontroller       import *
from spb.ai.grabcontroller           import *
from spb.ai.reachcontroller          import *

class AIBase:
	def set_config(self, config):
		self.config = config

	def __init__(self):
		# Default Settings
		self.config = {
			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Creature and Body Settings
			'creature_name'               : 'Koguma',
			'no_contacts'                 : [
												('so_Waist'         , ['so_Chest'  ]),
												('so_LeftUpperLeg'  , ['so_Abdomen']),
												('so_RightUpperLeg' , ['so_Abdomen']),
												('so_LeftUpperArm'  , ['so_Head'   ]),
												('so_RightUpperArm' , ['so_Head'   ]),
												('so_LeftLowerArm'  , ['so_Head'   ]),
												('so_RightLowerArm' , ['so_Head'   ]),

												('so_RightUpperLeg' , ['so_LeftUpperLeg']),
												('so_RightFoot'     , ['so_LeftFoot']),

												('so_RightUpperLeg' , ['so_RightLowerLeg', 'so_RightFoot']),
												('so_LeftUpperLeg'  , ['so_LeftLowerLeg',  'so_LeftFoot']),
											],

			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Perception Settings
			'floor_name'                  : 'Floor',
			'attention_visualizer_name'   : 'Attention',


			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Look Settings
			'enable_look'                 : True,
			'head_name'                   : 'so_Head',
			'look_max_margin'             : rad(25),
			'look_margin_att_lower_th'    : 0.0,
			'look_margin_att_higher_th'   : 0.7,
			'head_look_ctl'               : 'HeadLook',
			'look_avg_speed'              : 5.0,
			'look_wait_vel'               : 5.0,
			'look_restart_vel'            : 2.5,


			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Eye Settings
			'enable_eyemovement'          : True,
			'eyes_name'                   : {'L':'so_LeftEye', 'R':'so_RightEye'},
			# 黒目が中心に来る時のx, yの値
			'lefteye_center_xy'           : Vec2d(-0.05,  0.08),
			'righteye_center_xy'          : Vec2d(-0.05, -0.08),
			'eye_limit_angle'             : rad(25),


			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Touch Settings
			'enable_touch'                : True,
			'hands_name'                  : {'L':'so_LeftHand', 'R':'so_RightHand'},
			'arms_joint_name'             : {'L':'jo_LeftUpperArm', 'R':'jo_RightUpperArm'},

			'hands_reach_ctl'             : {'LR':'HandsReach', 'L':'LeftReach', 'R':'RightReach'},
			'hand_reach_avg_speed'        : 30.0, #default : 15.0
			'hand_reach_wait_vel'         : 20.0,
			'hand_reach_restart_vel'      : 10.0,


			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Walk Settings
			'enable_walk'                 : True,
			'feet_name'                   : {'L':'so_LeftFoot', 'R':'so_RightFoot'},
			'base_name'                   : 'so_Base',
			'base_joint_name'             : 'jo_Waist',
			'waist_name'                  : 'so_Waist',
			'upper_body_names'            : [
												'so_Abdomen',
												'so_Chest',
												'so_Head',
												'so_RightUpperArm',
												'so_RightLowerArm',
												'so_RightHand',
												'so_LeftUpperArm',
												'so_LeftLowerArm',
												'so_LeftHand',
											],
			'walk_d_friction'             : 0.07,
			'walk_rotation_Kp'            : 100.0,
			'walk_rotation_Kd'            :   5.0,
			'walk_pole'                   : (-1, -2, -3, -4),
			'walk_max_angle_x'            : rad(30),
			'walk_max_angle_y'            : rad(30),
			'walk_max_velocity'           : 10.0,
			'walk_max_angvel'             : 10.0,

			'walk_force_apply_scale'      : 0.055,
			'walk_force_apply_max'        : 1000,

			'walk_dir_ang_diff_max'       : rad(10),

			'walk_traj_target_distance'   : 10.0,


			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----n
			# Grab Settings
			# * Enable Touch control when you want to use Grab control. *
			'enable_grab'                 : True,


			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Eat Settings
			# * Enable Look control when you want to use Eat control. *
			'enable_eat'                  : True,
			'head_ik_tips'                : {'Look':'ike_Head_Tip', 'Eat':'ike_Head_mouthTip'},
			'hands_ik_tips' : {'L':'ike_LeftHand_Tip', 'R':'ike_RightHand_Tip'},
			'max_eat_candidates'          : 5,
			'eat_start_distance'          : 4.0,
			'eat_resign_distance'         : 5.0,
			'eat_mouth_start_open'        : 4.0,
			'eat_mouth_compl_open'        : 1.5,
			'eat_complete_time'           : 0.8,
			'wait_after_eat'              : 2.0,

			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# FootStepSettings
			'foot_distance'               : 1.4111*2,
			'foot_height'                 : 0.6,
			'foot_up_height'              : 0.5,
			'max_pace'                    : 2.0,
			'low_pass_filter_alpha'       : 0.02,
			'walk_transition_threshold'   : 0.8,
			'pace_coefficient'            : 2.0,
			'fix_transition_threshold'    : 0.15,
			'fix_transition_timer'        : 20,
			'fix_time_step'               : 0.05,

			'head_reach_ctl'              : 'HeadReach',
			'head_reach_avg_speed'        : 10.0,
			'head_reach_wait_vel'         : 10.0,
			'head_reach_restart_vel'      :  5.0,
		}

	def init_petari(self):
		self.petari = PetariLeap()

	def init_body(self):
		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Body Settings

		print(self.config)

		for so1, lst in self.config['no_contacts']:
			if len(lst)==0:
				Scn.spr().SetContactMode(So[so1].spr(), 0)
			else:
				for so2 in lst:
					print(so1, so2)
					Scn.spr().SetContactMode(So[so1].spr(), So[so2].spr(), 0)


	def init_visualizer(self):
		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Visualizers

		self.visualizer   = Vis[self.config['attention_visualizer_name']]


	def init_perception(self):
		# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
		# Sensors

		self.touchsensor   = Cr[self.config['creature_name']].get_engine(CRTouchSensor, CRTouchSensorDesc())

		if self.config['enable_eyemovement']:
			visualSensorDesc = CRVisualSensorDesc()
			visualSensorDesc.limitDistance = 120
			self.visualsensorL = Cr[self.config['creature_name']].get_engine(CRVisualSensor, visualSensorDesc, 0)
			self.visualsensorL.SetSolid(So[self.config['eyes_name']['L']].spr())

			self.visualsensorR = Cr[self.config['creature_name']].get_engine(CRVisualSensor, visualSensorDesc, 1)
			self.visualsensorR.SetSolid(So[self.config['eyes_name']['R']].spr())

			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Perception
			self.perception = Perception([self.visualsensorL, self.visualsensorR], self.touchsensor, self.visualizer)
			self.perception.info[So[self.config['floor_name']].spr()].ignore = True

		else:
			visualSensorDesc = CRVisualSensorDesc()
			visualSensorDesc.limitDistance = 120
			self.visualsensor = Cr[self.config['creature_name']].get_engine(CRVisualSensor, visualSensorDesc)
			self.visualsensor.SetSolid(So[self.config['head_name']].spr())

			# ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
			# Perception
			self.perception = Perception([self.visualsensor], self.touchsensor, self.visualizer)
			self.perception.info[So[self.config['floor_name']].spr()].ignore = True


	def init_walk(self):
		if not self.config['enable_walk']:
			return

		# -- Walk
		self.footstepctl  = FootStepController(So[self.config['base_name']].spr(), So[self.config['feet_name']['L']].spr(), So[self.config['feet_name']['R']].spr(), self.config)
		self.walktrajctl  = WalkTrajectoryController()
		self.walkanimegen = AnimationGenerator(Scn.spr(), self.config['upper_body_names'], So[self.config['floor_name']].spr(), So[self.config['base_name']].spr(), So[self.config['waist_name']].spr(), self.touchsensor, self.footstepctl, Jo[self.config['base_joint_name']].spr(), self.config)


	def init_look(self):
		if not self.config['enable_look']:
			return

		# -- Look
		self.headlook = Cc[self.config['head_look_ctl']]
		self.headlook.spr().SetIKEndEffector(IKe[self.config['head_name']].spr(), 0)
		cb_leye = Cb[self.config['eyes_name']['L']] if self.config['eyes_name']['L'] in Cb else None
		cb_reye = Cb[self.config['eyes_name']['R']] if self.config['eyes_name']['L'] in Cb else None
		self.lookctl  = LookController(self.headlook.spr(), cb_leye, cb_reye, self.config)
		self.headlook.spr().Init()


	def init_touch(self):
		if not self.config['enable_touch']:
			return

		# -- Reach
		self.handsreach = Cc[self.config['hands_reach_ctl']['LR']]
		self.handsreach.spr().SetIKEndEffector(IKe[self.config['hands_name']['L']].spr(), 0)
		self.handsreach.spr().SetIKEndEffector(IKe[self.config['hands_name']['R']].spr(), 1)
		self.handsreach.spr().SetBaseJoint(0, Jo[self.config['arms_joint_name']['L']].spr())
		self.handsreach.spr().SetBaseJoint(1, Jo[self.config['arms_joint_name']['R']].spr())
		
		self.handsreach.spr().SetNumUseHands(-1)
		self.handsreach.spr().SetMargin(0)
		self.handsreach.spr().SetAverageSpeed(self.config['hand_reach_avg_speed'])
		self.handsreach.spr().SetRestartVel(self.config['hand_reach_restart_vel'])
		self.handsreach.spr().SetWaitVel(self.config['hand_reach_wait_vel'])

		self.handsreach.spr().Init()
		
		self.touchctl	= TouchController(self.handsreach.spr(), self.perception, self.config)

		
	def init_eat(self):
		if not self.config['enable_eat']:
			return

		# -- Eat
		self.headreach	= Cc[self.config['head_reach_ctl']]
		self.headreach.spr().SetIKEndEffector(IKe[self.config['head_name']].spr(), 0)
		self.headreach.spr().Init()
		self.eatctl		= EatController(self.headlook, self.headreach, self.perception, self.config) 

	def init_grab(self):
		if not self.config['enable_grab']:
			return

		# -- Grab
		self.leftgrab = Cr[self.config['creature_name']].get_engine(CRGrabController, CRGrabControllerDesc(), 0)
		self.leftgrab.SetSolid(Cb[self.config['hands_name']['L']].spr())

		self.rightgrab = Cr[self.config['creature_name']].get_engine(CRGrabController, CRGrabControllerDesc(), 1)
		self.rightgrab.SetSolid(Cb[self.config['hands_name']['R']].spr())
		
		self.grabctl = GrabController(self.leftgrab, self.rightgrab, self.handsreach, self.perception, self.config)
	
	def init_reach(self):
		# -- Reach
		self.leftreach = Cr[self.config['creature_name']].get_engine(CRReachController, CRReachControllerDesc(), 5)
		self.leftreach.SetIKEndEffector(IKe[self.config['hands_name']['L']].spr())
		self.leftreach.SetAverageSpeed(self.config['hand_reach_avg_speed'])
		
		
		self.rightreach = Cr[self.config['creature_name']].get_engine(CRReachController, CRReachControllerDesc(), 6)
		self.rightreach.SetIKEndEffector(IKe[self.config['hands_name']['R']].spr())
		self.rightreach.SetAverageSpeed(self.config['hand_reach_avg_speed'])
		
		self.leftreach.Init()
		self.rightreach.Init()
		
		self.reachctl = ReachController(self.leftreach, self.rightreach, self.handsreach, self.perception, self.config)
		
	
	def step_perception(self):
		fov_horiz = Cr[self.config['creature_name']].get_cr_param("FOV Horiz",90)
		fov_vert  = Cr[self.config['creature_name']].get_cr_param("FOV Vert", 90)
		self.visualsensorL.SetRange(Vec2d(rad(fov_horiz), rad(fov_vert)))
		self.visualsensorR.SetRange(Vec2d(rad(fov_horiz), rad(fov_vert)))

		c_fov_horiz = Cr[self.config['creature_name']].get_cr_param("FOV Horiz Center",10)
		c_fov_vert  = Cr[self.config['creature_name']].get_cr_param("FOV Vert Center", 10)
		self.visualsensorL.SetCenterRange(Vec2d(rad(c_fov_horiz), rad(c_fov_vert)))
		self.visualsensorR.SetCenterRange(Vec2d(rad(c_fov_horiz), rad(c_fov_vert)))
		self.perception.step()


	def step_walk(self):
		if not self.config['enable_walk']:
			return

		ap = bpy.data.objects[self.config['base_name']].location
		self.walktrajctl.step(actual_pos=Vec2d(ap.x, ap.y))

		position, direction = self.walktrajctl.get_next_target(self.config['walk_traj_target_distance'])
		if direction is None:
			direction = Vec3d(0,-1,0)

		#print("direcyion x,y :", round(direction.x, 3), round(direction.y, 3))

		tarPos    = Vec3d(position.x,position.y,0)
		tarVel    = Vec3d(0,0,0)
		tarAngle  = Vec3d(0,0,0)
		tarAngvel = Vec3d(0,0,0)
		tarAngleF = Vec3d(direction.x, direction.y, 0)
		Dvec      = [tarPos, tarAngle, tarVel, tarAngvel, tarAngleF]

		self.walkanimegen.animeStep(Scn.spr(), Dvec, self.config['upper_body_names'])


	def step_walk_animation(self):
		if not self.config['enable_walk']:
			return

		self.footstepctl.step(self.walkanimegen.walkctl.getFootPos())


	def step_look(self):
		if not self.config['enable_look']:
			return

		self.headlook.spr().Enable(True)
		self.headlook.spr().EnableLookatMode(True)
		self.headlook.spr().SetAverageSpeed(self.config['look_avg_speed'])
		self.headlook.spr().SetWaitVel(self.config['look_wait_vel'])
		self.headlook.spr().SetRestartVel(self.config['look_restart_vel'])
		self.lookctl.step()
		
	def step_touch(self):
		if not self.config['enable_touch']:
			return

		self.touchctl.step()


	def step_eat(self):
		if not self.config['enable_eat']:
			return

		self.headreach.spr().Enable(True)
		self.headreach.spr().SetAverageSpeed(self.config['head_reach_avg_speed'])
		self.headreach.spr().SetWaitVel(self.config['head_reach_wait_vel'])
		self.headreach.spr().SetRestartVel(self.config['head_reach_restart_vel'])
		self.eatctl.step()
		
	def step_grab(self):
		if not self.config['enable_grab']:
			return

		return self.grabctl.step()
	
	def step_reach(self, leftcnt, rightcnt):
		self.reachctl.step(leftcnt, rightcnt)
		
		
	def draw(self):
		if not self.config['enable_walk']:
			return
		self.walktrajctl.draw()
		
	def step_petari(self):
		self.petari.step()


