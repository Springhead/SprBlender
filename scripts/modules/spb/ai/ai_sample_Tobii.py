from spb.ai.ai       import *
from spb.ai.ai_utils import *
from spb.abbrev      import *
import time

class AISample:
	def __init__(self):
		self.ai = AIBase()

		#Tobii
		self.eye = None
		self.ignorelis = ['so_so_Head',
						  'so_so_Chest',
						  'so_so_Waist',
						  'so_so_Abdomen',
						  'so_so_LeftUpperLeg',
						  'so_so_RightUpperLeg',
						  'so_so_LeftUpperArm',
						  'so_so_RightUpperArm',
						  'so_so_LeftLowerArm',
						  'so_so_RightLowerArm',
						  'so_so_RightFoot',
						  'so_so_LeftFoot',
						  'so_so_LeftHand',
						  'so_so_RightHand',
						  'Basket'
						  ]
		self.boringvalue = 0
		self.flag = False
		#self.seeingobj = So['so_AppleR1.007'].spr()
		self.seeingobj = None
		self.latestseeingobj = None
		self.latest_max_att_obj = None
		self.conviction = 0
		self.delay = 0

		self.beforetime = 0
		self.nowtime    = 0

		#self.guidemode = None
	def init(self):
		self.walk_target = None

		fwleap = spb.spbapi_cpp.CreateLeap()
		#spb.spbapi_cpp.CreateLeapUDP()

		hileap = fwleap.GetSensor()
		scale = 0.7
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

		#self.ai.step_petari()

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

		self.beforetime = self.nowtime
		self.nowtime    = time.time()
		dtime           = self.nowtime - self.beforetime 

		# Look Attractive Object
		max_att_obj = None
		try:
			# 追加の知覚情報を生成する
			for solid, info in self.ai.perception.info.items():
				if not solid is None:
					if "Apple" in solid.GetName():
						info.edible = True

			#Tobii
			"""
			if self.latest_max_att_obj is not None:
				if self.latest_max_att_obj.att_tpd_interest > 0:
					if self.latest_max_att_obj == max(self.ai.perception.info.values(), key=lambda info: (info.att_tpd_interest if not info.solid is None else 0)):
						self.guidemode = True
				else:
					self.guidemode = False
			print(self.guidemode)
			print(self.conviction)
			"""

			#近くにあるオブジェクトを取得(soThetaの角度の範囲内)
			soliddict = {}
			for solid, info in self.ai.perception.info.items():
				if not solid is None:
					if solid.GetName() not in self.ignorelis:
						if self.eye.eyeDirection != None :
							solidPos = solid.GetPose().getPos() - to_spr( self.eye.CameraPosition )
							hePos  = So['so_Head'].spr().GetPose().getPos() - to_spr( self.eye.CameraPosition )
							soTheta  = acos( to_spr( self.eye.eyeDirection )*solidPos / ( (solidPos.norm())*(to_spr( self.eye.eyeDirection ).norm()) ) )
							heTheta  = acos( to_spr( self.eye.eyeDirection )*hePos / ( (hePos.norm())*(to_spr( self.eye.eyeDirection ).norm()) ) )
							if soTheta < rad(15):
								soliddict[solid] = soTheta
			nearobj = min([(s,i) for i,s in soliddict.items()])[1] #Rayから一番近いオブジェクトを取得
			if not nearobj == {}:
				print("#nearobj:")
				print( nearobj.GetName() )

			min_att_tpd_base_AppleR = Cr[self.ai.config['creature_name']].get_cr_param('MIN_TDA Apple Red', 0.5)
			max_att_tpd_base_AppleR = Cr[self.ai.config['creature_name']].get_cr_param('MAX_TDA Apple Red', 1.5)
			#min_att_tpd_base_AppleG = Cr[self.ai.config['creature_name']].get_cr_param('TDA Apple Green', 0.1)
			#max_att_tpd_base_AppleG = Cr[self.ai.config['creature_name']].get_cr_param('TDA Apple Green', 0.1) + 1.0
			min_att_tpd_base_EyePosition = Cr[self.ai.config['creature_name']].get_cr_param('MIN_TDA EyePosition', 0.8)
			max_att_tpd_base_Eyeposition = Cr[self.ai.config['creature_name']].get_cr_param('MAX_TDA EyePosition', 4.0)

			min_att_tpd_boring = Cr[self.ai.config['creature_name']].get_cr_param('MIN_TDA Boring', 0)
			max_att_tpd_boring = Cr[self.ai.config['creature_name']].get_cr_param('MAX_TDA Boring', 1)

			min_att_tpd_wonder = Cr[self.ai.config['creature_name']].get_cr_param('MIN_TDA Wonder', 0)
			max_att_tpd_wonder = Cr[self.ai.config['creature_name']].get_cr_param('MAX_TDA Wonder', 3)

			min_att_tpd_interest = Cr[self.ai.config['creature_name']].get_cr_param('MIN_TDA Interest', 0)
			max_att_tpd_interest = Cr[self.ai.config['creature_name']].get_cr_param('MAX_TDA Interest', 4)

			#swich_att_threshold = 0.1
			lowpassparam = Cr[self.ai.config['creature_name']].get_cr_param('lowpass', 0.7)
			boringparam = Cr[self.ai.config['creature_name']].get_cr_param('boring', 0.02)
			awarenessparam = Cr[self.ai.config['creature_name']].get_cr_param('awareness', 0.1)
			wonderparam = Cr[self.ai.config['creature_name']].get_cr_param('wonder', 0.01)
			interestparam = Cr[self.ai.config['creature_name']].get_cr_param('interest', 0.4)
			recovery_ratio = Cr[self.ai.config['creature_name']].get_cr_param('recovery_ratio', 0.3)
			seeing_correct_value = Cr[self.ai.config['creature_name']].get_cr_param('seeing_correct', 1000)
			big_attention_correct_value = Cr[self.ai.config['creature_name']].get_cr_param('big_attention_correct', 10)
			big_attention = Cr[self.ai.config['creature_name']].get_cr_param('big_attention', 5)
			ratio_range = 0
			#ratioparam = 2
			sum_att_total = 0
			guidemode = None



			att_ratio_list = []
			udeg = Cr[self.ai.config['creature_name']].get_cr_param('udeg', 5)
			# ユーザの顔(EyePosition)について
			for solid, info in self.ai.perception.info.items():
				if not solid is None:
					if "EyePosition" in solid.GetName(): #EyePositionはユーザの位置
						# ユーザーの顔が視野内
						if info.visible is True:
							# 人の視線が高速で動いていたら不審に思い反応する
							if self.eye.eyevelocity > 0.1:
								info.att_tpd_wonder += self.eye.eyevelocity
							else:
								info.att_tpd_wonder -= wonderparam

							# ユーザの顔が中心視野内
							if info.visible_center is True: 
								print("***User central vision")
								if not nearobj == {}:
									self.seeingobj = self.ai.perception.info[nearobj]
									if "Apple" in self.seeingobj.solid.GetName():
										self.seeingobj.att_tpd_interest += (1 - lowpassparam) * interestparam
									if "Cube" in self.seeingobj.solid.GetName():
										self.seeingobj.att_tpd_interest += (1 - lowpassparam) * interestparam
									# ユーザの顔が中心視野内かつユーザがくまを見ている
									if heTheta < rad(udeg):
										print("###User looking(central)")
										# 中心視野内に入っている間は飽きを増やす(ユーザがくまを見ている場合は飽きが早い)
										info.att_tpd_boring -= (1 - lowpassparam) * boringparam
										# ユーザがくまを見ている間はbaseを増やす
										info.att_tpd_base += (1 - lowpassparam) * awarenessparam
									# ユーザの顔が中心視野内かつユーザがくまを見ていない
									else:
										# 中心視野内に入っている間は飽きを増やす(ユーザがくまを見ている場合は飽きが遅い)
										info.att_tpd_boring -= (1 - lowpassparam) * boringparam * 0.5
										# ユーザがくまを見ていない間はbaseを減らす
										info.att_tpd_base -= (1 - lowpassparam) * awarenessparam * 0.2
										self.seeingobj.att_tpd_boring = 1 
										guidemode = True
										#self.conviction += 0.01
										
							# ユーザの顔が周辺視野内 (見えているが中心視野内ではない)
							if info.visible_center is False:
								# 中心視野に入っていない間は飽きを減らす
								#info.att_tpd_boring += (1 - lowpassparam) * boringparam * recovery_ratio
								info.att_tpd_boring += (1 - lowpassparam) * boringparam
								# ユーザの目の動く速度に比例してユーザの顔への注意を増やす
								
								if not nearobj == {}:
									# ユーザの顔が周辺視野内かつユーザがくまを見ている
									if heTheta < rad(udeg):
										print("###User looking(peripheral)")
										info.att_tpd_base += (1 - lowpassparam) * awarenessparam
											
									# ユーザの顔が周辺視野内かつユーザがくまを見ていない
									else:
										# ユーザがくまを見ていない間はbaseを減らす
										info.att_tpd_base -= (1 - lowpassparam) * awarenessparam * 0.2
							
						# ユーザーの顔が視野外
						else:
							# ユーザが視野に入っていない間は飽きを減らす
							#info.att_tpd_boring += (1 - lowpassparam) * boringparam * recovery_ratio
							info.att_tpd_boring += (1 - lowpassparam) * boringparam
							# ユーザが視野に入っていない間はbaseを減らす
							info.att_tpd_base -= (1 - lowpassparam) * awarenessparam * 0.2

						# トップダウンの要素値が最大値/最小値を越えていたらその値にする
						if info.att_tpd_base < min_att_tpd_base_EyePosition:
							info.att_tpd_base = min_att_tpd_base_EyePosition
						if info.att_tpd_base > max_att_tpd_base_Eyeposition:
							info.att_tpd_base = max_att_tpd_base_Eyeposition

					if "AppleR" in solid.GetName():
						if info.visible_center is True:
							# 中心視野内に入っている間は飽きを増やす
							info.att_tpd_boring -= (1 - lowpassparam) * boringparam
						else:
							# 見ていない間は飽きを減らす
							info.att_tpd_boring += (1 - lowpassparam) * boringparam * recovery_ratio

						# baseが最大値/最小値を超えていたらその値にする
						if info.att_tpd_base < min_att_tpd_base_AppleR:
							info.att_tpd_base = min_att_tpd_base_AppleR
						if info.att_tpd_base > max_att_tpd_base_AppleR:
							info.att_tpd_base = max_att_tpd_base_AppleR

					if "Cube" in solid.GetName():
						if info.visible_center is True:
							# 中心視野内に入っている間は飽きを増やす
							info.att_tpd_boring -= (1 - lowpassparam) * boringparam
						else:
							# 見ていない間は飽きを減らす
							info.att_tpd_boring += (1 - lowpassparam) * boringparam * recovery_ratio

					
					# ユーザが見ていない物の興味は下げる
					if self.seeingobj is not None:
						if solid.GetName() != self.seeingobj.solid.GetName():
							info.att_tpd_interest -= (1 - lowpassparam) * interestparam * 0.2

					if self.latestseeingobj is not None:
						if self.latestseeingobj != self.seeingobj:
							self.conviction = 0
					
					# 飽き値が最大値/最小値を超えていたらその値にする
					if info.att_tpd_boring < min_att_tpd_boring:
						info.att_tpd_boring = min_att_tpd_boring
					if info.att_tpd_boring > max_att_tpd_boring:
						info.att_tpd_boring = max_att_tpd_boring

					# 不審値が最大値/最小値を超えていたらその値にする
					if info.att_tpd_wonder < min_att_tpd_wonder:
						info.att_tpd_wonder = min_att_tpd_wonder
					if info.att_tpd_wonder > max_att_tpd_wonder:
						info.att_tpd_wonder = max_att_tpd_wonder

					# ユーザが見ているものへの興味が最大値/最小値を超えていたらその値にする
					if info.att_tpd_interest < min_att_tpd_interest:
						info.att_tpd_interest = min_att_tpd_interest
					if info.att_tpd_interest > max_att_tpd_interest:
						info.att_tpd_interest = max_att_tpd_interest

					info.att_topdown = info.att_tpd_boring * (info.att_tpd_base + info.att_tpd_wonder + info.att_tpd_interest)
					self.latestseeingobj = self.seeingobj

			# 全剛体のatt_totalを出力
			#print("all objects att_total:")
			#print({(info.solid.GetName() if not info.solid is None else ""):info.att_tpd_interest for info in self.ai.perception.info.values()})
			#print({(info.solid.GetName() if not info.solid is None else ""):info.att_total for info in self.ai.perception.info.values()})
			
			self.ai.step_perception()

			"""
			for solid, info in self.ai.perception.info.items():
				if not solid is None:
					if "Cube" in solid.GetName():
						info.att_topdown = 0.0
					if "EyePosition" in solid.GetName():
						info.att_topdown = 0.0
					if "Leap" in solid.GetName():
						info.att_topdown = 0.0
			"""

			# 注意量最大のオブジェクトを得る
			#max_att_obj = max(self.ai.perception.info.values(), key=lambda info: (info.att_total if not info.solid is None else 0))
			
			for solid, info in self.ai.perception.info.items():
				if not solid is None:
					
					if self.latest_max_att_obj is not None:
						"""
						if not guidemode:
							if self.latest_max_att_obj.solid.GetName() == info.solid.GetName():
								if "Apple" in info.solid.GetName():
									info.att_total *= correct_value * 5
								if "Cube" in info.solid.GetName():
									info.att_total *= correct_value * 5
								if "EyePosition" in info.solid.GetName():
									info.att_total *= correct_value * 5
						else:
							if self.latest_max_att_obj.solid.GetName() == info.solid.GetName():
								if "EyePosition" in info.solid.GetName():
									info.att_total *= correct_value * 0.5
						"""
						if self.latest_max_att_obj.solid.GetName() == info.solid.GetName():
							if "Apple" in info.solid.GetName():
								info.att_total *= seeing_correct_value * 5
							if "Cube" in info.solid.GetName():
								info.att_total *= seeing_correct_value * 5
							if "EyePosition" in info.solid.GetName():
								info.att_total *= seeing_correct_value * 5
						else:
							if info.att_total > big_attention:
								if "Apple" in info.solid.GetName():
									info.att_total *= big_attention_correct_value * 5
								if "Cube" in info.solid.GetName():
									info.att_total *= big_attention_correct_value * 5
								if "EyePosition" in info.solid.GetName():
									info.att_total *= big_attention_correct_value * 5
							#if "Basket" in info.solid.GetName():
							#	info.att_total *= 800
						
					sum_att_total += info.att_total

			for solid, info in self.ai.perception.info.items():
				if not solid is None:
					if not sum_att_total == 0:
						if not info.att_total == 0:
							ratio_range += (info.att_total / sum_att_total)
							att_ratio_list.append([ratio_range, info])

			random_value = random.random()
			if att_ratio_list != []:
				for range_info_pair in att_ratio_list:
					if random_value < range_info_pair[0]:
						max_att_obj = range_info_pair[1]
						break

			Vis["Graph1"].set_graph_bold(max_att_obj.solid.GetName()[3:])

			"""
			# 描画
			for solid, info in self.ai.perception.info.items():
				if not info.ignore:
					graph = Vis["Graph1"]
					if graph is not None:
						graph.set_graphdata(info.solid.GetName()[3:],     info.pos_world.curr_var, info.att_total)
			"""
					

			#if max_att_obj is not None:
			print("")
			#print(sum_att_total)
			for i in att_ratio_list:
				print(i[0], i[1].solid.GetName())
			print(max_att_obj.solid.GetName())
			print(random.random())	
			print("")


			"""
			if self.guidemode:
				if self.conviction <= 0.1:
					for solid, info in self.ai.perception.info.items():
						if not solid is None:
							if "EyePosition" in solid.GetName():
								max_att_obj = info
								break
			"""
			"""
			if self.latest_max_att_obj is not None:
				if (max_att_obj.att_total - self.latest_max_att_obj.att_total) < swich_att_threshold:
					max_att_obj = self.latest_max_att_obj
			"""
			self.latest_max_att_obj = max_att_obj
			
		except (ValueError):
			pass

		if max_att_obj and max_att_obj.solid:

			print("max attention object : " + max_att_obj.solid.GetName())
			print(max_att_obj.att_total)

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

			if max_att_obj.att_total > 0.1 and max_att_obj.edible:
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

