# -*- coding: utf-8 -*-

import spb
import random

from   collections  import defaultdict
from   spb.utils    import *
from   spb.abbrev   import *
from   Spr          import *
from   math         import *


class PerceptionObject:
	def __init__(self):
		self.solid            = None
		self.ignore           = False

		self.confidence_pos   = 0
		self.confidence_type  = 0
		self.weariness        = 0
		self.k_weariness      = 0

		# --- 視覚情報 ---
		self.visible          = False
		self.visible_center   = False
		self.visible_count    = 0
		self.pos_world        = Var(lambda: Vec3d(), alpha=0.5, diff_alpha=0.5, keep_value=True)
		self.sensor_pos       = Var(lambda: Vec3d(), alpha=0.5, diff_alpha=0.5, keep_value=True)
		self.sensor_ori       = Var(lambda: Vec3d(), alpha=0.5, diff_alpha=0.5, keep_value=True)
		self.sensor_pose_avg  = Posed()

		self.close_vel        = 0
		self.away_vel         = 0
		self.side_vel         = 0

		# --- 触覚情報 ---
		self.touching         = False
		self.list             = []
		self.touch_force      = Var(lambda:       0, alpha=0.30, diff_alpha=0.50)
		self.touch_pos        = Var(lambda: Vec3d(), alpha=1.00, diff_alpha=0.50)

		# --- 注意情報 ---
		self.att_visual       = 0
		self.att_touch        = 0
		self.att_topdown      = 0
		self.att_total        = 0

		# --- topdown注意の要素 ---
		self.att_tpd_base 	  	= 0
		self.att_tpd_boring		= 1
		self.att_tpd_wonder   	= 0
		self.att_tpd_interest	= 0

		# some properties
		self.edible           = False

		# GainAdjuster用の一意なランダムキー
		self.rand_val         = random.randint(0,1000)*100


	def clear(self):
		self.visible          = False
		self.visible_center   = False
		self.touching         = False
		self.list             = []

		self.pos_world.clear()
		self.sensor_pos.clear()
		self.sensor_ori.clear()

		self.touch_force.clear()
		self.touch_pos.clear()

	def input_visual_info(self, vis):
		self.visible = True
		self.pos_world.input( self.solid.GetPose().getPos() )
		self.sensor_pos.input( vis.sensorPose.getPos() )
		self.sensor_ori.input( vis.sensorPose.getOri().RotationHalf() )

	def input_visual_center_info(self, vis):
		self.visible_center = vis.bCenter
		self.pos_world.input( self.solid.GetPose().getPos() )
		self.sensor_pos.input( vis.sensorPose.getPos() )
		self.sensor_ori.input( vis.sensorPose.getOri().RotationHalf() )

	def input_touch_info_other(self, con):
		self.list.append(con.soMe)
		self.pos_world.input( self.solid.GetPose().getPos() )
		self.input_touch_info(con)

	def input_touch_info_me(self, con):
		self.list.append(con.soOther)
		self.input_touch_info(con)

	def input_touch_info(self, con):
		self.touching = True
		self.touch_force.input( con.force.norm() )
		self.touch_pos.input( con.pos )

	def update(self, dt):
		self.pos_world.update(dt)
		self.sensor_pos.update(dt)
		self.sensor_ori.update(dt)

		self.touch_force.update(dt)
		self.touch_pos.update(dt)
		
		if self.touch_pos.n_input > 0:
			#print("Touch Pos Var :" , self.touch_pos.v_input, self.touch_pos.n_input)
			pass

		# 位置の確信度の更新
		if self.visible or self.touching:
			if self.visible:
				self.confidence_pos  = min(self.confidence_pos + 0.30, 1)
			else:
				self.confidence_pos  = min(self.confidence_pos + 0.10, 1)

		# 種別の確信度の更新
		if self.visible:
			self.confidence_type = min(self.confidence_type + 0.10, 1)
			self.visible_count  += 1
		else:
			self.confidence_type = max(self.confidence_type - 0.05, 0)
			self.visible_count   = 0

		# 情報がないとき：確信度の低下
		if not self.visible and not self.touching:
			self.confidence_pos  = max(self.confidence_pos - 0.05, 0)

		# 確信度があるときだけ予測を作用させる
		'''
		if self.confidence_pos > 1e-5:
			self.pos_world.predict = True
		else:
			self.pos_world.predict = False
		#'''

		# 飽き値の更新
		if self.confidence_pos > 0.99:
			self.weariness = min(self.weariness + 0.003, 1)
		if self.confidence_pos < 0.50:
			self.weariness = max(self.weariness - 0.005, 0)

		self.k_weariness = sqrt(1-self.weariness) * 0.5 + 0.5

		# 視覚注意を算出
		self.sensor_pose_avg = Posed( self.sensor_pos.curr_var, Quaterniond.Rot(self.sensor_ori.curr_var) )
		distance  = max((self.pos_world.curr_var - self.sensor_pos.curr_var).norm(), 0.1)
		vel_local = (self.sensor_pose_avg.Inv().transform(self.pos_world.diff_var)) * (1 / distance)
		self.att_visual_close =  (4/20) * abs(max(vel_local.y, 0))
		self.att_visual_away  =  (1/20) * abs(min(vel_local.y, 0))
		self.att_visual_side  =  (2/20) * Vec2d(vel_local.x, vel_local.z).norm()
		# self.att_visual = self.k_weariness * self.confidence_pos * (self.att_visual_close + self.att_visual_away + self.att_visual_side)
		self.att_visual = 4.0 * (self.att_visual_close + self.att_visual_away + self.att_visual_side)
		
		# 触覚注意を算出
		self.att_touch_dpos   =  2.0 * GainAdjuster(self.rand_val+4)[ self.touch_pos.diff_var.norm() ]
		self.att_touch_force  =  1.0 * GainAdjuster(self.rand_val+5)[ abs(self.touch_force.curr_var) ]
		self.att_touch_dforce =  1.0 * GainAdjuster(self.rand_val+6)[ abs(self.touch_force.diff_var) ]

		self.att_touch = 5.0 * self.k_weariness * GainAdjuster(self.rand_val+7)[ self.att_touch_dpos + self.att_touch_force + self.att_touch_dforce ]

		# 総合注意の算出
		self.att_total = self.att_visual + self.att_touch + self.att_topdown

		if not self.visible and not self.touching:
			self.att_visual = 0.0
			self.att_touch = 0.0
			#self.att_total = 0.0



class Perception:
	def __init__(self, visualsensors, touchsensor, visualizer):
		self.visualsensors = visualsensors
		self.touchsensor   = touchsensor
		self.visualizer    = visualizer
		self.info          = defaultdict(lambda: PerceptionObject())

		self.att_visual_level = defaultdict(lambda: KeepMaxLevelMeter(0.5))
		self.att_touch_level  = defaultdict(lambda: KeepMaxLevelMeter(0.5))

	def step(self):
		#for so in Scn.spr().GetSolids():
		#	print(so.GetName())

		# 初期化
		for solid, info in self.info.items():
			#if "so_so_AppleR1" in solid.GetName():
			#	print(solid.GetName())
			#	print(info.att_total)
			info.clear()

		# 視覚入力
		for visualsensor in self.visualsensors:
			visualsensor.Update()
			for i in range(visualsensor.NVisibles()):
				vis = visualsensor.GetVisible(i)
				self.info[vis.solid].solid = vis.solid
				#print(vis.solid.GetName())
				if vis.bMyBody:
					self.info[vis.solid].ignore = True
				if not self.info[vis.solid].ignore:
					self.info[vis.solid].input_visual_info(vis)
					# 中心視野
					self.info[vis.solid].input_visual_center_info(vis)

		# 触覚入力
		self.touchsensor.Update()
		for i in range(self.touchsensor.NContacts()):
			con = self.touchsensor.GetContact(i)
			self.info[con.soOther].solid = con.soOther
			self.info[con.soOther].input_touch_info_other(con)
			# <!!>
			self.info[con.soMe].solid = con.soMe
			self.info[con.soOther].input_touch_info_me(con)

		# 計算処理
		for solid, info in self.info.items():
			if not info.ignore:
				info.update(1/20.0) # <!!>
		GainAdjuster.update()


		# Auto Ignore
		for solid, info in self.info.items():
			if not solid is None:
				#if "InputskelLeap" in solid.GetName():
				#	info.ignore = True
				if "Floor" in solid.GetName():
					info.ignore = True
				if "soUp" in solid.GetName():
					info.ignore = True
				if "soFoot" in solid.GetName():
					info.ignore = True
				if "Wall" in solid.GetName():
					info.ignore = True
				if "Basket" in solid.GetName():
					info.ignore = True


		# 描画
		for solid, info in self.info.items():
			if not info.ignore:
				self.att_visual_level[info.solid].input(info.att_visual)
				self.att_touch_level[info.solid].input( info.att_touch )
				try:
					if not self.visualizer is None:
						val = [
							( (info.solid.GetName()+" visual") , self.att_visual_level[info.solid].max ),
							( (info.solid.GetName()+" touch")  , self.att_touch_level[info.solid].max ),
							( (info.solid.GetName()+" top")    , info.att_topdown ),
						]
						self.visualizer.set(info.pos_world.curr_var, val)
				except:
					pass
				
				graph = Vis["Graph1"]
				if graph is not None:
					graph.set_graphdata(info.solid.GetName()[3:],     info.pos_world.curr_var, info.att_total)
					"""
					if "EyePosition" in info.solid.GetName(): # bpy.data.objects[info.solid.GetName()[3:]].select:
						graph.set_graphdata(info.solid.GetName()[3:]+"_base",     info.pos_world.curr_var, info.att_tpd_base)
						graph.set_graphdata(info.solid.GetName()[3:]+"_boring",   info.pos_world.curr_var, info.att_tpd_boring)
						graph.set_graphdata(info.solid.GetName()[3:]+"_wonder",   info.pos_world.curr_var, info.att_tpd_wonder)
						graph.set_graphdata(info.solid.GetName()[3:]+"_interest", info.pos_world.curr_var, info.att_tpd_interest)
					elif bpy.data.objects[info.solid.GetName()[3:]].select:
						graph.set_graphdata(info.solid.GetName()[3:]+"_base",     info.pos_world.curr_var, info.att_tpd_base)
						graph.set_graphdata(info.solid.GetName()[3:]+"_boring",   info.pos_world.curr_var, info.att_tpd_boring)
						graph.set_graphdata(info.solid.GetName()[3:]+"_wonder",   info.pos_world.curr_var, info.att_tpd_wonder)
						graph.set_graphdata(info.solid.GetName()[3:]+"_interest", info.pos_world.curr_var, info.att_tpd_interest)
					else:
						graph.clear_graphdata(info.solid.GetName()[3:]+"_base")
						graph.clear_graphdata(info.solid.GetName()[3:]+"_boring")
						graph.clear_graphdata(info.solid.GetName()[3:]+"_wonder")
						graph.clear_graphdata(info.solid.GetName()[3:]+"_interest")
					"""
		if not self.visualizer is None:
			self.visualizer.update()
