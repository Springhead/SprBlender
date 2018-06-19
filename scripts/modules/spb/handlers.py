# -*- coding: utf-8 -*-

import bpy
import spb
import time

from   copy                          import deepcopy
from   collections                   import defaultdict

from   spb.handlers_imp.scene        import SceneHandler
from   spb.handlers_imp.solid        import SolidHandler
from   spb.handlers_imp.pointer      import PointerHandler
from   spb.handlers_imp.shape        import ShapeHandler
from   spb.handlers_imp.joint        import JointHandler
from   spb.handlers_imp.limit        import LimitHandler
from   spb.handlers_imp.ikeff        import IKEffHandler
from   spb.handlers_imp.ikact        import IKActHandler
from   spb.handlers_imp.creature     import CreatureHandler
from   spb.handlers_imp.crbone       import CRBoneHandler
from   spb.handlers_imp.crcontroller import CRControllerHandler
from   spb.handlers_imp.visualizer   import VisualizerHandler

from   spb.utils                     import *
from   spb.spbapi                    import spbapi
from   spb.keyframebin               import KeyframeBin

from   Spr                           import *


class Handlers(defaultdict):
	'''ハンドラの一覧を管理するクラス．'''

	def __init__(self):
		self.is_initialized      = False

		defaultdict.__init__(self, lambda:NoneCheckDict())

		# ハンドラ一覧を作る
		self.handlers_list = []
		self.scene_handlers        = self.add_handlers( SceneHandler        )
		self.solid_handlers        = self.add_handlers( SolidHandler        )
		self.pointer_handlers      = self.add_handlers( PointerHandler      )
		self.shape_handlers        = self.add_handlers( ShapeHandler        )
		self.joint_handlers        = self.add_handlers( JointHandler        )
		self.limit_handlers        = self.add_handlers( LimitHandler        )
		self.ikeff_handlers        = self.add_handlers( IKEffHandler        )
		self.ikact_handlers        = self.add_handlers( IKActHandler        )
		self.creature_handlers     = self.add_handlers( CreatureHandler     )
		self.crbone_handlers       = self.add_handlers( CRBoneHandler       )
		self.crcontroller_handlers = self.add_handlers( CRControllerHandler )
		self.visualizer_handlers   = self.add_handlers( VisualizerHandler   )

		# シーンハンドラだけは最初に作る
		self.scene_handler = SceneHandler(bpy.context.scene)
		self.scene_handlers[self.scene_handler.name] = self.scene_handler

		self.last_step_enabled = False

		# これをFalseにするとHandlerの実行を一時的に止めることができる．
		self.operation = True

		# Creature Ruleの実行を行うかどうかをSpringhead Thread側から取得するための関数
		self.creature_rule_execution = False

		# Keyframe Recorder
		self.bake_mode  = False
		self.bake_frame_no = 0
		self.keys = KeyframeBin()
		self.record_step_count = 0
		
		#debug
		self.flag = 0
		self.step_count = 0;

	def add_handlers(self, HandlerClass):
		'''指定クラスのハンドラ一覧を作って返す'''
		handlers = self[HandlerClass]
		self.handlers_list.append(handlers)
		return handlers


	# --- --- --- --- ---
	# ステップ

	@logged
	def step(self):
		'''1ステップ分の処理を行う'''
		if self.operation==False:
			return

		# Step Enable処理
		'''
		debuglog.log("BEGIN", "Begin Step Enable/Disable Process.")
		enable = bpy.context.scene.spr_step_enabled
		if enable==True or enable==1:
			if not spbapi.GetHapticTimer().IsStarted():
				spbapi.GetHapticTimer().Start()
				if not spb.simulation_started:
					self.rule_init()
					spb.handlers.store("quickstore_on_start")
					spb.simulation_started = True
			if not spbapi.GetPhysicsTimer().IsStarted():
				spbapi.GetPhysicsTimer().Start()
				
		else:
			if spbapi.GetHapticTimer().IsStarted():
				spbapi.GetHapticTimer().Stop()
				spb.handlers.store("quickstore_on_end")
			if spbapi.GetPhysicsTimer().IsStarted():
				spbapi.GetPhysicsTimer().Stop()
		'''
		debuglog.log("BEGIN", "Begin Step Enable/Disable Process.")
		enable = bpy.context.scene.spr_step_enabled
		#print("start")
		if enable==True or enable==1:
			#print("enable")
			if not spbapi.GetPhysicsTimer().IsStarted():
				spbapi.GetPhysicsTimer().SetInterval(self.scene_handler.spr().GetTimeStep() * 1000)
				spbapi.GetPhysicsTimer().Start()
				#print("timer start")
				if not spb.simulation_started:
					self.rule_init()
					spb.handlers.store("quickstore_on_start")
					spb.simulation_started = True
				
		else:
			if spbapi.GetPhysicsTimer().IsStarted():
				spbapi.GetPhysicsTimer().Stop()
				spb.handlers.store("quickstore_on_end")

		# Creature Ruleを実行するかどうかのフラグをbpyから取得してspr用変数へコピー（spr threadから直接読むとコケるので）
		debuglog.log("BEGIN", "Begin Creature Rule Execution Flag Copy.")
		flag = bpy.context.scene.spr_creature_enabled==1 # <!!> and bpy.context.scene.spr_step_enabled==1
		self.creature_rule_execution = flag


		# シーンの強制アップデート
		bpy.context.scene.update()


		# キーフレーム書き出しモード
		if self.bake_mode:
			self.bake_step()
		
		#No Sync
		elif self.is_initialized and bpy.context.scene.spr_no_sync:
			pass

		# Minimal Sync
		elif self.is_initialized and bpy.context.scene.spr_minimal_sync:
			self.minimal_step()

		# 通常のSync処理
		else:
			self.full_step()


		# Keyframe Record処理
		if bpy.context.scene.spr_step_enabled and bpy.context.scene.spr_record:
			self.record_step()


		# スクリプトの実行
		if enable==True or enable==1:
			if True: #self.step_count % 5 == 0:
				self.creature_bpy_rule()


		self.step_count += 1


	@logged
	def full_step(self):
		'''完全自動同期モード'''
		self.generate()
		self.build()
		self.cleanup()
		self.sync()
		self.handler_step()
		self.is_initialized = True


	@logged	
	def minimal_step(self):
		'''最小同期モード'''
		# 実行時はspr->bpyの最小限同期を実行
		if bpy.context.scene.spr_step_enabled:
			if self.last_step_enabled==False:
				self.full_step()
			else:
				self.minimal_sync()

		self.last_step_enabled = bpy.context.scene.spr_step_enabled


	@logged
	def record_step(self):
		'''キーフレーム記録のステップ処理'''
		if self.record_step_count % bpy.context.scene.spr_record_every_n_steps == 0:
			self.record()
		self.record_step_count += 1
		bpy.context.scene.spr_recording_frame += 1


	@logged
	def bake_step(self):
		'''キーフレーム書き出し中のステップ処理'''
		self.keys.bake_frame(self.bake_frame_no)
		self.bake_frame_no += 1
		if self.bake_frame_no >= len(self.keys.keyframes):
			self.bake_mode = False
			debuglog.log("EVENT", "Bake Complete.")


	# --- --- --- --- ---
	# 全削除

	@logged
	def clear(self):
		'''ハンドラを全削除する'''
		# 関連オブジェクトの破壊
		for handlers in self.handlers_list.__reversed__():
			for handler in handlers.values():
				if handler:
					handler.destroy()

		# ハンドラの全削除
		for handlers in self.handlers_list.__reversed__():
			handlers.clear()

		# シーンハンドラも作り直し
		self.scene_handler = SceneHandler(bpy.context.scene)
		self.scene_handlers["Scene"] = self.scene_handler

		self.is_initialized = False


	# --- --- --- --- ---
	# 削除

	@logged
	def cleanup(self):
		'''不要になったハンドラを見つけてきて削除する．'''
		for handlers in self.handlers_list.__reversed__():
			self.cleanup_each_handlers(handlers)


	def cleanup_each_handlers(self, handlers):
		remove_list = []

		for handler in handlers.values():
			if (handler is None) or handler.must_removed():
				remove_list.append(handler)

		for handler in remove_list:
			debuglog.log("EVENT", "Removing ", handler, " as ", handler.name)
			handlers.pop(handler.name)
			handler.destroy()
			debuglog.log("END", "Remove Finished.")


	# --- --- --- --- ---
	# 生成・構築

	@logged
	def generate(self):
		'''対応するハンドラ一覧を生成する．
		一度生成済みの場合，未生成のハンドラ(新規追加要素等)のみ生成する．'''

		# -- Migration Check --
		if bpy.context.scene.spr_need_migration == 0:
			for obj in bpy.data.objects:
				if obj.spr_physics_type == "Dynamic":
					bpy.context.scene.spr_need_migration = 1

		# -- List Targets --
		handler_targets = []
		handler_targets += bpy.data.objects
		handler_targets += bpy.data.groups
		handler_targets += [ctl for grp in bpy.data.groups for ctl in grp.spr_controllers]
		handler_targets += [vis for grp in bpy.data.groups for vis in grp.spr_visualizers]

		# -- Generate Handlers --
		for target in handler_targets:
			for HandlerClass, handlers in self.items():
				if (not (target.name in handlers.keys()) and HandlerClass.is_target(target) ):
					handler = HandlerClass(target)
					handlers[target.name] = handler
					debuglog.log("EVENT", "Add ", handler, " named ", handler.name, " as ", type(handler))


	@logged
	def build(self):
		'''各ハンドラのbuild/post_buildを呼び出してSpringhead objectの構築を行う．'''
		# Build処理は毎回は行わない
		if self.step_count % 15 != 0:
			return

		need_sync = False

		# 構築・再構築
		for handlers in self.handlers_list:
			for handler in handlers.values():
				if handler:
					# ビルド情報と依存関係の更新
					handler.update()

					# 破壊
					if handler.build_info_changed or handler.dependency_changed:
						handler.destroy()
						debuglog.log("EVENT", "[Destroy]"+str(handler))
						handler.build_finished = False
					else:
						handler.rebuilt = False

					# 再生
					if not handler.build_finished: # ビルド完了するまで何度でも
						if (handler.build_info_completed and handler.dependency_ready):
							handler.post_build_finished = False
							try:
								handler.build_finished = handler.build()
								handler.rebuilt        = True
								need_sync              = True
								debuglog.log("EVENT", "[Build]"+str(handler))
							except:
								debuglog.log("ERROR", "[Build]"+traceback.format_exc())

		# 初期シンクロその１
		if need_sync:
			self.sync() # とりあえずシンクロしとかないとpost_buildに必要な状態が得られないとかそういう理由だったと思う
		
		# 後処理
		for handlers in self.handlers_list:
			for handler in handlers.values():
				if handler and handler.rebuilt:
					if not handler.post_build_finished:
						handler.post_build_finished = handler.post_build()
						need_sync = True

		# 初期シンクロその２と初期ストア
		if need_sync:
			self.sync()	# post_buildの結果を反映してもういちど！
			self.store("default")


	# --- --- --- --- ---
	# シンクロ

	@logged
	def sync(self):
		'''各ハンドラのsyncを呼び出して bpy<=>spr間の同期を行う．'''
		# Syncの順番は他とは異なる（依存関係のため）
		handlers_list = []
		handlers_list.append( self.scene_handlers        )
		handlers_list.append( self.shape_handlers        )
		handlers_list.append( self.solid_handlers        ) # Inertiaのためshapeよりあと
		handlers_list.append( self.joint_handlers        )
		handlers_list.append( self.limit_handlers        )
		handlers_list.append( self.ikeff_handlers        )
		handlers_list.append( self.ikact_handlers        )
		handlers_list.append( self.creature_handlers     )
		handlers_list.append( self.crbone_handlers       )
		handlers_list.append( self.crcontroller_handlers )
		handlers_list.append( self.visualizer_handlers   )

		# 前処理
		bpy.context.scene.update()
		for handlers in handlers_list:
			for handler in handlers.values():
				if handler:
					handler.update_bpy_object()

		# -- Before Sync
		for handlers in handlers_list:
			for handler in handlers.values():
				if handler:
					handler.before_sync()

		# -- Sync
		for handlers in handlers_list:
			for handler in handlers.values():
				if handler:
					debuglog.log("BEGIN", "Sync ", handler)
					handler.sync()
					debuglog.log("END", "Sync ", handler)

		# -- After Sync
		for handlers in handlers_list:
			for handler in handlers.values():
				if handler:
					handler.after_sync()


	@logged
	def minimal_sync(self):
		'''spr=>bpyの最小限の同期を行う．'''

		bpy.context.scene.update()

		# -- Solid Sync
		for handler in self.solid_handlers.values():
			if handler:
				'''
				handler.sync()
				'''
				new_spr = handler.state_sync.get_spr_value_mod(handler.state_sync.spr)
				handler.state_sync.bpy = to_bpy(new_spr)
				handler.state_sync.spr = copy(new_spr)
				handler.state_sync.set_bpy_value(handler.state_sync.bpy)
				#'''
		
		# -- Scene Step
		self.scene_handler.step()

		# -- Creature Step
		for handler in self.creature_handlers.values():
			if handler:
				handler.step()

	# --- --- --- --- ---
	# 個別ステップ

	@logged
	def handler_step(self):
		'''各ハンドラが1ステップごとに実行する内容を実行する．'''
		for handlers in self.handlers_list:
			for handler in handlers.values():
				if handler:
					handler.step()

	@logged
	def rule_init(self):
		if bpy.context.scene.spr_run_scripts_enabled==1:
			self.scene_handler.rule.update()
			self.scene_handler.rule.init()
		if self.creature_rule_execution:
			for creature in self.creature_handlers.values():
				creature.rule.update()
				creature.rule.init()

	@logged	
	def creature_rule(self):
		if self.creature_rule_execution:
			for creature in self.creature_handlers.values():
				creature.rule.step()

	@logged
	def creature_bpy_rule(self):
		if self.creature_rule_execution:
			for creature in self.creature_handlers.values():
				creature.rule.step_bpy()


	# --- --- --- --- ---
	# Store, ReStore

	def store(self, key):
		'''状態の一時保存を行う．'''
		for handlers in self.handlers_list:
			for handler in handlers.values():
				if handler:
					handler.store(key)
	
	def restore(self, key):
		'''保存しておいた状態に戻す．'''
		for handlers in self.handlers_list:
			for handler in handlers.values():
				if handler:
					handler.restore(key)

		# spr=>bpy に一方通行のsyncが必要
		bpy.context.scene.update()
		for handler in self.solid_handlers.values():
			if handler:
				new_spr = handler.state_sync.get_spr_value_mod(handler.state_sync.spr)
				handler.state_sync.bpy = to_bpy(new_spr)
				handler.state_sync.spr = copy(new_spr)
				handler.state_sync.set_bpy_value(handler.state_sync.bpy)


	# --- --- --- --- ---
	# 描画機能

	def draw3d(self):
		'''３次元描画を行う'''
		for handlers in self.handlers_list:
			for handler in handlers.values():
				if handler:
					handler.draw3d()
		
	def draw2d(self):
		'''２次元描画を行う'''
		for handlers in self.handlers_list:
			for handler in handlers.values():
				if handler:
					handler.draw2d()
		
	
	# --- --- --- --- ---
	# キーフレーム録画

	def record(self):
		'''キーフレームに記録する'''
		frame = bpy.context.scene.spr_recording_frame

		handlers_list = []
		handlers_list.append( self.scene_handlers      )
		handlers_list.append( self.solid_handlers      )
		handlers_list.append( self.visualizer_handlers )

		for handlers in handlers_list:
			for handler in handlers.values():
				if handler:
					handler.record(frame)
		
		
