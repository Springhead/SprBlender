# -*- coding: utf-8 -*-

import bpy
import spb

from   copy              import deepcopy

from   Spr               import *
from   spb.utils         import *

import time


class Handler():
	'''ハンドラ：Sprとbpyをつなぐユニットのベースクラス'''

	def __init__(self):
		# blenerオブジェクト
		self.object = None

		# blenerオブジェクトを引くための名前
		self.name = ""

		# シンクロナイザ
		self.synchronizers = []

		# Springheadオブジェクト構築が完了したか
		self.build_finished = False

		# Springheadオブジェクトの構築を行ったかどうか。依存関係にあるハンドラがspr再構築を行うかの目印
		self.rebuilt = False

		# Springheadオブジェクト構築後の処理が正しく完了したか
		self.post_build_finished = False  # <このフラグは初期状態storeと共用なので注意すること>

		# 依存関係にあるハンドラ。相手がspr再構築した（=rebuilt）場合こちらも自動で再構築する。
		self.dependency = {"nothing" : True}
		self.dependency_changed   = False # 依存ハンドラの構成や内容に変化が生じた
		self.dependency_completed = False # 必要な依存ハンドラが全て取得できた
		self.dependency_ready     = False # 依存ハンドラのbuildが全て完了している

		# Springheadオブジェクトの構築に必要な情報。
		self.build_info = {"nothing" : True}
		self.build_info_changed   = False # ビルド情報に変化が生じた
		self.build_info_completed = False # 必要なビルド情報が全て取得できた
		
		# Save,LoadState用Buff
		self.save = {}

		# StoreSpecial用の変数テーブル
		self.store_data = {}

	def update_bpy_object(self):
		'''bpyオブジェクトの生存確認（と必要があれば再取得）を行う。'''
		if self.object:
			if (self.object.users==0) and (self.name in bpy.data.objects):
				self.object = bpy.data.objects[self.name]

	def update(self):
		'''ビルド情報と依存関係のアップデートを行う'''
		# ビルド情報の更新
		self.build_info_changed = False
		last_build_info = deepcopy(self.build_info)
		self.build_info.clear()
		self.build_info_completed = self.update_build_info()
		if (last_build_info != self.build_info):
			self.build_info_changed = True

		# 依存関係の更新
		self.dependency_changed = False
		last_dependency = self.dependency.copy()
		self.dependency.clear()
		self.dependency_completed = self.update_dependency()
		for key, hnd in self.dependency.items():
			if hnd is None:
				self.dependency_completed = False
		if (last_dependency != self.dependency):
			self.dependency_changed = True

		# 依存ハンドラがrebuildされた場合も依存関係の変更とみなす
		self.dependency_ready = False
		if self.dependency_completed:
			self.dependency_ready = True
			for key, hnd in self.dependency.items():
				if hnd.rebuilt:
					self.dependency_changed = True
				if not hnd.build_finished:
					self.dependency_ready   = False

	def before_sync(self):
		'''Synchronize前に行う処理を記述する。オーバーライド用。'''
		pass

	def after_sync(self):
		'''Synchronize後に行う処理を記述する。オーバーライド用。'''
		pass

	def sync(self):
		'''bpy<=>spr間の同期を行う。'''
		# 同期
		if self.build_finished: # 構築が正しく完了するまでは動かない
			for synchronizer in self.synchronizers:
				try:
					if self.rebuilt or synchronizer.bpy_sync_cond():
						new_bpy = synchronizer.get_bpy_value_mod(synchronizer.bpy)
						synchronizer.bpy = copy(new_bpy)
						synchronizer.spr = to_spr(new_bpy)
						synchronizer.set_spr_value(synchronizer.spr)
						
					elif synchronizer.spr_sync_cond():
						new_spr = synchronizer.get_spr_value_mod(synchronizer.spr)
						synchronizer.bpy = to_bpy(new_spr)
						synchronizer.spr = copy(new_spr)
						synchronizer.set_bpy_value(synchronizer.bpy)

				except (AttributeError, KeyError, TypeError):
					debuglog.log("ERROR", "synchronization error was ignored")

	def sync_spr_to_bpy(self):
		'''spr=>bpyの反映のみ行う（更新チェックもしない）。'''
		for synchronizer in self.synchronizers:
			synchronizer.sync_spr_to_bpy()
	
	def sync_bpy_to_spr(self):
		'''bpy=>sprの反映のみ行う'''
		for synchronizer in self.synchronizers:
			synchronizer.sync_bpy_to_spr()


	# ---

	def store(self, key):
		'''状態の一時保存を行う。'''
		# Springhead Store
		if self.spr_storable():
			stat = ObjectStates().Create()
			stat.SingleSave(self.spr())
			self.save[key] = stat

		# Synchronizer Store
		for synchronizer in self.synchronizers:
			if synchronizer.storable():
				synchronizer.store(key)

		# Special Store
		self.store_special(key)
			
	def restore(self,key):
		'''保存しておいた状態に戻す。'''
		try:
			# Springhead Restore
			if self.spr_storable():
				if key in self.save:
					self.save[key].SingleLoad(self.spr())

			# Synchronizer Restore
			for synchronizer in self.synchronizers:
				if synchronizer.storable():
					synchronizer.restore(key)

			# Special Restore
			self.restore_special(key)

		except TypeError:
			debuglog.log("ERROR", "restore error was ignored : ", self)


	# --

	def update_build_info(self):
		'''Springheadオブジェクトの構築に必要な情報を更新。これが変化すると再構築される。
		ビルドに必要な情報がすべて出揃った場合のみTrueを返すこと'''
		return True

	def update_dependency(self):
		'''依存関係を更新。これが変化すると再構築される。
		ビルドに必要な依存ハンドラがすべて出揃った場合のみTrueを返すこと'''
		return True

	def destroy(self):
		'''Springheadオブジェクトを削除する。存在しないものものを消さないように気をつけること'''
		pass

	def build(self):
		'''対応するSpringhead側オブジェクトを構築する。
		ビルドが成功した場合のみTrueを返すこと（それまでsynchronizeは動作しない）'''
		return True

	def post_build(self):
		'''Springheadオブジェクト構築後に行う必要のある後処理。Trueを返すまで何度でも呼ばれる'''
		return True

	# --

	def bpy(self):
		'''このハンドラが対応する（広義の）bpyオブジェクト。削除判定に使う'''
		return self.object
	
	def spr(self):
		'''自分の持つsprオブジェクトを返す'''
		return None
		
	def spr_storable(self):
		'''Springheadの機能を利用したStore/Restoreが可能かを返す。
		Stateを持たないSpringhead ObjectへのHandlerを作る場合はオーバーライドすること'''
		return( not self.spr() is None )

	def store_special(self, key):
		'''SpringheadのState以外に独自のStore/Restoreを定義する場合にオーバーライドする'''
		pass
	
	def restore_special(self, key):
		'''SpringheadのState以外に独自のStore/Restoreを定義する場合にオーバーライドする'''
		pass

	def must_removed(self):
		'''このハンドラはもはや消滅すべき状態なのではないだろうかと自問する'''
		o = self.bpy()
		return (o.users==0) or (not type(self).is_target(o))

	def step(self):
		'''1ステップごとに実行する内容を記述する。Ruleの実行など'''
		pass

	def draw3d(self):
		'''描画を行う（３次元）'''
		pass

	def draw2d(self):
		'''描画を行う（２次元）'''
		pass

	def record(self, frame):
		'''キーフレームへの記録を行う。'''
		pass

	def __str__(self):
		return( type(self).__name__ + "<" + self.name + ">" )
