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

// Python��GIL���X�R�[�v���b�N�ɂ���N���X�B�X�R�[�v�������Ɋm����Release���邽��
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

	// �V���O���g���I�u�W�F�N�g
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

	// �C���^�t�F�[�X
	std::vector< UTRef<HIBaseIf> >  interfaces;
	FWSkeletonSensorIf* fwLeap;

	// �E�B���h�E�n���h��
	HWND                    hWnd;

	// �����������t���O
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

	// �V���O���g���擾
	static SprBlenderDLL* GetInstance();

	// �^�C�}�R�[���o�b�N
	static void SPR_CDECL TimerCallback(int id, void* arg);
	static void SPR_CDECL ThreadCallback(int id, void* arg);

	// Step�R�[���o�b�N
	static void SPR_CDECL CallbackBeforeStep(void* arg);
	static void SPR_CDECL CallbackAfterStep(void* arg);
	
	// --- --- --- --- ---

	// �R���X�g���N�^�E�f�X�g���N�^
	SprBlenderDLL();
	~SprBlenderDLL() {
		timerPhysics->Stop();
		timerHaptic->Stop();

		#ifdef LEAPMOTION
		DestroyLeap();
		#endif

		#ifdef TOBII
		//EyeX�̏I��
		DestroyEyeX();
		#endif
	}

	// ������
	void Init();

	// �L���E����
	void Enable(bool bEnable) { this->bEnable = bEnable; }

	// --- --- --- --- ---

	// SDK�擾
	FWSdkIf*  GetFWSdk() { return fwSdk; }
	CRSdkIf*  GetCRSdk() { return crSdk; }
	HISdkIf*  GetHISdk() { return hiSdk; }

	// Render�擾
	GRRenderIf* GetGRRender() { return grRender; }

	// --- --- --- --- ---

	// �C���^�t�F�[�X�擾
	int NInterfaces() { return (int)interfaces.size(); }
	HIBaseIf* GetInterface(int i) { return interfaces[i]; }

	// SPIDAR�̍쐬
	HISpidarGIf* CreateSPIDAR();

	// SpaceNavigator�̍쐬
	HISpaceNavigatorIf* CreateSpaceNavigator();

	// SpaceNavigator�̍쐬
	HINovintFalconIf* CreateNovintFalcon();

	// HapticPointer�̍쐬
	FWHapticPointerIf*  CreateHapticPointer(FWSceneIf* fwScene, HIBaseIf* hi);

	// Leapmotion�̍쐬
	FWSkeletonSensorIf* CreateLeap();
	FWSkeletonSensorIf* CreateLeapUDP();

	// �^�C�}�擾
	UTTimerIf*  GetHapticTimer()  { return timerHaptic;  }
	UTTimerIf*  GetPhysicsTimer() { return timerPhysics; }

	// �^�C�}�R�[���o�b�N
	void TimerFunc(int id);
	void ThreadFunc(int id);

	// Step�R�[���o�b�N
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

	/// Pliant-torque�Ƀ��[�p�X��������Dalpha��1�X�e�b�v������̓K�p����
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

	// <!!>�i�f�o�b�O�p�j ���݂̃V�[�����o��
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

	//EyeX(Tobii�̊֐�)
	bool InitializeGlobalInteractorSnapshot(TX_CONTEXTHANDLE hContext);
	static void SPR_CDECL OnSnapshotCommitted(TX_CONSTHANDLE hAsyncData, TX_USERPARAM param);
	static void SPR_CDECL OnEngineConnectionStateChanged(TX_CONNECTIONSTATE connectionState, TX_USERPARAM userParam);
	static void OnGazeDataEvent(TX_HANDLE hGazeDataBehavior);
	static void SPR_CDECL HandleEvent(TX_CONSTHANDLE hAsyncData, TX_USERPARAM userParam);

	double GetGazeX();
	double GetGazeY();

	Vec3d CalculateDirection(double Viewing_angle_h);

	Vec2d GetGazePosition(); //��ʏ�Ō��Ă���_��2�������W

	Vec3d GetLeftPosition(); //�ዅ��3�������W(��)
	Vec3d GetRightPosition(); //�ዅ��3�������W(�E)
	Vec3d GetEyePosition(); //���E�̊ዅ�̊Ԃ�3�������W

	#endif

};

