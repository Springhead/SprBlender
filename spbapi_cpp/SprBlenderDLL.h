#include <Physics/PHHapticEngine.h>
#include <EmbPython/EmbPython.h>

#include <sstream>
#include <fstream>
#include "windows.h"
#include <mmsystem.h>
#include <EmbPython/EmbPython.h>

// #define USE_KINECT

#ifdef USE_KINECT
#pragma comment(lib,"Kinect20.lib")
#pragma comment(lib,"Kinect20.Face.lib")
#pragma comment(lib,"Kinect20.Fusion.lib")
#pragma comment(lib,"Kinect20.VisualGestureBuilder.lib")
#include <Kinect.h>
#endif

// #define TOBII

#ifdef TOBII
//EyeX
#include <stdio.h>
#include <conio.h>
#include <assert.h>
#include "eyex\EyeX.h"

#pragma comment(lib,"Tobii.EyeX.Client.lib")
#endif

// PythonのGILをスコープロックにするクラス。スコープ抜け時に確実にReleaseするため
class PythonGIL {
	PyGILState_STATE state;
public:
	PythonGIL()  { state = PyGILState_Ensure(); }
	~PythonGIL() { PyGILState_Release(state);   }
};

// <!!>
template<class Interface>
inline void SafeRelease(Interface *& pInterfaceToRelease)
{
	if (pInterfaceToRelease != NULL){
		pInterfaceToRelease->Release();
		pInterfaceToRelease = NULL;
	}
}

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
class SprBlenderDLL {

	// シングルトンオブジェクト
	static SprBlenderDLL* instance;

	// --- --- --- --- ---

	// SDK
	UTRef< FWSdkIf >        fwSdk;
	UTRef< CRSdkIf >        crSdk;
	UTRef< HISdkIf >        hiSdk;

	// Render
	UTRef< GRRenderIf >     grRender;

	// Timer
	UTTimerIf*              timerHaptic;
	UTTimerIf*              timerPhysics;
	int                     timerHapticID;
	int                     timerPhysicsID;

	// CPS Counter
	float					cps;

	// インタフェース
	std::vector< UTRef<HIBaseIf> >  interfaces;
	FWSkeletonSensorIf* fwLeap;

	// ウィンドウハンドル
	HWND                    hWnd;

	// 初期化完了フラグ
	bool                    bInitialized;

	// For SaveState
	UTRef<ObjectStatesIf>	statesMainSimulation;
	UTRef<ObjectStatesIf>	statesTestSimulation;

	// For Pliant Motion
	struct JointDesc {
		PHHingeJointDesc hinge;
		PHBallJointDesc  ball;
		double           alphaLPFTorque;
		JointDesc() {
			hinge.offsetForce = 0.0;
			ball.offsetForce  = Vec3d();
			alphaLPFTorque    = 1.0;
		}
	};
	std::vector<JointDesc>	 jointdescs;

	struct SolidDesc {
		PHSolidDesc desc;
		PHSolidDesc desc_orig;
		bool        bContact;
		SolidDesc() {
			desc      = PHSolidDesc();
			desc_orig = PHSolidDesc();
			desc.mass = -1;
			bContact  = false;
		}
	};
	std::vector<SolidDesc>   soliddescs;

	std::vector<bool>        contacts;

	bool                     bEnable;
	bool                     bIKEnabled;
	bool                     bPliant, bPliantBefore;
	bool                     bResetTestSim;

	std::vector<PHIKActuatorState>		ikaStates;
	std::vector<PHIKEndEffectorState>	ikeStates;

	PyObject*				callbackCreatureRuleStep;

public:

	// シングルトン取得
	static SprBlenderDLL* GetInstance();

	// タイマコールバック
	static void SPR_CDECL TimerCallback(int id, void* arg);
	static void SPR_CDECL ThreadCallback(int id, void* arg);

	// Stepコールバック
	static void SPR_CDECL CallbackBeforeStep(void* arg);
	static void SPR_CDECL CallbackAfterStep(void* arg);
	
	// --- --- --- --- ---

	// コンストラクタ・デストラクタ
	SprBlenderDLL();
	~SprBlenderDLL() {
		timerPhysics->Stop();
		timerHaptic->Stop();

		#ifdef LEAPMOTION
		DestroyLeap();
		#endif

		#ifdef TOBII
		//EyeXの終了
		DestroyEyeX();
		#endif
	}

	// 初期化
	void Init();

	// 有効・無効
	void Enable(bool bEnable) { this->bEnable = bEnable; }

	// --- --- --- --- ---

	// SDK取得
	FWSdkIf*  GetFWSdk() { return fwSdk; }
	CRSdkIf*  GetCRSdk() { return crSdk; }
	HISdkIf*  GetHISdk() { return hiSdk; }

	// Render取得
	GRRenderIf* GetGRRender() { return grRender; }

	// --- --- --- --- ---

	// インタフェース取得
	int NInterfaces() { return (int)interfaces.size(); }
	HIBaseIf* GetInterface(int i) { return interfaces[i]; }

	// SPIDARの作成
	HISpidarGIf* CreateSPIDAR();

	// SpaceNavigatorの作成
	HISpaceNavigatorIf* CreateSpaceNavigator();

	// SpaceNavigatorの作成
	HINovintFalconIf* CreateNovintFalcon();

	// HapticPointerの作成
	FWHapticPointerIf*  CreateHapticPointer(FWSceneIf* fwScene, HIBaseIf* hi);

	// Leapmotionの作成
	FWSkeletonSensorIf* CreateLeap();
	FWSkeletonSensorIf* CreateLeapUDP();

	// タイマ取得
	UTTimerIf*  GetHapticTimer()  { return timerHaptic;  }
	UTTimerIf*  GetPhysicsTimer() { return timerPhysics; }

	// タイマコールバック
	void TimerFunc(int id);
	void ThreadFunc(int id);

	// Stepコールバック
	void BeforeStep();
	void AfterStep();
	void OneStep() {
		bool bEnableOrig = bEnable;
		bEnable = true;
		BeforeStep();
		fwSdk->GetScene(0)->GetPHScene()->Step();
		AfterStep();
		bEnable = bEnableOrig;
	}

	// --- --- --- --- ---

	// Step for Pliant Motion
	void StepPliantBefore();
	void StepPliantAfter();

	void EnablePliant(bool enable) { bPliant = enable; }
	bool IsPliantEnabled()         { return bPliant;   }

	void ResetTestSimulation()     { bResetTestSim = true; }

	void SetPliantSolidMass(PHSolidIf* solid, double mass) {
		PHSceneIf* phScene = GetFWSdk()->GetScene(0)->GetPHScene();
		soliddescs.resize(phScene->NSolids());
		for (int i=0; i<phScene->NSolids(); ++i) {
			if (phScene->GetSolids()[i] == solid) {
				soliddescs[i].desc.mass = mass;
			}
		}
	}

	void SetPliantSolidContact(PHSolidIf* solid, bool enabled) {
		PHSceneIf* phScene = GetFWSdk()->GetScene(0)->GetPHScene();
		soliddescs.resize(phScene->NSolids());
		for (int i=0; i<phScene->NSolids(); ++i) {
			if (phScene->GetSolids()[i] == solid) {
				soliddescs[i].bContact = enabled;
			}
		}
	}

	/// Pliant-torqueにローパスをかける．alphaは1ステップあたりの適用割合
	void SetPliantTorqueLPF(PHJointIf* joint, double alpha) {
		PHSceneIf* phScene = GetFWSdk()->GetScene(0)->GetPHScene();
		jointdescs.resize(phScene->NJoints());
		for (int i=0; i<phScene->NJoints(); ++i) {
			if (phScene->GetJoint(i) == joint) {
				jointdescs[i].alphaLPFTorque = alpha;
			}
		}
	}

	// --- --- --- --- ---

	#ifdef USE_KINECT
	// Kinect
	UTTimerIf*  GetKinectTimer() { return timerkinect; }
	void KinectFunc(int id);
	UTTimerIf*				timerkinect;
	int						timerkinectID;
	static void SPR_CDECL KinectCallback(int id, void* arg);
	bool                CreateKinect();
	bool                bKinectInitialized;
	IKinectSensor*      pSensor;
	IBodyFrameSource*   pBodySource;
	IBodyFrameReader*   pBodyReader;
	PHSolidIf*          KinectBone[6][8];
	#endif

	// --- --- --- --- ---

	// <!!>（デバッグ用） 現在のシーンを出力
	void PrintScene() { fwSdk->Print(std::cout); }

	// CPS Count
	float GetCPS() { return cps; }

	// Step Count
	int GetCount() {
		if (bInitialized) {
			return GetFWSdk()->GetScene(0)->GetPHScene()->GetCount();
		} else {
			return 0;
		}
	}

	// --- --- --- --- ---

	#ifdef TOBII
	void CreateEyeX();
	void DestroyEyeX();

	//EyeX(Tobiiの関数)
	bool InitializeGlobalInteractorSnapshot(TX_CONTEXTHANDLE hContext);
	static void SPR_CDECL OnSnapshotCommitted(TX_CONSTHANDLE hAsyncData, TX_USERPARAM param);
	static void SPR_CDECL OnEngineConnectionStateChanged(TX_CONNECTIONSTATE connectionState, TX_USERPARAM userParam);
	static void OnGazeDataEvent(TX_HANDLE hGazeDataBehavior);
	static void SPR_CDECL HandleEvent(TX_CONSTHANDLE hAsyncData, TX_USERPARAM userParam);

	double GetGazeX();
	double GetGazeY();

	Vec3d CalculateDirection(double Viewing_angle_h);

	Vec2d GetGazePosition(); //画面上で見ている点の2次元座標

	Vec3d GetLeftPosition(); //眼球の3次元座標(左)
	Vec3d GetRightPosition(); //眼球の3次元座標(右)
	Vec3d GetEyePosition(); //左右の眼球の間の3次元座標

	#endif

};

