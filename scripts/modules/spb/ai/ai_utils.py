# -*- coding: utf-8 -*-

import time

from   collections import defaultdict
from   random      import random
from   Spr         import *
from   spb.utils   import *


def s_curve(x, begin=0, end=1, max=1, min=0, invert=False):
	'''S字折れ線関数．'''
	if x < begin:
		return min
	if end < x:
		return max
	if invert:
		m = -(max-min) / (end-begin)
		b = max-m*begin
	else:
		m = (max-min) / (end-begin)
		b = min-m*begin
	return m*x + b


def rand(mean=0.5, error=0.5, integer=False):
	'''mean ± error の乱数を発生する．'''
	if integer:
		r = int( random()*(error*2 + 1) )
	else:
		r = random()*error*2
	return r + (mean - error)


def spheric_random():
	'''半径1の球体内に分布するランダムなVec3dを返す．'''
	v = Vec3d(rand(0,error=1), rand(0,error=1), rand(0,error=1))
	while v.norm() > 1:
		v = Vec3d(rand(0,error=1), rand(0,error=1), rand(0,error=1))
	return v


def point_in(empty_name, point=None):
	if point is None:
		'''empty_nameで表されるEmptyオブジェクト(Sphere前提)の内部に入る点をランダムに返す'''
		if empty_name in bpy.data.objects:
			empty  = bpy.data.objects[empty_name]
			center = to_spr(bpy_object_pose(empty).translation)
			random = spheric_random()
			scale  = empty.scale
			return center+Vec3d(random.x*scale.x, random.y*scale.y, random.z*scale.z)
		else:
			return Vec3d()

	else:
		'''pointが，empty_nameで表されるEmptyオブジェクト(Sphere前提)の内部にあるか判定する'''
		if empty_name in bpy.data.objects:
			empty  = bpy.data.objects[empty_name]
			center = to_spr(bpy_object_pose(empty).translation)
			relpos = point - center
			scale  = empty.scale
			scaled = Vec3d(relpos.x/scale.x, relpos.y/scale.y, relpos.z/scale.z)
			return scaled.norm() <= 1
		else:
			return False


def point_of(name):
	'''nameで示されるobjectの座標を返す．'''
	if name in bpy.data.objects:
		return to_spr(bpy.data.objects[name].matrix_world.to_translation())
	else:
		return Vec3d()


class DelaySelect:
	'''mintime[秒]以上経過してはじめて切り替わりが発生するような仕組み．'''
	def __init__(self, mintime):
		self.lastchangetime = time.time()
		self.mintime = mintime
		self.selection = None

	def force_input(self, item):
		self.selection = item
		self.lastchangetime = time.time()
		
	def input(self, item):
		if time.time() - self.lastchangetime > self.mintime:
			if not item==self.selection:
				self.selection = item
				self.lastchangetime = time.time()
				return True
		return False


class StateMachine:
	'''便利なステートマシン．'''
	def __init__(self):
		self.state       = "Init"
		self.laststate   = "Init"
		self.entertime   = time.time()
	
	def step(self):
		self.on_enter  = (not self.laststate == self.state)
		if self.on_enter:
			self.entertime = time.time()
			# print(self.state)

		self.laststate = self.state
		nextstate = getattr(self, "On"+self.state)()
		self.state = nextstate if (not nextstate is None) else self.state

	def waited(self, waittime):
		'''最後の状態遷移からwaittime秒経ったらTrue'''
		return time.time() - self.entertime > waittime

	def percent(self, pct):
		'''pct％の確率でTrue'''
		return( random() < (pct/100) )
		
	def OnInit(self):
		pass