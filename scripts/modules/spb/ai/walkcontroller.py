from Spr import *
from spb.utils  import *
from spb.abbrev import *
from math       import *

from numpy import *
import spb

# 20140628 ezoe
# まだできてない事
# ベース剛体と上体剛体を分けてリストに登録出来るようにし
# getCurrentFeedbackGain, addControlForceの中身を般化させる

class WalkController():
	def __init__(self, scene, nameList, soFloor, soBase, soWaist, touchsensor, config):
		self.config = config

		# Solids
		#self.soLow         = None		
		self.soUp          = None
		self.soFoot        = None
		self.jo_foot_joint = None
		self.lastVel   = Vec3d(0,0,0)
		
		self.nameList = nameList
		self.phScene = scene

		self.soFloor = soFloor
		self.soBase  = soBase
		self.soWaist = soWaist

		self.controlEnable = True
		self.state = "Walking"

		self.touchsensor = touchsensor

		'''Floorの摩擦を全部消す'''
		soFloor.GetShapes()[0].SetFrictionSpring(0)
		soFloor.GetShapes()[0].SetFrictionDamper(0)

		if scene.FindObject('soUp') == None :


			''' シミュレーション用の剛体を生成する '''
			# 振子 : soUp
			self.soUp = scene.CreateSolid()                                              # create
			self.soUp.SetName('soUp')                                                    # name
			self.soUp.SetMass(self.getSamOfNamedSolidMass(self.nameList))                # mass
			self.soUp.SetFramePosition(self.getCenterOfNamedSolidMass(self.nameList))    # center pos
			### for debug ###
			#self.soUp.SetMass(1)                                                        # mass
			#self.soUp.SetFramePosition(Vec3d(0,0,3))                                    # center pos
			self.soUp.SetCenterOfMass(Vec3d(0,0,0))                                      # center mass
			self.soUp.SetDynamical(True)
			soUpPos = self.soUp.GetPose().getPos()

			#　台車 : soFoot
			self.soFoot = scene.CreateSolid()
			self.soFoot.SetName('soFoot')
			self.soFoot.SetMass(20)
			'''ここで台車の位置を決めている（必要あれば変更）'''
			self.soFoot.SetFramePosition(Vec3d(soUpPos.x, soUpPos.y, 0.5))
			self.soFoot.SetCenterOfMass(Vec3d(0,0,0))
			self.soFoot.SetDynamical(True)
			# 台車の（シェイプ）
			descBox = CDBoxDesc()
			descBox.boxsize = Vec3f(1,1,1)
			cdBox = self.phScene.GetSdk().CreateShape(CDBox.GetIfInfoStatic(), descBox)
			cdBox.SetStaticFriction(0)
			cdBox.SetDynamicFriction(0)
			cdBox.SetFrictionSpring(0)
			cdBox.SetFrictionDamper(0)
			self.soFoot.AddShape(cdBox)
			# コリジョン
			self.phScene.SetContactMode(self.soFoot, 0)
			self.phScene.SetContactMode(self.soFoot, soFloor, 2)

			#ジョイントで二剛体をつなげる
			descJoint = PHBallJointDesc()
			descJoint.spring = 0
			descJoint.damper = 0
			descJoint.poseSocket = Posed(Vec3d(0,0,-0.5), Quaterniond())
			descJoint.posePlug   = Posed(Vec3d(0,0,-(self.soUp.GetPose().getPos().z)), Quaterniond())
			# descJoint.poseSocket.setPos(Vec3d(0,0,-0.5))
			# descJoint.posePlug.setPos(Vec3d(0,0,-(self.soUp.GetPose().getPos().z)))
			self.ballJoint = self.phScene.CreateJoint(self.soFoot, self.soUp, PHBallJoint.GetIfInfoStatic(), descJoint)
			
			print('Create simulation solid.')

		else :
			self.soUp   = scene.FindObject('soUp')
			self.soFoot = scene.FindObject('soFoot')
			print('Simulation solids have already created.')


		# Initialize
		## Feedback control
		self.lastAnglex  = 0
		self.lastAngley  = 0
		self.lastPos     = self.soUp.GetCenterPosition()
		self.pole        = [0,0,0,0]
		## Torque PD control
		self.front       = Vec3d(0,-1,0)
		self.lastAngleF  = Vec3d()
		self.lastAngvel  = Vec3d()
		self.DFriction   = self.config['walk_d_friction']
		self.Kp          = self.config['walk_rotation_Kp']
		self.Kd          = self.config['walk_rotation_Kd']

		# パラメータ
		## 極配置
		self.setPole(*(self.config['walk_pole']))
		#self.setPole(-1.5,-2.5,-1,-3.2)
		#self.setPole(-1.9,-1.2,-1.3,-2)

		#限界条件
		## 限界角度
		self.maxRadx   = self.config['walk_max_angle_x']
		self.maxRady   = self.config['walk_max_angle_y']
		## 限界速度
		self.Maxvel    = self.config['walk_max_velocity']
		## 限界回転速度
		self.maxAngVel = self.config['walk_max_angvel']

		# フィードバックゲインを求める
		self.Kx = 0
		self.Ky = 0
		self.getCurrentFeedbackGain()

		# 以下デバッグ
		self.setWaistPose(self.soBase, self.soWaist)

		# <!!>
		self.forces = []


# --- --- --- --- ---

	# step function
	def step(self, scene, target):
		self.calcControlEnable()
		cCE = self.getControlEnable()
		# 姿勢制御が可能でかつ歩行中の時のみ制御を行う
		# print(self.state, cCE)
		if cCE and self.state == "Walking" :
			self.soUp.SetDynamical(True)
			self.soFoot.SetDynamical(True)
			self.soFoot.GetShape(0).SetStaticFriction(0)
			self.soFoot.GetShape(0).SetDynamicFriction(0)
			self.addControlForce(scene, target)
			self.setWaistPose(self.soBase, self.soWaist)
			self.addControlTorque(scene, self.soUp, target[4])
			self.state = "Walking"
		elif self.state == "Standing":
			self.state = "Standing"
			self.soUp.SetDynamical(False)
			self.soFoot.SetDynamical(False)
			self.soFoot.GetShape(0).SetStaticFriction(100)
			self.soFoot.GetShape(0).SetDynamicFriction(100)
		else :
			self.state = "Falling"
			self.soUp.SetDynamical(False)
			self.soFoot.SetDynamical(False)
			self.soFoot.GetShape(0).SetStaticFriction(100)
			self.soFoot.GetShape(0).SetDynamicFriction(100)
		#del self.solidList[:] #更新のため、毎ステップリストを空に
		#self.getCreatureSolids(scene)
		self.addAppliedForce()
		self.addControlForce(scene, target)
		self.setWaistPose(self.soBase, self.soWaist)
		self.addControlTorque(scene, self.soUp, target[4])

		#debug
		#self.state = "Standing"

	def initializeModel(self, fp):
		self.soFoot.SetPose(Posed(Vec3d(fp.x, fp.y, 0.5), Quaterniond()))
		self.soUp.SetPose(Posed(Vec3d(fp.x, fp.y, self.relCoM.z), self.soWaist.GetPose().getOri()))

		zero = Vec3d(0,0,0)
		self.soFoot.SetAngularVelocity(zero)
		self.soFoot.SetVelocity(zero)
		self.soUp.SetAngularVelocity(zero)
		self.soUp.SetVelocity(zero)

		# self.state = "Standing"
		self.state = "Walking"

	def setState(self, name):
		self.state = name

	def setWaistPose(self, soBase, soWaist):
		UpPos = self.getBodyPose().getPos()
		UpOri = self.getBodyPose().getOri()
		#シーン内のキャラクタ剛体の重心
		CoM   = self.getCenterOfNamedSolidMass(self.nameList)
		#シーン内のCoMへの腰剛体からの相対位置ベクトル
		relSoM = CoM - soWaist.GetPose().getPos()
		pos = UpPos - relSoM

		soBase.SetPose(Posed(pos, UpOri))
		# soBase.SetFramePosition(pos)


	def draw(self):
		bgl.glBegin(bgl.GL_LINES)
		while len(self.forces) > 0:
			bgl.glColor4f(1.0, 0.2, 0.2, 1.0)
			force, pos =  self.forces.pop()
			f = pos + (force * 1.0)
			bgl.glVertex3f(pos.x, pos.y, pos.z)
			bgl.glVertex3f(f.x,   f.y,   f.z  )
		bgl.glEnd()


	def addAppliedForce(self):
		# （注意）touchsensorのUpdateはここでは呼ばないので必ず他で呼ぶこと
		force_total = Vec3d()
		for i in range(self.touchsensor.NContacts()):
			con = self.touchsensor.GetContact(i)
			if con.soMe.GetName()[3:] in self.nameList and (not "Apple" in con.soOther.GetName()):
				force = con.force * self.config['walk_force_apply_scale']
				force_total += force
				if force_total.norm() < self.config['walk_force_apply_max']:
					self.soUp.AddForce(force, con.pos)
					self.forces.insert(0, (con.force, con.pos))


	def addControlTorque(self, scene, solid, target):
		Kp         = self.Kp
		Kd         = self.Kd
		DF         = self.DFriction
		lastAng    = self.lastAngleF
		lastAngvel = self.lastAngvel

		#正面方向ベクトルを求める
		relFront  = (solid.GetPose().transform(self.front) - solid.GetPose().getPos())
		#relFront  = solid.GetPose().transform(self.front).unit()
		#target方向ベクトルを求める
		#relTarget = target - solid.GetPose().getPos()
		relTarget = target

		#回転を求める
		#ang    = atan2(relTarget.y, relTarget.x) - atan2(relFront.y, relFront.x)
		tarvec = Vec3d(target.x,   target.y,   0).unit()
		frovec = Vec3d(relFront.x, relFront.y, 0).unit()
		#print('frovec', frovec)
		ang    = tarvec.CrossL(frovec)
		ang_diff_max = self.config['walk_dir_ang_diff_max']
		if (ang.norm() > ang_diff_max):
			ang = ang.unit() * ang_diff_max

		dtInv   = (1/ scene.GetTimeStep())
		angdiff = (ang - lastAng)
		angvel  = angdiff * dtInv


		#torqueを計算
		torque = (ang*(-Kp))  # + (angvel*(-Kd)) # - DF * angvel

		#torqueをsolidのposeで変換
		torque2 = solid.GetOrientation() * torque

		#addTorque
		solid.AddTorque(torque2)

		# print('ang')
		# print(ang * (180/3.14))
		# print(angvel)
		# print(torque)

		
		# -- Add Damper -- <!!>
		av = solid.GetAngularVelocity()
		solid.AddTorque(Vec3d(0,0,av.z) * (-Kd))


		self.lastAngleF = ang
		self.lastAngvel = angvel

	# add force for inverted pendulum control
	def addControlForce(self, scene, target):
		'''状態ベクトルを求める'''
		pos    = self.soUp.GetCenterPosition()
		relpos = pos - self.soFoot.GetPose().transform(Vec3d(0,0,-(self.soFoot.GetPose().getPos().z)))
		# #relpos = pos - self.soFoot.GetPose().transform(Vec3d(0,0,-0.125))
		# print('relpos.z = ',relpos.z)
		# print('from FL  = ',(pos.z - (self.soFloor.GetPose().getPos().z + (self.soFloor.GetShapes()[0].GetBoxSize().z /2))))
		vel    = (pos - self.lastPos) * (1/ scene.GetTimeStep())
		anglex = atan2(relpos.x, relpos.z)
		angley = atan2(relpos.y, relpos.z)
		angvelx = (anglex - self.lastAnglex) * (1/ scene.GetTimeStep())
		angvely = (angley - self.lastAngley) * (1/ scene.GetTimeStep())
		X      = array([[pos.x], [anglex], [vel.x], [angvelx]])
		Y      = array([[pos.y], [angley], [vel.y], [angvely]])
		tarX   = array([[target[0].x], [target[1].x], [target[2].x], [target[3].x]])
		tarY   = array([[target[0].y], [target[1].y], [target[2].y], [target[3].y]])

		Fx = -dot(self.Kx, (X - tarX))
		Fy = -dot(self.Ky, (Y - tarY))

		self.soFoot.AddForce(Vec3d(Fx[0][0].real, Fy[0][0].real, 0))

		self.lastPos   = pos
		self.lastAnglex = anglex
		self.lastAngley = angley

	# 現在のFeedback gain を求める
	def getCurrentFeedbackGain(self):
		M       = self.soFoot.GetMass()
		m       = self.soUp.GetMass()
		#relCoM  = (self.soUp.GetCenterPosition() + self.soUp.GetCenterOfMass()) - (self.soFoot.GetCenterPosition())
		self.relCoM  = (self.soUp.GetCenterPosition() - self.soFoot.GetPose().transform(Vec3d(0,0,-(self.soFoot.GetPose().getPos().z))))
		relCoM = self.relCoM
		lx      = sqrt((relCoM.x)*(relCoM.x) + (relCoM.z)*(relCoM.z))
		ly      = sqrt((relCoM.y)*(relCoM.y) + (relCoM.z)*(relCoM.z))

		self.Kx = self.getFeedbackGain(M, m, lx, self.pole)
		self.Ky = self.getFeedbackGain(M, m, ly, self.pole)

	# Feedback gain を求める
	def getFeedbackGain(self, M, m, l, pole):
		print(M,m,l,pole)
		# M 台車の質量
		# m 振子の質量
		# l 質点までの距離
		# pole 目標の極が入ったリスト

		# 慣性モーメント
		J = (m*l*l)/3
		g = 9.8

		Ay  = array([[M+m, m*l],
					 [m*l, J+m*l*l]])
		IAy = linalg.inv(Ay)
		By  = array([[0,0],[0,m*g*l]])
		Cu  = array([[1],[0]]) 
		X21 = dot(IAy, By)
		a = X21[0][0]
		b = X21[0][1]
		c = X21[1][0]
		d = X21[1][1]
		U2  = dot(IAy, Cu)

		# 状態空間モデル
		A   = array([[0.0,0.0,1.0,0.0],
			 	     [0.0,0.0,0.0,1.0],
					 [a,b,0.0,0.0],
					 [c,d,0.0,0.0]])
		B   = array([[0.0],
					 [0.0],
					 [U2[0][0]],
					 [U2[1][0]]])
		C   = array([[1.0,0.0,0.0,0.0],
					 [0.0,1.0,0.0,0.0]])

		# 極配置
		# 制御対象の特性多項式の係数行列
		pA = array([[0.0,-d,0.0,0.0]])

		# 極から求められる特性多項式の係数行列
		p1 = pole[0]
		p2 = pole[1]
		p3 = pole[2]
		p4 = pole[3]

		pP = array([[-p1-p2-p3-p4,
					p1*p2 + p1*p3 + p1*p4 + p2*p3 + p2*p4 + p3*p4,
					-p1*p2*p3 -p1*p2*p4 -p1*p3*p4 - p2*p3*p4,
					p1*p2*p3*p4]])

		# 可制御正準系のフィードバック係数ベクトル
		K2 = pP - pA

		# 可制御性行列
		Uc  = c_[B, dot(A,B), dot(A,dot(A,B)), dot(A, dot(A, dot(A,B)))]
		IUc = linalg.inv(Uc)
		# 最後の行
		e4 = IUc[3]

		# 変換行列T
		invT = r_[[e4],
				 [dot(e4,A)],
				 [dot(e4,dot(A,A))],
				 [dot(e4,dot(A,dot(A,A)))]]

		#フィードバック係数
		K = dot(K2,invT)

		return K

	# get world center position of solids mass in list
	def getCenterOfMass(self, solidList):
		
		SamOfMass = 0
		SamOfMassPos = Vec3d(0,0,0)
		
		for solid in solidList:
			# SCP = solid.GetCenterPosition()
			# SCoM = SCP + solid.GetCenterOfMass()
			SolidCoM   = solid.GetPose().transform(solid.GetCenterOfMass())
			SolidMass  = solid.GetMass()
			# SoMPos = SoMPos + Vec3d(SCoM.x, SCoM.y, SCoM.z)*SMass
			SamOfMassPos += SolidCoM * SolidMass
			SamOfMass    += SolidMass

		CoM = SamOfMassPos * (1/SamOfMass)
		
		return CoM


	def getCenterOfNamedSolidMass(self, nameList):
		
		SamOfMass = 0
		SamOfMassPos = Vec3d(0,0,0)
		
		for solid in nameList:
			so = So[solid].spr()
			# SCP = solid.GetCenterPosition()
			# SCoM = SCP + solid.GetCenterOfMass()
			#SolidCoM   = so.GetPose().transform(so.GetCenterOfMass())
			SolidCoM   = so.GetCenterPosition()
			SolidMass  = so.GetMass()
			# SoMPos = SoMPos + Vec3d(SCoM.x, SCoM.y, SCoM.z)*SMass
			SamOfMassPos += SolidCoM * SolidMass
			SamOfMass    += SolidMass

		CoM = SamOfMassPos * (1/SamOfMass)
		
		return CoM

	def getSamOfMass(self):

		SAM = 0
		for solid in self.solidList:
			SAM = SAM + solid.GetMass()

		return SAM

	def getSamOfNamedSolidMass(self, nameList):
		SAM = 0
		for solid in nameList:
			SAM = SAM + So[solid].spr().GetMass()
		return SAM
	
	# get solids which creature has
	def getCreatureSolids(self, scene):
		sceneList = []
		nameList  = []
		
		# sceneに存在する全てのsolidを取ってくる
		for solid in scene.GetSolids():
			sceneList.append(solid)
		
		# 取得したい（キャラクターを構成している）solidの名前を入れたリスト
		nameList = ['so_Upper',
		            'so_Lower',
		            'so_Foot']
		
		# nameListに含まれるsolidだけをsolidListに格納
		for name in nameList:
			for sceneSolid in sceneList:
				if name == sceneSolid.GetName():
					self.solidList.append(sceneSolid)
		
		# solid情報を更新
		self.soUp    = self.solidList[0]
		self.soLow   = self.solidList[1]
		self.soFoot  = self.solidList[2]

	def getFootPos(self):
		fp = self.soFoot.GetPose().getPos()
		fp.z = 0
		return fp

	def getBodySolid(self):
		return self.soUp

	def getBodyPose(self):
		return self.soUp.GetPose()

	# front vector setter
	def setFront(self, vector):
		self.front = vector

	def setPole(self, p1, p2, p3, p4):
		self.pole = [p1,p2,p3,p4]

	def setControlEnable(self, bool):
		self.controlEnable = bool

	def getControlEnable(self):
		return self.controlEnable

	# def getHightFromFloor(self):
	# 	'''床面からの重心の高さを返す（平地限定）'''
	# 	pos    = self.soUp.GetCenterPosition()
	# 	relpos = pos - self.soFoot.GetPose().transform(Vec3d(0,0,-(self.soFoot.GetPose().getPos().z)))
	# 	#relpos = pos - self.soFoot.GetPose().transform(Vec3d(0,0,-0.125))
	# 	print('relpos.z = ',relpos.z)
	# 	print('from FL  = ',(relpos.z - (self.soFloor.GetPose().getPos().z + (self.soFloor.GetShapes()[0].GetBoxSize().z /2))))

	def calcControlEnable(self):
		#bpy.data.objects['Debug'].location            = to_bpy(self.soUp.GetPose().getPos())
		#bpy.data.objects['Debug'].rotation_quaternion = to_bpy(self.soUp.GetPose().getOri())

		pos    = self.soUp.GetPose().getPos()
		footpos = self.soFoot.GetPose().transform(Vec3d(0,0,-(self.soFoot.GetPose().getPos().z)))
		relpos = pos - footpos
		anglex = atan2(relpos.x, relpos.z)
		angley = atan2(relpos.y, relpos.z)
		# print("anglex", round((anglex*180/pi),3))
		# print("angley", round((angley*180/pi),3))

		if (fabs(anglex) > self.maxRadx) or (fabs(angley) > self.maxRady) :
			# print("Disable Walk Control : ", pos, footpos, relpos, anglex, self.maxRadx, angley, self.maxRady)
			self.setControlEnable(False)

	def getState(self):
		return self.state

	def setMaxRad(self, X, Y):
		self.maxRadx = rad(X)
		self.maxRady = rad(Y)