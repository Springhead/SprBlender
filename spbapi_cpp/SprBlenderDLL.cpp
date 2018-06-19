// #include "Physics/PHHapticEngineMultiBase.h"
#include "Physics/PHConstraintEngine.h"

#include <iomanip>
#include <sstream>

#include <Framework/SprFWApp.h>
#include <Framework/FWGLUT.h>

#include "SprBlenderDLL.h"

#ifdef TOBII
//EyeX
#include <math.h>
#endif

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

// シングルトン
SprBlenderDLL* SprBlenderDLL::instance = NULL;

// フックする前の本来のWndProc
WNDPROC WndProcOrig = NULL;

// --- --- --- --- ---

// シングルトン取得
SprBlenderDLL* SprBlenderDLL::GetInstance() {
	if (!instance) { instance = new SprBlenderDLL(); }
	return instance;
}

// タイマコールバック
void SprBlenderDLL::TimerCallback(int id, void* arg) {
	GetInstance()->TimerFunc(id);
}

void SprBlenderDLL::ThreadCallback(int id, void* arg) {
	GetInstance()->ThreadFunc(id);
}

#ifdef USE_KINECT
void SprBlenderDLL::KinectCallback(int id, void* arg) {
	GetInstance()->KinectFunc(id);
}
#endif


// Stepコールバック
void SprBlenderDLL::CallbackBeforeStep(void* arg) {
	GetInstance()->BeforeStep();
}

void SprBlenderDLL::CallbackAfterStep(void* arg) {
	GetInstance()->AfterStep();
}

// WndProcフック
LRESULT CALLBACK WndProcHook(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
	MSG m;
	m.hwnd		= hWnd;
	m.message	= msg;
	m.wParam	= wParam;
	m.lParam	= lParam;
	SprBlenderDLL* spb = SprBlenderDLL::GetInstance();

	// SpaceNavigatorが作成されていればメッセージを渡す
	for (int i=0; i<spb->NInterfaces(); ++i) {
		HISpaceNavigatorIf* spcnav = spb->GetInterface(i)->Cast();
		if (spcnav && spcnav->PreviewMessage(&m)) { return 0L; }
	}

	// SpaceNavigatorがメッセージを受け取らなかった場合は本来のWndProcに渡す
	return CallWindowProc(WndProcOrig, hWnd, msg, wParam, lParam);
}

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

// コンストラクタ
SprBlenderDLL::SprBlenderDLL() {
	bEnable       = true;
	bPliant       = false;
	bPliantBefore = false;
	bInitialized  = false;
	callbackCreatureRuleStep = NULL;

	// --- --- --- --- ---
	// Create HISdk (何度も作らない)
	hiSdk = HISdkIf::CreateSdk();

	// --- --- --- --- ---
	// Add Real Devices
	DRUsb20SimpleDesc usbSimpleDesc;
	hiSdk->AddRealDevice(DRUsb20SimpleIf::GetIfInfoStatic(), &usbSimpleDesc);

	DRUsb20Sh4Desc usb20Sh4Desc;
	for (int i=0; i<10; ++i) {
		usb20Sh4Desc.channel = i;
		hiSdk->AddRealDevice(DRUsb20Sh4If::GetIfInfoStatic(), &usb20Sh4Desc);
	}

	DRCyUsb20Sh4Desc cyDesc;
	for(int i=0; i<10; ++i){
		cyDesc.channel = i;
		hiSdk->AddRealDevice(DRCyUsb20Sh4If::GetIfInfoStatic(), &cyDesc);
	}

	hiSdk->AddRealDevice(DRKeyMouseWin32If::GetIfInfoStatic());

	// --- --- --- --- ---
	// Hook WndProc
	/*
	hWnd = GetActiveWindow();
	WndProcOrig = (WNDPROC)(GetWindowLongPtr(hWnd, GWLP_WNDPROC));
	SetWindowLongPtr(hWnd, GWLP_WNDPROC, (LONG_PTR)(WndProcHook));
	*/

	// --- --- --- --- ---
	// Create Timers
	
	// 物理ステップ用のタイマを作成
	timerPhysics = UTTimerIf::Create();
	timerPhysics->SetMode(UTTimerIf::THREAD);
	timerPhysics->SetCallback(SprBlenderDLL::ThreadCallback, this);
	timerPhysics->SetResolution(1);
	timerPhysics->SetInterval(1); // <!!> なぜか20に変えてあったがそれでは遅いだろう
	timerPhysics->Stop();
	timerPhysicsID = timerPhysics->GetID();

	// 力覚スレッド用のマルチメディアタイマを作成
	timerHaptic = UTTimerIf::Create();
	timerHaptic->SetMode(UTTimerIf::MULTIMEDIA);
	timerHaptic->SetCallback(SprBlenderDLL::TimerCallback, this);
	timerHaptic->SetResolution(1);
	timerHaptic->SetInterval(1);
	timerHaptic->Stop();
	timerHapticID = timerHaptic->GetID();

	#ifdef USE_KINECT
	// kinect用のスレッドを作成
	timerkinect = UTTimerIf::Create();
	timerkinect->SetMode(UTTimerIf::THREAD);
	timerkinect->SetCallback(SprBlenderDLL::KinectCallback, this);
	timerkinect->SetResolution(1);
	timerkinect->SetInterval(1);
	timerkinect->Stop();
	timerkinectID = timerkinect->GetID();
	#endif

	// --- --- --- --- ---
	// Prepare States
	statesMainSimulation = ObjectStatesIf::Create();
	statesTestSimulation = ObjectStatesIf::Create();

	// --- --- --- --- ---
	// Leap
	fwLeap = NULL;

	// --- --- --- --- ---
	// Kinect
	#ifdef USE_KINECT
	bKinectInitialized = false;
	#endif
}

// 初期化
void SprBlenderDLL::Init() {
	bInitialized = false;

	// Create SDKs (HISdkを除く)
	fwSdk = FWSdkIf::CreateSdk();
	crSdk = CRSdkIf::CreateSdk();

	// Create Scenes
	FWSceneIf* fwScene = fwSdk->CreateScene(PHSceneDesc(), GRSceneDesc());

	// Initialize PHScene
	PHSceneIf* phScene = fwScene->GetPHScene();
	phScene->SetHapticTimeStep((double)timerHaptic->GetInterval() / 1000.0);
	//phScene->GetHapticEngine()->EnableHapticEngine(true);
	//phScene->GetHapticEngine()->SetHapticEngineMode(PHHapticEngineDesc::MULTI_THREAD);
	//phScene->GetHapticEngine()->SetCallbackBeforeStep(SprBlenderDLL::CallbackBeforeStep, this);
	//phScene->GetHapticEngine()->SetCallbackAfterStep(SprBlenderDLL::CallbackAfterStep, this);

	phScene->GetConstraintEngine()->SetBSaveConstraints(true);
	
	bInitialized  = true;
	bResetTestSim = true;

	// Create Render
	/* // <!!>
	grRender = fwSdk->GetGRSdk()->CreateRender();
	GRDeviceIf* grDevice = fwSdk->GetGRSdk()->CreateDeviceGL();
	grRender->SetDevice(grDevice);
	grRender->GetDevice()->Init();
	*/
}

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

// SPIDARの作成
HISpidarGIf* SprBlenderDLL::CreateSPIDAR() {
	HISpidarGIf* spidar=NULL;

	spidar = hiSdk->CreateHumanInterface(HISpidarGIf::GetIfInfoStatic())->Cast();
	spidar->Init(&HISpidarGDesc("SpidarG6X3R"));
	spidar->Calibration();

	interfaces.push_back(spidar);

	return spidar;
}

// SpaceNavigatorの作成
HISpaceNavigatorIf* SprBlenderDLL::CreateSpaceNavigator() {
	HISpaceNavigatorDesc descSpcNav;
	descSpcNav.hWnd = &hWnd;

	HISpaceNavigatorIf* spcNav;
	spcNav = hiSdk->CreateHumanInterface(HISpaceNavigatorIf::GetIfInfoStatic())->Cast();
	spcNav->Init(&descSpcNav);
	spcNav->SetPose(Posef(Vec3f(0,0,0), Quaternionf()));

	interfaces.push_back(spcNav);

	return spcNav;
}

// Novint Falconの作成
HINovintFalconIf* SprBlenderDLL::CreateNovintFalcon() {
	HINovintFalconIf* falcon;
	falcon = hiSdk->CreateHumanInterface(HINovintFalconIf::GetIfInfoStatic())->Cast();
	falcon->Init(NULL);
	falcon->Calibration();

	interfaces.push_back(falcon);

	return falcon;
}

// Leapmotionの作成
FWSkeletonSensorIf* SprBlenderDLL::CreateLeap() {
	// 一度しか作成しない
	if (fwLeap) { return fwLeap; }

	HILeapDesc descLeap;

	HILeapIf* leap;
	leap = hiSdk->CreateHumanInterface(HILeapIf::GetIfInfoStatic())->Cast();
	leap->Init(&descLeap);
	leap->SetScale(1/30.0);
	leap->SetCenter(Vec3d(0,0,-5));
	leap->SetRotation(Quaterniond::Rot(Rad(90),'x'));

	interfaces.push_back(leap);

	FWSkeletonSensorDesc descSS;
	fwLeap = GetFWSdk()->GetScene(0)->CreateSkeletonSensor(descSS);
	fwLeap->AddChildObject(leap);
	fwLeap->SetRadius(Vec2d(0.4, 0.4));

	return fwLeap;
}

// Leapmotionの作成
FWSkeletonSensorIf* SprBlenderDLL::CreateLeapUDP() {
	// 一度しか作成しない
	if (fwLeap) { return fwLeap; }

	HILeapUDPDesc descLeap;

	HILeapUDPIf* leap;
	leap = hiSdk->CreateHumanInterface(HILeapUDPIf::GetIfInfoStatic())->Cast();
	leap->Init(&descLeap);
	const float SCALE = 43.0f;
	leap->SetScale(1.0f/SCALE);
	leap->SetCenter(Vec3d((- 625-20+30+30-10) / SCALE, (- 380 - 90 -50  ) / SCALE, (-240 -90 +100+30+20) / SCALE));
	leap->SetRotation(Quaterniond::Rot(Rad(90),'x'));

	interfaces.push_back(leap);

	FWSkeletonSensorDesc descSS;
	fwLeap = GetFWSdk()->GetScene(0)->CreateSkeletonSensor(descSS);
	fwLeap->AddChildObject(leap);
	fwLeap->SetRadius(Vec2d(0.4, 0.4));

	return fwLeap;
}

FWHapticPointerIf* SprBlenderDLL::CreateHapticPointer(FWSceneIf* fwScene, HIBaseIf* hi) {
	// 力覚ポインタの作成
	PHHapticPointerIf* phPointer = fwScene->GetPHScene()->CreateHapticPointer();

	Posed defaultPose;
	defaultPose.Pos() = Vec3d(0,0,3);
	defaultPose.Ori() = Quaterniond::Rot(Rad(90), 'x');
	phPointer->SetDefaultPose(defaultPose);	// 力覚ポインタ初期姿勢の設定

	phPointer->SetLocalRange(0.1f);			// 局所シミュレーション範囲の設定
	phPointer->SetPosScale(100);			// 力覚ポインタの移動スケールの設定
	phPointer->SetReflexSpring(5000.0f);	// バネ係数の設定
	phPointer->SetReflexDamper(0.0f);		// ダンパ係数の設定
	phPointer->EnableFriction(false);		// 摩擦を有効にするかどうか
	phPointer->EnableForce(true);			// 力を有効にするかどうか

	// HumanInterfaceと接続するためのオブジェクトを作成
	FWHapticPointerIf* fwPointer = fwScene->CreateHapticPointer();

	fwPointer->SetHumanInterface(hi);		// HumanInterfaceの設定
	fwPointer->SetPHHapticPointer(phPointer); // PHHapticPointerIfの設定

	return fwPointer;
}

// --- --- --- --- ---

// タイマコールバック
void SprBlenderDLL::TimerFunc(int id) {
	// <!!>
	/*
	if (!bInitialized || !bEnable) { return; }

	if (id==timerHapticID) {
		for (int i=0; i<fwSdk->NScene(); ++i) {
			fwSdk->GetScene(i)->UpdateHapticPointers();
			fwSdk->GetScene(i)->GetPHScene()->StepHapticLoop();
		}
	}
	*/
}

void SprBlenderDLL::ThreadFunc(int id) {
	if (!bInitialized || !bEnable) { return; }

	// 複数のシーンを同時に走らせることは想定しない．
	// <!!> fwSdk->GetScene(0)->GetPHScene()->GetHapticEngine()->StepPhysicsSimulation();

	// <!!> Haptic Engineを使わないようにしてみる 2014年夏SIGGRAPH用
	BeforeStep();
	{
		UTAutoLock LOCK(EPCriticalSection);
		fwSdk->GetScene(0)->GetPHScene()->Step();
	}
	AfterStep();
}

#ifdef USE_KINECT
void SprBlenderDLL::KinectFunc(int id) {
	if (!bInitialized || !bEnable) { return; }

	IBodyFrame* pBodyFrame = nullptr;
	HRESULT hResult;
	hResult = pBodyReader->AcquireLatestFrame(&pBodyFrame);
	if (SUCCEEDED(hResult)){
		IBody* pBody[BODY_COUNT] = { 0 };
		hResult = pBodyFrame->GetAndRefreshBodyData(BODY_COUNT, pBody);
		if (SUCCEEDED(hResult)){
			for (int count = 0; count < BODY_COUNT; count++){
				BOOLEAN bTracked = false;
				hResult = pBody[count]->get_IsTracked(&bTracked);
				if (SUCCEEDED(hResult) && bTracked){
					UINT64 trackingID;
					std::cout << trackingID << "  ";
					pBody[count]->get_TrackingId(&trackingID);
					Joint joint[JointType::JointType_Count];
					hResult = pBody[count]->GetJoints(JointType::JointType_Count, joint);
					if (SUCCEEDED(hResult)){
						CameraSpacePoint pos_ = joint[JointType_HandLeft].Position;
						Vec3d pos = Vec3d(pos_.X, pos_.Y, pos_.Z);

					}
				}
			}
			std::cout << std::endl;
		}
		for (int count = 0; count < BODY_COUNT; count++){
			SafeRelease(pBody[count]);
		}
	}
	SafeRelease(pBodyFrame);
}

bool SprBlenderDLL::CreateKinect() {
	if (bKinectInitialized) { return true; }

	//kinectに割り当てる剛体を生成
	PHSceneIf* phScene = fwSdk->GetScene(0)->GetPHScene();
	string partname[] = {
		"Head",
		"Spine",
		"RightElbow",
		"LeftElbow",
		"RightWrist",
		"LeftWrist",
		"RightHand",
		"LeftHand",
	};
	for(int i = 0; i < 6; i++){
		for(int j = 0; j < 8; j++){
			KinectBone[i][j] = phScene->CreateSolid();
			std::ostringstream oss;
			oss << "soKinectHuman" << i << "_" << partname[j];
			KinectBone[i][j]->SetName(oss.str().c_str());
			KinectBone[i][j]->SetDynamical(false);
		}
	}

	// Sensor
	HRESULT hResult = S_OK;
	hResult = GetDefaultKinectSensor(&pSensor);
	if (FAILED(hResult)){
		std::cerr << "Error : GetDefaultKinectSensor" << std::endl;
		return -1;
	}

	hResult = pSensor->Open();
	if (FAILED(hResult)){
		std::cerr << "Error : IKinectSensor::Open()" << std::endl;
		return -1;
	}

	// Source
	hResult = pSensor->get_BodyFrameSource(&pBodySource);
	if (FAILED(hResult)){
		std::cerr << "Error : IKinectSensor::get_BodyFrameSource()" << std::endl;
		return -1;
	}

	// Reader
	hResult = pBodySource->OpenReader(&pBodyReader);
	if (FAILED(hResult)){
		std::cerr << "Error : IBodyFrameSource::OpenReader()" << std::endl;
		return -1;
	}

	/*
	SafeRelease(pBodySource);
	SafeRelease(pBodyReader);
	if (pSensor){
		pSensor->Close();
	}
	SafeRelease(pSensor);
	*/

	bKinectInitialized = true;
	return true;
}
#endif

void SprBlenderDLL::BeforeStep() {
	PHSceneIf* phScene = GetFWSdk()->GetScene(0)->GetPHScene();

	// EPロック獲得
	// EPCriticalSection.Enter(); // <!!> 2014/08/10

	if (!bEnable) { return; }

	// FW Skeleton Sensor Step
	GetFWSdk()->GetScene(0)->UpdateSkeletonSensors();

	// Pliant Motion
	if (bPliant) {
		StepPliantBefore();
		bPliantBefore = true;
	} else {
		bPliantBefore = false;
	}
}

void SprBlenderDLL::AfterStep() {
	PHSceneIf* phScene = GetFWSdk()->GetScene(0)->GetPHScene();

	if (!bEnable) {
		// EPCriticalSection.Leave(); // <!!> 2014/08/10
		return;
	}

	// Pliant Motion
	if (bPliantBefore) {
		StepPliantAfter();
	}

	// Creature Step
	crSdk->Step();

	// EPロック解除
	// EPCriticalSection.Leave(); // <!!> 2014/08/10

	// Count "Cycle Per Second"
	{
		static int cycle = 0;
		static DWORD lastCounted = timeGetTime();
		DWORD now = timeGetTime();
		if (now - lastCounted > 1000) {
			cps = (float)(cycle) / (float)(now - lastCounted) * 1000.0f;
			lastCounted = now;
			cycle = 0;
		}
		cycle++;
	}
}


void SprBlenderDLL::StepPliantBefore() {
	PHSceneIf* phScene = GetFWSdk()->GetScene(0)->GetPHScene();
	jointdescs.resize(phScene->NJoints());
	soliddescs.resize(phScene->NSolids());
	ikaStates.resize(phScene->NIKActuators());
	ikeStates.resize(phScene->NIKEndEffectors());

	// テストシミュレーション前の状態を保存
	statesMainSimulation->SaveState(phScene);

	// 接触対象剛体の位置を保存
	for (int i=0; i<phScene->NSolids(); ++i) {
		if (soliddescs[i].desc.mass > 0) {
			soliddescs[i].desc.pose        = phScene->GetSolids()[i]->GetPose();
			soliddescs[i].desc.velocity    = phScene->GetSolids()[i]->GetVelocity();
			soliddescs[i].desc.angVelocity = phScene->GetSolids()[i]->GetAngularVelocity();
		}
	}

	// 接触モードを退避
	contacts.resize(phScene->NSolids() * phScene->NSolids());
	{
		int n=0;
		for (int i=0; i<phScene->NSolids(); ++i) {
			for (int j=i+1; j<phScene->NSolids(); ++j) {
				PHSolidIf* so1 = phScene->GetSolids()[i];
				PHSolidIf* so2 = phScene->GetSolids()[j];			
				bool swap;
				contacts[n] = phScene->GetSolidPair(so1, so2, swap)->IsContactEnabled();
				n++;
			}
		}
	}


	// 前回のテストシミュレーション後の状態に復帰
	if (bResetTestSim) {
		bResetTestSim = false;
	} else {
		statesTestSimulation->LoadState(phScene);
	}


	// シミュレーション条件をテストシミュレーション用に変更
	bIKEnabled    = phScene->GetIKEngine()->IsEnabled();
	int iter_orig = phScene->GetNumIteration();
	phScene->SetNumIteration(500);

	// バネダンパ値を退避して，ダンパ無限大にセット
	for (int i=0; i<phScene->NJoints(); ++i) {
		PHHingeJointIf* hj = phScene->GetJoint(i)->Cast();
		if (hj) {
			jointdescs[i].hinge.spring = hj->GetSpring();
			jointdescs[i].hinge.damper = hj->GetDamper();
			jointdescs[i].hinge.fMax   = hj->GetMaxForce();

			hj->SetSpring(0);
			hj->SetDamper(FLT_MAX);
			hj->SetMaxForce(FLT_MAX);
			hj->SetOffsetForce(0);
		}
		PHBallJointIf* bj = phScene->GetJoint(i)->Cast();
		if (bj) {
			jointdescs[i].ball.spring = bj->GetSpring();
			jointdescs[i].ball.damper = bj->GetDamper();
			jointdescs[i].ball.fMax   = bj->GetMaxForce();

			bj->SetSpring(0);
			bj->SetDamper(FLT_MAX);
			bj->SetMaxForce(FLT_MAX);
			bj->SetOffsetForce(Vec3d());
		}
	}

	// 接触モードを変更
	{
		int n=0;
		for (int i=0; i<phScene->NSolids(); ++i) {
			for (int j=i+1; j<phScene->NSolids(); ++j) {
				PHSolidIf* so1 = phScene->GetSolids()[i];
				PHSolidIf* so2 = phScene->GetSolids()[j];
				bool enable = soliddescs[i].bContact || soliddescs[j].bContact;
				phScene->SetContactMode(so1, so2, (enable ? PHSceneDesc::MODE_LCP : PHSceneDesc::MODE_NONE));
				n++;
			}
		}
	}

	// 剛体のパラメータを一時的に変更
	for (int i=0; i<phScene->NSolids(); ++i) {
		if (soliddescs[i].desc.mass > 0) {
			soliddescs[i].desc_orig.mass = phScene->GetSolids()[i]->GetMass();
			phScene->GetSolids()[i]->SetMass(soliddescs[i].desc.mass);
			phScene->GetSolids()[i]->SetPose(soliddescs[i].desc.pose);
			phScene->GetSolids()[i]->SetVelocity(soliddescs[i].desc.velocity);
			phScene->GetSolids()[i]->SetAngularVelocity(soliddescs[i].desc.angVelocity);
		}
	}

	// テストシミュレーション実行
	phScene->Step();

	// テストシミュレーションの結果を保存
	for (int i=0; i<phScene->NJoints(); ++i) {
		PHHingeJointIf* hj = phScene->GetJoint(i)->Cast();
		double alpha = jointdescs[i].alphaLPFTorque;
		if (hj) {
			jointdescs[i].hinge.targetPosition = hj->GetTargetPosition();
			jointdescs[i].hinge.targetVelocity = hj->GetTargetVelocity();
			jointdescs[i].hinge.offsetForce    = alpha*hj->GetMotorForce() + (1-alpha)*jointdescs[i].hinge.offsetForce;
		}
		PHBallJointIf* bj = phScene->GetJoint(i)->Cast();
		if (bj) {
			jointdescs[i].ball.targetPosition = bj->GetTargetPosition();
			jointdescs[i].ball.targetVelocity = bj->GetTargetVelocity();
			jointdescs[i].ball.offsetForce    = alpha*bj->GetMotorForce() + (1-alpha)*jointdescs[i].ball.offsetForce;
		}
	}

	// IKの状態変数を保存（LoadStateで消えてしまうので）
	for (int i=0; i<phScene->NIKActuators(); ++i) {
		PHIKHingeActuatorIf* hika = phScene->GetIKActuator(i)->Cast();
		if (hika) { hika->GetState(&(ikaStates[i])); }
		PHIKBallActuatorIf*  bika = phScene->GetIKActuator(i)->Cast();
		if (bika) { bika->GetState(&(ikaStates[i])); }
	}
	for (int i=0; i<phScene->NIKEndEffectors(); ++i) {
		PHIKEndEffectorIf* ike = phScene->GetIKEndEffector(i)->Cast();
		ike->GetState(&(ikeStates[i]));
	}

	// テストシミュレーションの結果をSaveState
	statesTestSimulation->SaveState(phScene);

	// テストシミュレーション前の状態に復帰
	statesMainSimulation->LoadState(phScene);

	// シミュレーション条件を本番用に変更
	phScene->GetIKEngine()->Enable(false);
	phScene->SetNumIteration(iter_orig);

	// 接触モードを復帰
	{
		static int count_x = 0;
		int n=0;
		for (int i=0; i<phScene->NSolids(); ++i) {
			for (int j=i+1; j<phScene->NSolids(); ++j) {
				phScene->GetSolidPair(i,j)->EnableContact(contacts[n]);
				PHSolidIf* so1 = phScene->GetSolids()[i];
				PHSolidIf* so2 = phScene->GetSolids()[j];
				phScene->SetContactMode(so1, so2, (contacts[n] ? PHSceneDesc::MODE_LCP : PHSceneDesc::MODE_NONE));
				n++;
			}
		}
		count_x++;
	}

	// 剛体のパラメータをもとに戻す
	for (int i=0; i<phScene->NSolids(); ++i) {
		if (soliddescs[i].desc.mass > 0) {
			phScene->GetSolids()[i]->SetMass(soliddescs[i].desc_orig.mass);
		}
	}

	// バネダンパを通常に戻し，計算されたオフセットトルクおよび関節目標位置をセット
	for (int i=0; i<phScene->NJoints(); ++i) {
		PHHingeJointIf* hj = phScene->GetJoint(i)->Cast();
		if (hj) {
			hj->SetMaxForce(jointdescs[i].hinge.fMax);
			hj->SetOffsetForce(jointdescs[i].hinge.offsetForce);
			hj->SetSpring(jointdescs[i].hinge.spring);
			hj->SetDamper(jointdescs[i].hinge.damper);
			hj->SetTargetPosition(jointdescs[i].hinge.targetPosition);
			hj->SetTargetVelocity(jointdescs[i].hinge.targetVelocity);
		}
		PHBallJointIf* bj = phScene->GetJoint(i)->Cast();
		if (bj) {
			bj->SetMaxForce(jointdescs[i].ball.fMax);
			bj->SetOffsetForce(jointdescs[i].ball.offsetForce);
			bj->SetSpring(jointdescs[i].ball.spring);
			bj->SetDamper(jointdescs[i].ball.damper);
			bj->SetTargetPosition(jointdescs[i].ball.targetPosition);
			bj->SetTargetVelocity(jointdescs[i].ball.targetVelocity);
		}
	}

	// IKの状態変数を復帰
	for (int i=0; i<phScene->NIKActuators(); ++i) {
		PHIKHingeActuatorIf* hika = phScene->GetIKActuator(i)->Cast();
		if (hika) { hika->SetState(&(ikaStates[i])); }
		PHIKBallActuatorIf*  bika = phScene->GetIKActuator(i)->Cast();
		if (bika) { bika->SetState(&(ikaStates[i])); }
	}
	for (int i=0; i<phScene->NIKEndEffectors(); ++i) {
		PHIKEndEffectorIf* ike = phScene->GetIKEndEffector(i)->Cast();
		ike->SetState(&(ikeStates[i]));
	}

}

void SprBlenderDLL::StepPliantAfter() {
	PHSceneIf* phScene = GetFWSdk()->GetScene(0)->GetPHScene();

	// IKの有効・無効をStepPliant実行前の値に復旧
	phScene->GetIKEngine()->Enable(bIKEnabled);

	// オフセットトルクをクリア，バネダンパ値を元通りに復旧
	for (int i=0; i<phScene->NJoints(); ++i) {
		PHHingeJointIf* hj = phScene->GetJoint(i)->Cast();
		if (hj) {
			hj->SetOffsetForce(0);
			hj->SetMaxForce(jointdescs[i].hinge.fMax);
			hj->SetSpring(jointdescs[i].hinge.spring);
			hj->SetDamper(jointdescs[i].hinge.damper);
		}
		PHBallJointIf* bj = phScene->GetJoint(i)->Cast();
		if (bj) {
			bj->SetOffsetForce(Vec3d());
			bj->SetMaxForce(jointdescs[i].ball.fMax);
			bj->SetSpring(jointdescs[i].ball.spring);
			bj->SetDamper(jointdescs[i].ball.damper);
		}
	}
}

#ifdef TOBII
//EyeX(Tobiiの関数)

//EyeX(Tobii)
// ID of the global interactor that provides our data stream; must be unique within the application.
static const TX_STRING InteractorId = "Twilight Sparkle";
// global variables
static TX_HANDLE g_hGlobalInteractorSnapshot = TX_EMPTY_HANDLE;

/*
* Initializes g_hGlobalInteractorSnapshot with an interactor that has the Gaze Point behavior.
*/
bool SprBlenderDLL::InitializeGlobalInteractorSnapshot(TX_CONTEXTHANDLE hContext)
{
	TX_HANDLE hInteractor = TX_EMPTY_HANDLE;
	TX_HANDLE hBehavior = TX_EMPTY_HANDLE;
	TX_GAZEPOINTDATAPARAMS params = { TX_GAZEPOINTDATAMODE_LIGHTLYFILTERED };
	BOOL success;

	success = txCreateGlobalInteractorSnapshot(
		hContext,
		InteractorId,
		&g_hGlobalInteractorSnapshot,
		&hInteractor) == TX_RESULT_OK;
	success &= txCreateGazePointDataBehavior(hInteractor, &params) == TX_RESULT_OK;
	success &= txCreateInteractorBehavior(hInteractor, &hBehavior, TX_BEHAVIORTYPE_EYEPOSITIONDATA) == TX_RESULT_OK;

	txReleaseObject(&hBehavior);
	txReleaseObject(&hInteractor);

	return success;
}

/*
* Callback function invoked when a snapshot has been committed.
*/
void SPR_CDECL SprBlenderDLL::OnSnapshotCommitted(TX_CONSTHANDLE hAsyncData, TX_USERPARAM param)
{
	// check the result code using an assertion.
	// this will catch validation errors and runtime errors in debug builds. in release builds it won't do anything.

	TX_RESULT result = TX_RESULT_UNKNOWN;
	txGetAsyncDataResultCode(hAsyncData, &result);
	assert(result == TX_RESULT_OK || result == TX_RESULT_CANCELLED);
}

/*
* Callback function invoked when the status of the connection to the EyeX Engine has changed.
*/
void SPR_CDECL SprBlenderDLL::OnEngineConnectionStateChanged(TX_CONNECTIONSTATE connectionState, TX_USERPARAM userParam)
{
	switch (connectionState) {
	case TX_CONNECTIONSTATE_CONNECTED: {
		BOOL success;
		printf("The connection state is now CONNECTED (We are connected to the EyeX Engine)\n");
		// commit the snapshot with the global interactor as soon as the connection to the engine is established.
		// (it cannot be done earlier because committing means "send to the engine".)
		success = txCommitSnapshotAsync(g_hGlobalInteractorSnapshot, SprBlenderDLL::OnSnapshotCommitted, NULL) == TX_RESULT_OK;
		if (!success) {
			printf("Failed to initialize the data stream.\n");
		}
		else
		{
			printf("Waiting for gaze data to start streaming...\n");
		}
	}
		break;

	case TX_CONNECTIONSTATE_DISCONNECTED:
		printf("The connection state is now DISCONNECTED (We are disconnected from the EyeX Engine)\n");
		break;

	case TX_CONNECTIONSTATE_TRYINGTOCONNECT:
		printf("The connection state is now TRYINGTOCONNECT (We are trying to connect to the EyeX Engine)\n");
		break;

	case TX_CONNECTIONSTATE_SERVERVERSIONTOOLOW:
		printf("The connection state is now SERVER_VERSION_TOO_LOW: this application requires a more recent version of the EyeX Engine to run.\n");
		break;

	case TX_CONNECTIONSTATE_SERVERVERSIONTOOHIGH:
		printf("The connection state is now SERVER_VERSION_TOO_HIGH: this application requires an older version of the EyeX Engine to run.\n");
		break;
	}
}

//現在のx座標、y座標
double GazeX, GazeY;

/*
* Handles an event from the Gaze Point data stream.
*/
void SprBlenderDLL::OnGazeDataEvent(TX_HANDLE hGazeDataBehavior)
{
	TX_GAZEPOINTDATAEVENTPARAMS eventParams;
	if (txGetGazePointDataEventParams(hGazeDataBehavior, &eventParams) == TX_RESULT_OK) {
		GazeX = eventParams.X;
		GazeY = eventParams.Y;
	} else {
		printf("Failed to interpret gaze data event packet.\n");
	}
}

double SprBlenderDLL::GetGazeX(){
	return GazeX;
}

double SprBlenderDLL::GetGazeY(){
	return GazeY;
}

Vec2d SprBlenderDLL::GetGazePosition(){
	return Vec2d(GazeX, GazeY);
}

//眼球の三次元座標
double LeftPositionX, LeftPositionY, LeftPositionZ;
double RightPositionX, RightPositionY, RightPositionZ;

/*
* Handles an event from the Eye Position data stream.
*/
void OnEyePositionDataEvent(TX_HANDLE hEyePositionDataBehavior)
{
	COORD position = { 0, 8 };
	TX_EYEPOSITIONDATAEVENTPARAMS eventParams;
	if (txGetEyePositionDataEventParams(hEyePositionDataBehavior, &eventParams) == TX_RESULT_OK) {
		//モニターの中心がゼロの座標系(単位：ミリ)
		LeftPositionX = eventParams.LeftEyeX;
		LeftPositionY = eventParams.LeftEyeY;
		LeftPositionZ = eventParams.LeftEyeZ;

		RightPositionX = eventParams.RightEyeX;
		RightPositionY = eventParams.RightEyeY;
		RightPositionZ = eventParams.RightEyeZ;
	}
	else {
		printf("Failed to interpret eye position data event packet.\n");
	}
}

Vec3d SprBlenderDLL::GetLeftPosition(){
	return Vec3d(LeftPositionX, LeftPositionY, LeftPositionZ);
}

Vec3d SprBlenderDLL::GetRightPosition(){
	return Vec3d(RightPositionX, RightPositionY, RightPositionZ);
}

Vec3d SprBlenderDLL::GetEyePosition(){
	return Vec3d((LeftPositionX + RightPositionX) / 2, (LeftPositionY + RightPositionY) / 2, (LeftPositionZ + RightPositionZ) / 2);
}

//double Aspect_X = 1280, Aspect_Y = 720; //モニターの解像度
double Aspect_X = 1920, Aspect_Y = 1080; //モニターの解像度
//double Aspect_X = 1920, Aspect_Y = 1200; //モニターの解像度
double GazeX_n, GazeY_n; //-1～+1の範囲で正規化した値

//PHRayDescに使うためのDirection(カメラを原点にしたベクトル)を計算
Vec3d SprBlenderDLL::CalculateDirection(double Viewing_angle_h){
//	double d = 64.0; //センサーサイズ
//	double f = 90.0; //Lens欄に書いてある値
	double phi,theta;

	GazeX_n = (GazeX - Aspect_X / 2) / (Aspect_X / 2); //水平方向の正規化
	GazeY_n = (GazeY - Aspect_Y / 2) / (Aspect_Y / 2) * (-1); //垂直方向の正規化

	//double Viewing_angle_h = 2 * atan( d / (2*f) ); //水平方向の視野角
	//double Viewing_angle_h = 50.089 * ( M_PI / 180 ); //水平方向の視野角50.089度は決めうち
	double Viewing_angle_v = 2 * atan( ( Aspect_Y / Aspect_X ) * tan( Viewing_angle_h / 2 ) ); //垂直方向の視野角

	phi = (M_PI / 2) - atan(GazeX_n * tan(Viewing_angle_h / 2));
	theta = (M_PI / 2) - atan(GazeY_n * tan(Viewing_angle_v / 2));

	//カメラ座標系でのベクトル
	double x = sin(theta) * cos(phi);
	double y = cos(theta);
	double z = -sin(theta) * sin(phi);

	return Vec3d(x, y, z);
}

/*
* Callback function invoked when an event has been received from the EyeX Engine.
*/
void SPR_CDECL SprBlenderDLL::HandleEvent(TX_CONSTHANDLE hAsyncData, TX_USERPARAM userParam)
{
	TX_HANDLE hEvent = TX_EMPTY_HANDLE;
	TX_HANDLE hBehavior = TX_EMPTY_HANDLE;

	txGetAsyncDataContent(hAsyncData, &hEvent);

	// NOTE. Uncomment the following line of code to view the event object. The same function can be used with any interaction object.
	//OutputDebugStringA(txDebugObject(hEvent));

	if (txGetEventBehavior(hEvent, &hBehavior, TX_BEHAVIORTYPE_GAZEPOINTDATA) == TX_RESULT_OK) {
		OnGazeDataEvent(hBehavior);
		txReleaseObject(&hBehavior);
	}

	if (txGetEventBehavior(hEvent, &hBehavior, TX_BEHAVIORTYPE_EYEPOSITIONDATA) == TX_RESULT_OK) {
		OnEyePositionDataEvent(hBehavior);
		txReleaseObject(&hBehavior);
	}

	// NOTE since this is a very simple application with a single interactor and a single data stream, 
	// our event handling code can be very simple too. A more complex application would typically have to 
	// check for multiple behaviors and route events based on interactor IDs.

	txReleaseObject(&hEvent);
}


//EyeX(Tobii)の初期化
void SprBlenderDLL::CreateEyeX() {
	TX_CONTEXTHANDLE hContext = TX_EMPTY_HANDLE;
	TX_TICKET hConnectionStateChangedTicket = TX_INVALID_TICKET;
	TX_TICKET hEventHandlerTicket = TX_INVALID_TICKET;
	BOOL success;

	// initialize and enable the context that is our link to the EyeX Engine.
	success = txInitializeEyeX(TX_EYEXCOMPONENTOVERRIDEFLAG_NONE, NULL, NULL, NULL, NULL) == TX_RESULT_OK;
	success &= txCreateContext(&hContext, TX_FALSE) == TX_RESULT_OK;
	success &= InitializeGlobalInteractorSnapshot(hContext);
	success &= txRegisterConnectionStateChangedHandler(hContext, &hConnectionStateChangedTicket, SprBlenderDLL::OnEngineConnectionStateChanged, NULL) == TX_RESULT_OK;
	success &= txRegisterEventHandler(hContext, &hEventHandlerTicket, HandleEvent, NULL) == TX_RESULT_OK;
	success &= txEnableConnection(hContext) == TX_RESULT_OK;
}

//EyeX(Tobii)の終了
void SprBlenderDLL::DestroyEyeX() {
	TX_CONTEXTHANDLE hContext = TX_EMPTY_HANDLE;
	TX_TICKET hConnectionStateChangedTicket = TX_INVALID_TICKET;
	TX_TICKET hEventHandlerTicket = TX_INVALID_TICKET;
	BOOL success;
	// disable and delete the context.
	txDisableConnection(hContext);
	txReleaseObject(&g_hGlobalInteractorSnapshot);
	success = txShutdownContext(hContext, TX_CLEANUPTIMEOUT_DEFAULT, TX_FALSE) == TX_RESULT_OK;
	success &= txReleaseContext(&hContext) == TX_RESULT_OK;
	success &= txUninitializeEyeX() == TX_RESULT_OK;
	if (!success) {
		printf("EyeX could not be shut down cleanly. Did you remember to release all handles?\n");
	}
}
#endif
