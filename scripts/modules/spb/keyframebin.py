# -*- coding: utf-8 -*-

import bpy

from   spb.utils      import *
from   Spr            import *
from   collections    import defaultdict


class KeyframeBin():
	'''キーフレームを一時記録して後でBlenderに書き出すためのクラス．'''

	def __init__(self):
		self.keyframes = []
		
	def insert(self, object, frame, location=False, rotation=False, scale=False):
		'''あるオブジェクトの位置・姿勢・スケールをキーフレームとして記録'''
		if bpy.context.scene.spr_record_to_cache:
			# Keyframe Cacheを使う場合
			while len(self.keyframes) < (frame+1):
				self.keyframes.append({})
			key = [object, None, None, None, frame]
			if location:
				key[1] = object.location.copy()
			if rotation:
				key[2] = object.rotation_quaternion.copy()
			if scale:
				key[3] = object.scale.copy()
			self.keyframes[frame][object] = key

		else:
			# Keyframe Cacheを使わず直接書き込む場合（重い）
			if location:
				object.keyframe_insert(data_path="location", frame=frame)
			if rotation:
				object.keyframe_insert(data_path="rotation_quaternion", frame=frame)
			if scale:
				object.keyframe_insert(data_path="scale", frame=frame)
			

	def bake_frame(self, frame):
		'''Keyframe Cacheの内容をBlenderのキーフレームに書き込み'''
		keyframe = self.keyframes[frame]
		for key in keyframe.values():
			object = key[0]

			if not key[1] is None:
				object.location = key[1]
				object.keyframe_insert(data_path="location", frame=frame)
			if not key[2] is None:
				object.rotation_quaternion = key[2]
				object.keyframe_insert(data_path="rotation_quaternion", frame=frame)
			if not key[3] is None:
				object.scale = key[3]
				object.keyframe_insert(data_path="scale", frame=frame)

		if frame % 50 == 0:
			debuglog.log("EVENT", "Wrote #", frame, " / ", len(self.keyframes))

	
