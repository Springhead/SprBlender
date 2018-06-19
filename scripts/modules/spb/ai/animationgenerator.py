import spb

from Spr       import *
from spb.utils import *
from math      import *
from numpy     import *

from spb.ai.walkcontroller import *
from spb.ai.ai_utils       import *
from spb.ai.walkcontroller import *


class AnimationGenerator(StateMachine):
	def __init__(self, scene, nameList, soFloor, soBase, soWaist, touchsensor, animectl, joWaist, config):
		StateMachine.__init__(self)

		self.config = config

		self.walkctl  = WalkController(scene, nameList, soFloor, soBase, soWaist, touchsensor, config)
		self.animectl = animectl
		self.joWaist = joWaist
		self.soWaist = soWaist
		self.soBase = soBase

		self.target = Vec3d(0,0,0)
		self.scene  = scene

		self.lastFootPos = Vec3d(0,0,0)

		self.judge = 0

		# フェーズ関連
		# ステップの単位距離
		self.STEP_PHASE_X = 1
		self.STEP_PHASE_Y = 2
		# 現在のステップフェーズ
		self.phaseX = 0
		self.phaseY = 0

		# デバッグ用
		self.hosu = 0

	def animeStep(self, scene, target, nameList):
		# target = [tarPos, tarAng, tarVel, tarAngVel, tarAngBody]
		self.target = target
		self.scene  = scene
		StateMachine.step(self)

	def animationState(self):
		self.state = "Walking"

	def OnWalking(self):
		self.walkctl.step(self.scene, self.target)

		if self.walkctl.getState() == "Walking" :			
			self.phaseStep()
			self.animectl.enable(True)
			self.joWaist.Enable(True)

		elif self.walkctl.getState() == "Standing" :
			self.animectl.enable(False)
			self.joWaist.Enable(True)
			self.state = "Standing"

		elif self.walkctl.getState() == "Falling" :
			self.animectl.enable(False)
			self.joWaist.Enable(False)
			self.state = "Falling"

	def OnStanding(self):
		if self.walkctl.getState() == "Walking" :
			self.walkctl.initializeModel(self.getFootPos(self.animectl))		
			self.walkctl.setWaistPose(self.soBase, self.soWaist)
			self.animectl.enable(True)
			self.state = "Walking"
		elif self.walkctl.getState() == "Standing" :
			pass
		else :
			pass

	def OnFalling(self):
		self.walkctl.step(self.scene, self.target)
		#　現在の姿勢ベクトル
		posture = self.soWaist.GetPose().getPos() - self.getFootPos(self.animectl)
		standEnable = False

		stand = (acos(posture.unit() * Vec3d(0,0,1)) < 1)

		if stand:
			self.judge += 1
			if (self.judge > 60):
				standEnable = True
		else :
			self.judge = 0
		
		#print('selfjudge', self.judge)

		# Standing判定なら
		if standEnable :
			self.walkctl.initializeModel(self.getFootPos(self.animectl))
			self.walkctl.setWaistPose(self.soBase, self.soWaist)
			self.walkctl.setControlEnable(True)
			self.animectl.enable(True)
			self.state = "Walking"
			#print('walc seni')

	def OnInit(self):
		self.animationState()

	def getFootPos(self, animectl):
	 	Lf = animectl.so_leftfoot.GetPose().getPos()
	 	Rf = animectl.so_rightfoot.GetPose().getPos()
	 	footpos = (Lf + Rf) * (1/2)
	 	return footpos

	def phaseStep(self):
		WC = self.walkctl
		footPos  = WC.getFootPos()
		DFootPos = footPos - self.lastFootPos
		# bodyの座標系(1,1,0)
		# y...正面, x...右
		OriX  = WC.getBodySolid().GetOrientation() * Vec3d(self.STEP_PHASE_X,0,0)
		OriY  = WC.getBodySolid().GetOrientation() * Vec3d(0,self.STEP_PHASE_Y,0)

		DFootPos2 = array([[DFootPos.x, DFootPos.y]])
		Ori       = array([[OriX.x, OriY.x], [OriX.y, OriY.y]])

		ans = dot(DFootPos2, linalg.inv(Ori))

		DphaseX = ans[[0][0]][0]
		DphaseY = ans[[0][0]][1]

		self.phaseX += DphaseX
		self.phaseY += DphaseY

		if self.phaseX > 1 :
			self.phaseX += -2
		elif self.phaseX < -1:
			self.phaseX += 2

		if self.phaseY > 1 :
			self.phaseY += -2
			self.hosu += 1
		elif self.phaseY <-1:
			self.phaseY += 2
			self.hosu += -1

		self.lastFootPos = footPos

	def getFootCenter(self):
		return self.walkctl.getFootPos()

	def getPhase(self):
		return [self.phaseX, self.phaseY]