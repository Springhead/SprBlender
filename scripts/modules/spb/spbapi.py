# -*- coding: utf-8 -*-

from   Spr          import *
from   collections  import defaultdict
from   spb.utils    import *


class spbapi_class():
	'''Springheadを便利に使うためのAPI．'''
	def __init__(self):
		self.removed_solids = []
		self.removed_joints = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:None)))

		# Human Interfaces
		self.space_navigator = None
		self.spidar          = None
		self.spidar1         = None
		self.falcon          = None

	def Init(self):
		self.__init__()
		return spbapi_cpp.Init()
	
	def GetFWSdk(self):
		return spbapi_cpp.GetFWSdk()

	def GetCRSdk(self):
		return spbapi_cpp.GetCRSdk()

	def GetHISdk(self):
		return spbapi_cpp.GetHISdk()

	def NInterfaces(self):
		return spbapi_cpp.NInterfaces()

	def GetInterface(self, i):
		return spbapi_cpp.GetInterface(i)

	def GetSPIDAR(self, id=0):
		if id==0:
			if self.spidar is None:
				self.spidar = spbapi_cpp.CreateSPIDAR()
			return self.spidar
		else:
			if self.spidar1 is None:
				self.spidar1 = spbapi_cpp.CreateSPIDAR()
			return self.spidar1

	def GetSpaceNavigator(self):
		if self.space_navigator is None:
			self.space_navigator = spbapi_cpp.CreateSpaceNavigator()
		return self.space_navigator

	def GetNovintFalcon(self):
		if self.falcon is None:
			self.falcon = spbapi_cpp.CreateNovintFalcon()
		return self.falcon

	def CreateHapticPointer(self):
		fwScene   = self.GetFWSdk().GetScene(0)
		phPointer = fwScene.GetPHScene().CreateHapticPointer()

		defaultPose = Posed()
		defaultPose.setPos( Vec3d(0,0,3) )
		defaultPose.setOri( Quaterniond.Rot(rad(90), "x") )
		phPointer.SetDefaultPose(defaultPose)
		phPointer.SetLocalRange(0.1)      # 局所シミュレーション範囲の設定
		phPointer.EnableFriction(False)   # 摩擦を有効にするかどうか
		
		fwPointer = fwScene.CreateHapticPointer()
		fwPointer.SetPHHapticPointer(phPointer)

		return fwPointer

	def GetHapticTimer(self):
		return spbapi_cpp.GetHapticTimer()

	def GetPhysicsTimer(self):
		return spbapi_cpp.GetPhysicsTimer()

	def OneStep(self):
		return spbapi_cpp.OneStep()

	def PrintScene(self):
		return spbapi_cpp.PrintScene()

	def GetCPS(self):
		return spbapi_cpp.GetCPS()

	def EnablePliant(self, enable):
		spbapi_cpp.EnablePliant(enable)

	def IsPliantEnabled(self):
		return spbapi_cpp.IsPliantEnabled()

	# --- --- --- --- ---

	def SaveSpr(self, filename):
		fiSdk   = FISdk().CreateSdk()
		fileSpr = fiSdk.CreateFileSpr()
		objs    = ObjectIfs()
		objs.Push(self.GetFWSdk().GetScene(0))
		objs.Push(self.GetCRSdk())
		fileSpr.Save(objs, filename)

	# --- --- --- --- ---

	def CreateSolid(self):
		if len(self.removed_solids)==0:
			debuglog.log("MINOR_EVENT", "New Solid.")
			return spbapi_cpp.GetFWSdk().GetScene(0).GetPHScene().CreateSolid(PHSolidDesc())
		else:
			debuglog.log("MINOR_EVENT", "Reused Solid.")
			return self.removed_solids.pop()

	def RemoveSolid(self, solid):
		# Shapeがあればはずしておく
		for i in range(0,solid.NShape()):
			solid.RemoveShape(0)
		# Solidをリサイクルボックスに送る
		solid.SetDynamical(False)
		solid.SetName("none")
		solid.SetFramePosition(Vec3d(-10**16,-10**16,-10**16)) # 1 lightyear
		solid.SetOrientation(Quaterniond(1,0,0,0))
		solid.SetVelocity(Vec3d(0,0,0))
		solid.SetAngularVelocity(Vec3d(0,0,0))
		self.removed_solids.append(solid)
		debuglog.log("MINOR_EVENT", "Removed", solid.GetName(), " : ", type(solid))

	def RemovePointer(self, fwPointer):
		# Shapeがあればはずしておく
		solid = fwPointer.GetPHHapticPointer()
		for i in range(0,solid.NShape()):
			solid.RemoveShape(0)
		# 無効にする （いまのところリサイクルはしない<!!>）
		solid.SetDynamical(False)
		solid.SetName("none")
		solid.SetFramePosition(Vec3d(-10**16,-10**16,-10**16)) # 1 lightyear
		solid.SetOrientation(Quaterniond(1,0,0,0))
		solid.SetVelocity(Vec3d(0,0,0))
		solid.SetAngularVelocity(Vec3d(0,0,0))
		debuglog.log("MINOR_EVENT", "Removed ", solid.GetName(), " : ", type(solid))

	# --- --- ---

	def CreateJoint(self, socketSolid, plugSolid, jotype):
		phScene = spbapi_cpp.GetFWSdk().GetScene(0).GetPHScene()
		debuglog.log("MINOR_EVENT", "Looking for Joint : ", [jotype, socketSolid, plugSolid])
		if self.removed_joints[jotype][socketSolid][plugSolid] is None:
			debuglog.log("MINOR_EVENT", "Not Found. New Joint. : ", jotype)
			if jotype == "Ball":
				joDesc = PHBallJointDesc()
				jo     = phScene.CreateJoint(socketSolid, plugSolid, PHBallJoint.GetIfInfoStatic(), joDesc)
				jo.CreateLimit(PHBallJointConeLimit.GetIfInfoStatic(), PHBallJointConeLimitDesc())
				return jo

			if jotype == "Hinge":
				joDesc = PHHingeJointDesc()
				jo     = phScene.CreateJoint(socketSolid, plugSolid, PHHingeJoint.GetIfInfoStatic(), joDesc)
				jo.CreateLimit(PH1DJointLimitDesc())
				return jo

			if jotype == "Slider":
				joDesc = PHSliderJointDesc()
				jo     = phScene.CreateJoint(socketSolid, plugSolid, PHSliderJoint.GetIfInfoStatic(), joDesc)
				jo.CreateLimit(PH1DJointLimitDesc())
				return jo

			if jotype == "Spring":
				joDesc = PHSpringDesc()
				return phScene.CreateJoint(socketSolid, plugSolid, PHSpring.GetIfInfoStatic(), joDesc)

		else:
			debuglog.log("MINOR_EVENT", "Found. Reused Joint. : ", [jotype, plugSolid.GetName(), socketSolid.GetName()])
			jo = self.removed_joints[jotype][socketSolid][plugSolid]
			self.removed_joints[jotype][socketSolid][plugSolid] = None
			jo.Enable(True)
			return jo

	def RemoveJoint(self, joint):
		if type(joint) is PHBallJoint:
			jotype = "Ball"
		if type(joint) is PHHingeJoint:
			jotype = "Hinge"
		if type(joint) is PHSliderJoint:
			jotype = "Slider"
		if type(joint) is PHSpring:
			jotype = "Spring"
		self.removed_joints[jotype][joint.GetSocketSolid()][joint.GetPlugSolid()] = joint
		joint.Enable(False)
		debuglog.log("MINOR_EVENT", "Removed ", joint.GetName(), " : ", [jotype, joint.GetSocketSolid(), joint.GetPlugSolid()])

spbapi = spbapi_class()
