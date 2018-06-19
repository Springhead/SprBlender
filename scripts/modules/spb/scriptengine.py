# -*- coding: utf-8 -*-

import bpy
import sys
import traceback

from   spb.utils    import *

class ScriptEngine():
	def __init__(self):
		self.initRule    = ""
		self.stepRule    = ""
		self.bpyStepRule = ""
		self.drawRule    = ""
		self.initialized = False
		self.reset()

	def execute(self, script):
		'''scriptを実行する．'''
		try:
			exec(script, self.globals)
			return True
		except Exception as e:
			debuglog.log("ERROR", traceback.format_exc())
			return False

	def reset(self):
		'''変数類をリセットする．'''
		self.globals = {}

	def set_name(self, name):
		'''スクリプト名をセットする．'''
		self.name = name

	def update(self):
		'''テキストエディタからスクリプトを再読み込みする．'''
		self.reset()
		self.initRule    = self.update_rule(self.name+"_init"    , "")
		self.stepRule    = self.update_rule(self.name+"_step"    , "")
		self.bpyStepRule = self.update_rule(self.name+"_step_bpy", "")
		self.drawRule    = self.update_rule(self.name+"_draw"    , "")
		self.draw2dRule  = self.update_rule(self.name+"_draw2d"  , "")
		self.initialized = False

	def init(self):
		'''初期化スクリプトを実行する．'''
		if self.execute(self.initRule):
			self.initialized = True

	def step(self):
		'''ステップスクリプトを実行する．'''
		self.execute(self.stepRule)

	def step_bpy(self):
		'''bpyステップスクリプトを実行する．'''
		self.execute(self.bpyStepRule)

	def draw(self):
		'''描画スクリプトを実行する．'''
		self.execute(self.drawRule)

	def draw_2d(self):
		'''２次元描画スクリプトを実行する．'''
		self.execute(self.draw2dRule)

	def update_rule(self, rule_name, default_script=""):
		# 無ければ作る
		if not rule_name in bpy.data.texts:
			bpy.data.texts.new(rule_name)
			bpy.data.texts[rule_name].from_string(default_script)
		textedit = bpy.data.texts[rule_name]

		# .blendと同じディレクトリのファイルをimportできるようパスをセットしておく
		bnlen = len(bpy.path.basename(bpy.data.filepath))
		dir = bpy.data.filepath[0:-bnlen]
		if not dir in sys.path:
			sys.path.append(dir)

		# ファイル(External)ならリロードする
		if not textedit.filepath=='':
			filepath = textedit.filepath			

			# 相対パスの場合.blendのパスと置き換える
			if filepath[0:2]=='//':
				filepath = dir+filepath[2:]

			# スクリプト内で同じディレクトリのファイルをimportできるようパスをセットしておく
			bnlen = len(bpy.path.basename(filepath))
			dir = filepath[0:-bnlen]
			if not dir in sys.path:
				sys.path.append(dir)

			# スクリプトのリロード
			try:
				with open(filepath) as ifp:
					textedit.from_string(ifp.read())
			except FileNotFoundError:
				debuglog.log("ERROR", "Error : Rule Text Not Found for ", rule_name, " at ", filepath)

		return textedit.as_string()

