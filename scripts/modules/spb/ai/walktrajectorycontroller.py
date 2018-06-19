# -*- coding: utf-8 -*-

import spb
import bgl

from   collections  import defaultdict
from   spb.utils    import *
from   spb.abbrev   import *
from   Spr          import *
from   math         import *
from   numpy        import *


class WalkTrajectoryController():
	def __init__(self):
		self.init_pos    = Vec2d(0,0)
		self.init_vel    = Vec2d(0,0)

		self.targ_pos    = Vec2d(0,0)
		self.targ_vel    = Vec2d(0,0)

		self.curr_pos    = Vec2d(0,0)
		self.curr_vel    = Vec2d(0,0)

		self.final_pos   = Var(lambda:Vec2d(), alpha=1, diff_alpha=1)

		self.current_s   = 0
		self.b_waiting   = False

		self.traj_param  = [None, None]

		# キャラクタがジッサイに居る座標（一方curr_posは軌道上の座標）
		self.actual_pos  = Vec2d(0,0)

		# parameters
		self.wait_vel    = 0.5
		self.restart_vel = 0.45

		# recent direction
		self.last_direction = Vec3d(0,-1,0)

		# flug
		self.update_enable = True

	def set_final_pos(self, final_pos):
		self.final_pos.input(Vec2d(final_pos.x, final_pos.y))

	def step(self, actual_pos=None):
		self.actual_pos = actual_pos if not actual_pos is None else self.curr_pos

		# current_s以降の軌道上でAPに最も近い点のsを求め、それを新たにcurrent_sにする
		self.current_s  = self.get_nearest_s(self.actual_pos)

		# 軌道がない時、または起動終盤時のみenableをTrueに
		if (self.current_s == 0) or (self.current_s > 0.5):
			self.update_enable = True
		else :
			self.update_enable = False

		print('cur_s',self.current_s)

		# --

		dt = 1/80.0 # <!!>
		self.final_pos.update(dt)

		# --

		b_restart = False
		if self.b_waiting:
			if (self.final_pos.diff_var.norm() < self.restart_vel):
				self.b_waiting = False
				self.targ_pos = self.final_pos.curr_var
				b_restart = True

		else:
			if (self.final_pos.diff_var.norm() > self.wait_vel):
				self.b_waiting = True

		# --

		if b_restart:
			if self.current_s >= 1:
				self.curr_pos = self.actual_pos
				self.curr_vel = Vec2d(0,0)
			self.init_pos  = self.curr_pos
			self.init_vel  = self.curr_vel
			self.current_s = 0

		# --

		self.update_trajectory()

		point = self.get_trajectory(self.current_s)
		self.curr_pos = Vec2d(point[0], point[1])
		self.curr_vel = Vec2d(point[2], point[3])

		# --

		# <!!>
		# self.current_s = min(self.current_s+0.005, 1)

		# --

		self.final_pos.clear()


	def get_next_target(self, distance):
		'''curr_posからdistanceだけ離れた軌道上の（今よりも先の）点を返す'''

		curr_pos = self.get_trajectory_pos(self.current_s)

		s   = self.current_s
		pos = self.get_trajectory_pos(s)
		dis = (pos - self.curr_pos).norm()
		err = abs(distance - dis)
		min_s = s
		min_e = err
		for i in range(40):
			s   = (1-self.current_s) * i / 30 + self.current_s
			pos = self.get_trajectory_pos(s)
			dis = (pos - curr_pos).norm()
			err = abs(distance - dis)
			if err < min_e:
				min_s = s
				min_e = err

		if min_s < 0.1:
			s1 = min_s
			s2 = min_s+0.1
		else:
			s1 = min_s-0.1
			s2 = min_s
		p1 = self.get_trajectory_pos(s1)
		p2 = self.get_trajectory_pos(s2)

		direction = (p2 - p1)
		if direction.norm() < 0.001:
			direction = self.last_direction
		else:
			direction = direction.unit()
			self.last_direction = direction

		return (self.get_trajectory_pos(min_s), direction)


	def get_nearest_s(self, curr_pos):
		'''posに最も近い軌道上の（今よりも先の）点に対応するsを返す'''

		s   = self.current_s
		pos = self.get_trajectory_pos(s)
		dis = (pos - curr_pos).norm()
		min_s = s
		min_d = dis
		for i in range(40):
			s   = (1-self.current_s) * i / 30 + self.current_s
			pos = self.get_trajectory_pos(s)
			dis = (pos - curr_pos).norm()
			if dis < min_d:
				min_s = s
				min_d = dis

		return min_s


	def update_trajectory(self):
		if (self.init_pos - self.targ_pos).norm() < 1e-3:
			return

		t0 = 0
		tF = 1
		self.traj_param = [None, None]

		for i in range(2):

			A  = matrix([
			[1, t0, pow(t0,2),   pow(t0,3),    pow(t0,4),    pow(t0,5)],
			[0,  1,      2*t0, 3*pow(t0,2),  4*pow(t0,3),  5*pow(t0,4)],
			[0,  0,         2,        6*t0, 12*pow(t0,2), 20*pow(t0,3)],
			[1, tF, pow(tF,2),   pow(tF,3),    pow(tF,4),    pow(tF,5)],
			[0,  1,      2*tF, 3*pow(tF,2),  4*pow(tF,3),  5*pow(tF,4)],
			[0,  0,         2,        6*tF, 12*pow(tF,2), 20*pow(tF,3)],
			])

			b  = array([
			to_bpy(self.init_pos)[i],
			to_bpy(self.init_vel)[i],
			0                        ,
			to_bpy(self.targ_pos)[i],
			to_bpy(self.targ_vel)[i],
			0                        ,
			])

			self.traj_param[i] = dot(A.I, b)


	def get_trajectory(self, s):
		if (self.init_pos - self.targ_pos).norm() < 1e-3:
			return [self.targ_pos.x, self.targ_pos.y, self.targ_vel.x, self.targ_vel.y]
		if self.traj_param[0] is None or self.traj_param[1] is None:
			return [self.targ_pos.x, self.targ_pos.y, self.targ_vel.x, self.targ_vel.y]

		if s < 0:
			return [self.init_pos.x, self.init_pos.y, self.init_vel.x, self.init_vel.y]
		if 1 < s:
			return [self.targ_pos.x, self.targ_pos.y, self.targ_vel.x, self.targ_vel.y]

		result = [0,0,0,0]

		for i in range(2):
			c  = array([1, s, pow(s,2),   pow(s,3),   pow(s,4),   pow(s,5)])
			d  = array([0, 1,      2*s, 3*pow(s,2), 4*pow(s,3), 5*pow(s,4)])

			if self.traj_param[i] is not None:
				result[i]   = dot(self.traj_param[i], c)[0,0]
				result[i+2] = dot(self.traj_param[i], d)[0,0]

		traject = self.targ_pos - self.init_pos
		result[0] = self.init_pos.x + (traject.x * s)
		result[1] = self.init_pos.y + (traject.y * s)
		result[2] = 0
		result[3] = 0
		
		return result


	def get_trajectory_pos(self, s):
		point = self.get_trajectory(s)
		return Vec2d(point[0], point[1])


	def draw(self):
		bgl.glBegin(bgl.GL_LINE_STRIP)

		for i in range(40):
			s = i/40.0
			if (s < self.current_s):
				bgl.glColor4f(1.0, 0.2, 0.2, 1.0)
			else:
				bgl.glColor4f(0.2, 0.2, 1.0, 1.0)
			point = self.get_trajectory(s)
			bgl.glVertex3f(point[0], point[1], 0)

		bgl.glEnd()
