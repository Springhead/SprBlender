# -*- coding: utf-8 -*-

#
# Override bl_ui/properties_object.py
#

import bpy
import bgl
import blf

import Spr

import time
import random

import spb.properties
import spb.ui

# import spb.pitch.spectrum_analyzer
# import spb.pitch.optimize_double

from   spb.properties    import register_properties
from   spb.handlers      import Handlers
from   spb.spbapi        import spbapi
from   mathutils         import Vector,Quaternion

from   spb.utils         import *

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# UI Override
# * Depends on Blender Version *
#
if bpy.app.version[1] >= 70:
	import spb.ui_override_2_70
else:
	import spb.ui_override_2_69



# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Handlers
#

handlers = Handlers()



# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Initial Settings
#

simulation_started = False

# デバッグ表示関連
debuglog.log_print = True
# debuglog.log_file  = True
debuglog.level     = "EVENT";

som = None
last_posi = None
data = []
posi_x = None
posi_y = None

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Operator
#


def draw_callback_pixel(self, context):
	'''２次元描画コールバック'''
	handlers.draw2d()

def draw_callback_view(self, context):
	'''３次元描画コールバック'''

	bgl.glEnable(bgl.GL_BLEND)
	bgl.glColor4f(1.0, 0.0, 0.0, 0.5)
	bgl.glLineWidth(2)

	handlers.draw3d()

	bgl.glLineWidth(1)
	bgl.glDisable(bgl.GL_BLEND)
	bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


class SprOperator(bpy.types.Operator):
	'''SprPyBlender Operator'''
	bl_idname = "spr.operator"
	bl_label  = "SprOperator"

	timer = None
	step_count = 0
	prev_time  = time.time()
	
	def modal(self, context, event):
		# context.area.tag_redraw()
		
		if event.type == 'TIMER':
			# ハンドラの処理を行う
			debuglog.log("BEGIN", "Handler Step Begin.")
			handlers.step()
			debuglog.log("END", "Handler Step Done.")

			# CPSを計測する
			self.step_count += 1
			curr_time  = time.time()
			time_delta = curr_time - self.prev_time
			if time_delta > 1.0:
				self.prev_time = curr_time
				context.scene.spr_op_cps_count = (self.step_count / time_delta)
				self.step_count = 0

			context.scene.spr_phys_cps_count = spbapi.GetCPS()

		return {'PASS_THROUGH'}

	def execute(self, context):
		#timer登録
		context.window_manager.modal_handler_add(self)
		self.timer = context.window_manager.event_timer_add(1/100.0, context.window)

		# 描画ハンドラの登録
		args = (self, context)
		SprOperator.draw_view  = bpy.types.SpaceView3D.draw_handler_add(draw_callback_view,  args, 'WINDOW', 'POST_VIEW')
		SprOperator.draw_pixel = bpy.types.SpaceView3D.draw_handler_add(draw_callback_pixel, args, 'WINDOW', 'POST_PIXEL')

		return {'RUNNING_MODAL'}

	def cancel(self, context):
		spbapi.GetHapticTimer().Stop()
		spbapi.GetPhysicsTimer().Stop()
		spbapi_cpp.Enable(False)
		context.window_manager.event_timer_remove(self.timer)
		return {'CANCELLED'}



# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#
# Start Operation
#

def startup():
	'''ファイルロード時，オペレータを再登録'''
	debuglog.log("BEGIN", "Begin Startup Process.")

	# 登録されたものがあれば一度登録解除
	bpy.utils.unregister_module(__name__)
	debuglog.log("PASS", "-- Unregister Module Done.")

	# オペレータ及びプロパティの登録
	bpy.utils.register_module(__name__)
	register_properties()
	debuglog.log("PASS", "-- Register module Done.")

	# ハンドラの初期化
	spb.handlers.clear()
	debuglog.log("PASS", "-- Clear Handlers Done.")

	# Springheadの初期化
	spb.spbapi.Init()
	debuglog.log("PASS", "-- Init Springhead Done.")

	# オペレータ有効化
	bpy.ops.spr.operator()
	debuglog.log("PASS", "-- Enable Operator Done.")
	
	# 次回同じファイルをロードしたときには自動でimport spb & startupする
	if not "start_spb.py" in bpy.data.texts:
		textedit = bpy.data.texts.new("start_spb.py")
		s = ""
		s += "import bpy\n"
		s += "def on_load(context):\n"
		s += "\timport spb\n"
		s += "\tspb.startup()\n"
		s += "bpy.app.handlers.load_post.append(on_load)\n"
		textedit.from_string(s)
		textedit.use_module = True

	debuglog.log("END", "Startup Process Done.")

# はじめてimport spbしたファイルだった場合，ここでstartupする
# （start_spb.pyがRegisterでない場合も）
if (not "start_spb.py" in bpy.data.texts) or (not bpy.data.texts["start_spb.py"].use_module):
	startup()
