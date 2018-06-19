# -*- coding: utf-8 -*-

from   spb.utils    import *


class Synchronizer():
	'''BlenderとSpringheadの同期を担う機能のベースクラス'''

	def __init__(self, handler):
		self.handler  = handler
		self.bpy      = None
		self.spr      = None

		# Sync中断モード
		# 0 : 中断しない
		# 1 : 1回だけsyncして中断
		# 2 : 中断
		# 3 : Spr=>Bpyのみ(EditUnable)
		self.mode = 0
		

		# 他のSynchronizerが値を変更したい場合に使うmodifier（例：spring/damper ratio）
		self.modifiers = {}

		# 持ち主であるhandlerのsynchronizerリストに登録
		self.handler.synchronizers.append(self)

	def __str__(self):
		return( type(self).__name__ )

	def storable(self):
		'''storableでないことを返すための関数 (StorableSynchronizerでオーバーライドされる)'''
		return False

	def sync_spr_to_bpy(self):
		'''spr=>bpyの反映のみ行う（更新チェックもしない）．'''
		new_spr = self.get_spr_value_mod(self.spr)
		self.bpy = to_bpy(new_spr)
		self.spr = copy(new_spr)
		self.set_bpy_value(self.bpy)
	
	def sync_bpy_to_spr(self):
		'''bpy=>sprの反映のみ行う'''
		new_bpy = self.get_bpy_value_mod(self.bpy)
		self.spr = to_spr(new_bpy)
		self.bpy = copy(new_bpy)
		self.set_spr_value(self.spr)

	def get_bpy_value_mod(self, last):
		'''bpyの新しい値を取得し，modifierを適用して返す'''
		bpy = self.get_bpy_value(last)
		for key, value in self.modifiers.items():
			bpy_mod, spr_mod = value
			bpy = bpy_mod(bpy)
		return bpy
			
	def get_spr_value_mod(self, last):
		'''sprの新しい値を取得し，modifierを適用して返す'''
		spr = self.get_spr_value(last)
		for key, value in self.modifiers.items():
			bpy_mod, spr_mod = value
			spr = spr_mod(spr)
		return spr

	def bpy_sync_cond(self):
		'''bpy->sprのsyncを実行する条件：syncが有効（holdされてない）かつbpyに変更があるとき．'''
		hold = (self.mode==2)
		editunable = (self.mode==3)
		sync = (self.mode == 0)
		if self.mode==1:
			self.mode = 2
		return (not hold) and (not editunable) and (self.is_bpy_changed())
	
	def spr_sync_cond(self):
		'''spr->bpyのsyncのみを実行する条件 : syncが有効(holdされていない)かつsprに変更があるとき'''
		hold = (self.mode == 2)
		sync = (self.mode == 0)
		return self.is_spr_changed() and (not hold)

	def hold(self, v=True):
		'''Hold状態にする'''
		self.mode = 2 if v else 0

	def apply(self):
		'''Hold中なら1回だけsyncする'''
		self.mode = 1 if self.mode==2 else self.mode
	
	def editunable(self,v=True):
		'''Edit modeにする'''
		self.mode = 3 if v else 0 
	
	def transition(self, edit, hold, apply):
		if edit == 0:
			self.mode = 3		##editunable mode
			
		elif hold == 1:
			self.mode = 2		##hold mode
			
			if apply == 1:
				self.mode = 1	##apply mode
		
		else:
			self.mode = 0		##sync

	# -- 以下オーバーライド用

	def is_bpy_changed(self):
		'''bpyの新しい値を取得して，変更があったかを返す'''
		return( not self.bpy==self.get_bpy_value_mod(self.bpy) )

	def is_spr_changed(self):
		'''sprの新しい値を取得して，変更があったかを返す'''
		return( not self.spr==self.get_spr_value_mod(self.spr) )

	def get_bpy_value(self, last):
		'''bpyの新しい値を取得する'''
		return None
			
	def get_spr_value(self, last):
		'''sprの新しい値を取得する'''
		return None

	def set_bpy_value(self, value):
		'''sprに変更があった場合にbpyに反映する'''
		pass

	def set_spr_value(self, value):
		'''bpyに変更があった場合にsprに反映する'''
		pass




class StorableSynchronizer(Synchronizer):
	'''Store / Restoreに対応したシンクロナイザ．'''

	def __init__(self, handler):
		self.initialized  = NoneCheckDict()
		self.store_buffer = {}
		Synchronizer.__init__(self, handler)

	def storable(self):
		'''storableであることを返す'''
		return True

	def store(self, key):
		'''状態の一時保存を行う．'''
		self.store_buffer[key] = (self.bpy, self.spr)
		self.initialized[key] = True

	def restore(self, key):
		'''保存しておいた状態に戻す．'''
		if key in self.store_buffer and (self.mode==3 or self.mode==0):
			bpy, spr = self.store_buffer[key]
			self.set_bpy_value(bpy)
			self.set_spr_value(spr)
