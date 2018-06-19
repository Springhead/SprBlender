from spb.ai.ai       import *
from spb.ai.ai_utils import *
from spb.abbrev      import *


class AISample:
	def __init__(self):
		self.ai = AIBase()

	def init(self):
		self.walk_target = None

		fwleap = spb.spbapi_cpp.CreateLeap()
		#spb.spbapi_cpp.CreateLeapUDP()

		hileap = fwleap.GetSensor()
		scale = 0.8
		hileap.SetScale((1/22) * scale)
		hileap.SetCenter(Vec3d(0,-5,-3));
		fwleap.SetRadius(Vec2d(0.4*scale, 0.4*scale));

		self.touch_delaysel = DelaySelect(1.0)
		self.leftcnt = 0
		self.rightcnt = 0

		self.walk_final_pos = Vec3d()

		self.ai.init_petari()
		self.ai.init_body()
		self.ai.init_visualizer()
		self.ai.init_perception()
		#self.ai.init_walk()
		self.ai.init_look()
		self.ai.init_touch()
		self.ai.init_eat()
		self.ai.init_grab()
		self.ai.init_reach()

		print("Initialized.")


	def step(self):
		# Step
		#self.ai.walktrajctl.set_final_pos(Vec2d(self.walk_final_pos.x, self.walk_final_pos.y))
		#print('enable : ', self.ai.walktrajctl.update_enable)

		# --
		#self.ai.step_perception()
		#self.ai.step_walk()
		pass


	def step_bpy(self):
		# Step bpy

		self.ai.step_perception()

		# self.ai.step_petari()

		# Set Walk target
		'''
		if self.ai.walktrajctl.update_enable:
			if not self.walk_target is None:
				pos = self.walk_target.GetPose().getPos(); pos.z =0
				basketpos = to_spr(bpy.data.objects["Basket"].location); basketpos.z = 0
				currpos = to_spr(bpy.data.objects[self.ai.config["base_name"]].location); currpos.z = 0
				temp_dir = pos - basketpos
				temp_dis = pos - currpos
				if temp_dir.norm() < 4 :
					pass
				elif temp_dis.norm() < 10:
					pass
				elif pos.x < -55 or 56 < pos.x or pos.y < -12 or 28 < pos.y:
					pass
				else :
					self.walk_final_pos = pos
				#	pos = basketpos + temp_dir.unit() * 6

				# pos = self.walk_target.GetPose().getPos(); pos.z = 0
				# currpos = to_spr(bpy.data.objects[self.ai.config["base_name"]].location); currpos.z = 0
				# basketpos = to_spr(bpy.data.objects["Basket"].location); basketpos.z = 0
				# if False : # (pos-basketpos).norm() < 7.0:
				# 	pos = (currpos - basketpos).unit()*7.0 + basketpos
				# # traject
				# self.walk_final_pos = pos
		else :
			pass
		'''

		# Look Attractive Object
		max_att_obj = None
		try:
			# 追加の知覚情報を生成する
			for solid, info in self.ai.perception.info.items():
				if not solid is None:
					if "Apple" in solid.GetName():
						info.edible = True

			# トップダウン注意を生成する
			for solid, info in self.ai.perception.info.items():
				if not solid is None:
					if "AppleR" in solid.GetName():
						info.att_topdown = Cr[self.ai.config['creature_name']].get_cr_param('TDA Apple Red', 0.5)
					if "AppleG" in solid.GetName():
						info.att_topdown = Cr[self.ai.config['creature_name']].get_cr_param('TDA Apple Green', 0.1)

			# 注意量最大のオブジェクトを得る
			max_att_obj = max(self.ai.perception.info.values(), key=lambda info: (info.att_total if not info.solid is None else 0))

		except (ValueError):
			pass

		if max_att_obj and max_att_obj.solid:
			self.ai.lookctl.set_target_position(max_att_obj.solid.GetPose().getPos())
			self.ai.lookctl.set_attractiveness(max_att_obj.att_total)
			
			# --

			#'''
			if max_att_obj.att_total > 0.01:
				#print("max_att>0.1")
				if self.touch_delaysel.input(max_att_obj.solid):
					self.ai.touchctl.set_target_solid(self.touch_delaysel.selection)
					#self.ai.grabctl.set_grab_target(self.touch_delaysel.selection)

			if max_att_obj.att_total > 0.011:
				self.ai.handsreach.spr().SetNumUseHands(1)

			if max_att_obj.att_total > 0.1:
				self.ai.handsreach.spr().SetNumUseHands(-1)
			#'''

			# --

			if max_att_obj.att_total > 0.1 and max_att_obj.edible and max_att_obj.visible_count > 15:
				self.ai.eatctl.add_eat_target(max_att_obj.solid)

			# --
			"""
			if max_att_obj.att_total > 0.1:
				self.walk_target = max_att_obj.solid
			"""
		# --
		head_pose = So[self.ai.config["head_name"]].spr().GetPose()
		#"""
		mouth_tip = to_spr(bpy_object_pose(bpy.data.objects[self.ai.config['head_ik_tips']['Eat']]).translation)
		self.ai.reachctl.set_reach_target(mouth_tip)
		"""
		mouth_tip = bpy_object_pose(bpy.data.objects[self.ai.config['head_ik_tips']['Eat']]).translation
		mouth_pos_global = to_spr(mouth_tip)
		mouth_pos_local  = head_pose.Inv().transform(mouth_pos_global)
		self.ai.reachctl.set_reach_target(So[self.ai.config["head_name"]].spr(), mouth_pos_local)
		#"""
		if not self.touch_delaysel.selection is None and "Apple" in self.touch_delaysel.selection.GetName():
			self.ai.grabctl.set_grab_target(self.touch_delaysel.selection)
			
		#'''

		# --
		#print(self.leftcnt,self.rightcnt)
		#self.ai.step_walk_animation()
		self.ai.step_look()
		self.ai.step_eat()
		self.ai.step_touch()
		self.leftcnt, self.rightcnt = self.ai.step_grab()
		self.ai.step_reach(self.leftcnt, self.rightcnt)

		# --
		bpy.data.shape_keys["Key"].key_blocks["MouthOpen"].value = self.ai.eatctl.mouth_open
		bpy.data.objects['cd_MouthClose'].location.y = (0.4+0.387)* self.ai.eatctl.mouth_open - 0.387
		Shp['cd_MouthClose'].pose_sync.sync_bpy_to_spr()
		
		if self.ai.eatctl.control_mode == "Wait" and self.ai.eatctl.curr_target is not None:
			if self.ai.grabctl.leftgrab.GetGrabbingSolid()==self.ai.eatctl.curr_target:
				self.ai.grabctl.leftgrab.Reset()
				self.ai.grabctl.curr_grab_target = None
			if self.ai.grabctl.rightgrab.GetGrabbingSolid()==self.ai.eatctl.curr_target:
				self.ai.grabctl.rightgrab.Reset()
				self.ai.grabctl.curr_grab_target = None
			if self.ai.perception.info[self.ai.eatctl.curr_target].visible_count > 30:
				self.ai.eatctl.curr_target.SetFramePosition(Vec3d(500,100,100))
			self.ai.eatctl.curr_target = None


		# --
		for name, sohnd in So.items():
			if "Apple" in name:
				for wall in ["Wall1", "Wall2", "Wall3", "Wall4"]:
					if wall in So:
						Scn.spr().SetContactMode(sohnd.spr(), So[wall].spr(), 0)

				if sohnd.spr().GetPose().getPos().z < -50:
					sohnd.spr().SetFramePosition( to_spr(bpy.data.objects["Basket"].location) )
					sohnd.spr().SetVelocity(Vec3d())
					sohnd.spr().SetAngularVelocity(Vec3d())

	def draw(self):
		# Draw
		#self.ai.draw()
		pass

