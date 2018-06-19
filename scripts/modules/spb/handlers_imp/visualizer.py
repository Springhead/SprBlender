# -*- coding: utf-8 -*-

import bpy
import bgl
import blf
import spb

from   math             import sin, cos, tan, pi
from   mathutils        import Vector,Quaternion
from   collections      import defaultdict
from   spb.handler      import Handler
from   spb.spbapi       import spbapi

from   Spr              import *
from   spb.synchronizer import *
from   spb.utils        import *


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handler
#

class VisualizerHandler(Handler):
	'''個々のビジュアライザに対応するハンドラ．'''

	def __init__(self, visualizer):
		Handler.__init__(self)
		self.name       = visualizer.name

		# Bpy Object
		self.visualizer = visualizer
		self.group      = bpy.data.groups[self.visualizer.creaturename]

		# Spr Object
		pass

		# Linked Handlers
		pass

		# Others
		self.viewport   = None
		self.projection = None
		self.modelview  = None

		self.list  = [[], []]

		self.graphdata = defaultdict(lambda: [])
		self.graphpositions = {}
		self.colors   = [(0,0,1), (1,0,1), (0,1,0), (0,1,1), (1,0,0), (1,1,0), (1,1,1)]
		self.colortable = {}
		self.colorindex = 0
		self.bold_name = ""

	def bpy(self):
		if self.name in self.group.spr_visualizers:
			return self.group.spr_visualizers[self.name]
		else:
			return None

	def must_removed(self):
		if self.bpy() is None:
			return True
		return False

	@classmethod
	def is_target(cls, object):
		'''オブジェクトがこのハンドラの対象となるべきものであるかを返す'''
		return type(object) is spb.properties.CreatureVisualizer

	def glGetMatrix(self, type):
		buf = bgl.Buffer(bgl.GL_FLOAT, [4,4])
		bgl.glGetFloatv(type, buf)
		mat = Matrix()
		for i in range(0,4):
			for j in range(0,4):
				mat[i][j] = buf[j][i]
		return mat

	def draw3d(self):
		'''描画を行う（３次元）'''
		# 2次元描画用に各種行列を保存しておく
		self.viewport   = self.glGetMatrix(bgl.GL_VIEWPORT)
		self.projection = self.glGetMatrix(bgl.GL_PROJECTION_MATRIX)
		self.modelview  = self.glGetMatrix(bgl.GL_MODELVIEW_MATRIX)

		# 各ビジュアライザの描画
		if self.bpy().type == "FOV":
			self.draw_fov()

	def draw2d(self):
		'''描画を行う（２次元）'''
		if self.bpy().type == "Attention":
			self.draw_attention()
		if self.bpy().type == "Name":
			self.draw_name()
		if self.bpy().type == "Graph":
			self.draw_graph()

	# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- 

	def update(self):
		self.list[0] = self.list[1]
		self.list[1] = []

	def get_pos_2d(self, pos_3d):
		if self.viewport and self.projection and self.modelview:
			v = self.projection * self.modelview * pos_3d
			if (v.z < 0.03):
				v = (v * 0.5) + Vector((0.5,0.5,0))
			else:
				v = (v * (1/v.z) * 0.5) + Vector((0.5,0.5,0))
			width  = self.viewport[2][0]
			height = self.viewport[3][0]
			x = width  * v.x
			y = height * v.y
			return Vector((x, y, 0))

		else:
			return pos_3d

	# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- 

	def draw_fov(self):
		if not self.bpy().show:
			return

		for crHnd in spb.handlers.creature_handlers.values():
			for i in range(crHnd.spr().NEngines()):
				vs = crHnd.spr().GetEngine(i)
				if type(vs) is CRVisualSensor:
					# --- --- --- --- ---
					# Draw Peripheral FOV
					m     = to_bpy( vs.GetSolid().GetPose() * vs.GetPose() )
					fov   = vs.GetRange()
					horiz = fov.x
					vert  = fov.y

					# -- Draw Cone --
					bgl.glBegin(bgl.GL_TRIANGLE_FAN)

					depth        = 60.0
					vertices_num = 32
					radius_alt   = depth * tan(vert /2)
					radius_az    = depth * tan(horiz/2)

					bgl.glColor4f(0.0, 1.0, 0.0, 0.3)

					v = m * Vector((0,0,0))
					bgl.glVertex3f(v.x, v.y, v.z)
					
					for i in range(0, vertices_num+1):
						x =  radius_az  * cos(i * pi/(vertices_num/2))
						y = -depth
						z =  radius_alt * sin(i * pi/(vertices_num/2))
						v = m * Vector((x,y,z))

						bgl.glVertex3f(v.x, v.y, v.z)

					bgl.glEnd()

					# --- --- --- --- ---
					# Draw Central FOV
					m     = to_bpy( vs.GetSolid().GetPose() * vs.GetPose() )
					fov   = vs.GetCenterRange()
					horiz = fov.x
					vert  = fov.y

					# -- Draw Cone --
					bgl.glBegin(bgl.GL_TRIANGLE_FAN)

					depth        = 60.0
					vertices_num = 32
					radius_alt   = depth * tan(vert /2)
					radius_az    = depth * tan(horiz/2)

					bgl.glColor4f(1.0, 0.0, 0.0, 0.3)

					v = m * Vector((0,0,0))
					bgl.glVertex3f(v.x, v.y, v.z)
					
					for i in range(0, vertices_num+1):
						x =  radius_az  * cos(i * pi/(vertices_num/2))
						y = -depth
						z =  radius_alt * sin(i * pi/(vertices_num/2))
						v = m * Vector((x,y,z))

						bgl.glVertex3f(v.x, v.y, v.z)

					bgl.glEnd()


	# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- 

	def set_graphdata(self, name, pos, value):
		q = self.graphdata[name]
		q.append(value)
		self.graphdata[name] = q[-200:]
		self.graphpositions[name] = to_bpy(pos)
		if not name in self.colortable:
			self.colortable[name] = self.colors[self.colorindex]
			self.colorindex = (self.colorindex + 1) % len(self.colors)

	def set_graph_bold(self, name):
		self.bold_name = name

	def clear_graphdata(self, name):
		if name in self.graphdata:
			self.graphdata.pop(name)

	def draw_graph(self):
		if not self.bpy().show:
			return

		#max_name = max([[values[-1], name] for name, values in self.graphdata.items()])[1]

		cnt = 0
		for name, values in self.graphdata.items():
			if name == self.bold_name:
				bgl.glLineWidth(3)
			else:
				bgl.glLineWidth(1)

			col = self.colortable[name]
			bgl.glColor4f(col[0], col[1], col[2], 1.0)

			cx = 100
			cy = 100

			t = 200 - len(values)
			last_x = 0
			last_y = 0
			bgl.glBegin(bgl.GL_LINE_STRIP)
			for value in values:
				t += 1
				last_x = t*4 + cx
				last_y = value*100 + cy
				bgl.glVertex2f(last_x, last_y)
			bgl.glEnd()

			pos = self.get_pos_2d(self.graphpositions[name])
			bgl.glBegin(bgl.GL_LINES)
			bgl.glVertex2f(last_x, last_y)
			bgl.glVertex2f(pos.x, pos.y)
			bgl.glEnd()

			# Draw Label
			font_id = 0
			blf.position(font_id, pos.x, pos.y, 0)
			blf.size(font_id, 10, 72)
			blf.draw(font_id, name)

			cnt += 1


	# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- 

	def set(self, pos, value):
		self.list[1].append( (to_bpy(pos), value) )

	def draw_attention(self):
		if not self.bpy().show:
			return

		colors   = [(0,0,1), (1,0,1), (0,1,0), (0,1,1), (1,0,0), (1,1,0), (1,1,1)]

		bgl.glEnable(bgl.GL_BLEND)
		for item in self.list[0]:
			colors_idx = 0
			col = colors[colors_idx]
			bgl.glColor4f(col[0], col[1], col[2], 0.5)

			pos = self.get_pos_2d(item[0])
			val = item[1]

			sum = 0
			accum = []
			for label,x in val:
				sum += x
				accum.append(sum)

			indicator_range_max = 4
			for i in range(0,len(accum)):
				accum[i] = accum[i] / indicator_range_max

			bgl.glBegin(bgl.GL_TRIANGLE_FAN)
			bgl.glVertex2f(pos.x, pos.y)
			
			w = self.viewport[2][0]
			radius = w / 50
			vertices_num = 32
			for i in range(0, vertices_num+1):
				x =  pos.x + radius*cos(i * pi/(vertices_num/2))
				y =  pos.y + radius*sin(i * pi/(vertices_num/2))
				bgl.glVertex2f(x, y)

				while len(accum)>0 and i/vertices_num <= accum[0] and accum[0] <= (i+1)/vertices_num:
					r = accum[0]
					x =  pos.x + radius*cos(2 * pi * r)
					y =  pos.y + radius*sin(2 * pi * r)

					bgl.glVertex2f(x, y)

					accum = accum[1:]
					colors_idx += 1
					if colors_idx >= len(colors):
						colors_idx = 0

					col = colors[colors_idx]
					bgl.glColor4f(col[0], col[1], col[2], 0.5)
					bgl.glVertex2f(x, y)

				if len(accum)==0:
					break

			bgl.glEnd()

			# Draw Text Info <!!>
			if False:
				font_id = 0
				cnt = 0
				bgl.glColor4f(1, 1, 1, 1)
				for label,x in val:
					txt = (label + " : " + ("%.2f" % x))
					blf.position(font_id, pos.x, pos.y + cnt*10, 0)
					blf.size(font_id, 10, 72)
					blf.draw(font_id, txt)
					cnt += 1

		bgl.glDisable(bgl.GL_BLEND)
