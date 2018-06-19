%module SprBlenderDLL



%define EXTEND_NEW(type)
%header%{
	PyObject* __EPDECL newEP##type(type var1);
	PyObject* __EPDECL newEP##type();
%}

%wrapper%{
	PyObject* newEP##type(type var1)
	{
		PyObject *ret = EP##type##_new(&EP##type##Type,NULL,NULL);
		EPObject_Ptr(ret) = new type(var1);
		((EPObject*)ret)->mm = EP_MM_PY;
		return ret;
	}
	
	PyObject* newEP##type()
	{
		PyObject *ret = EP##type##_new(&EP##type##Type,NULL,NULL);
		EPObject_Ptr(ret) = new type();
		((EPObject*)ret)->mm = EP_MM_PY;
		return ret;
	}
%}
%enddef

%ignore LeapListener;
%ignore SprBlenderDLL::TimerCallBack;
%ignore SprBlenderDLL::leap;
%ignore SprBlenderDLL::leapListener;
%ignore SprBlenderDLL::fingerFromPalm;

%ignore SprBlenderDLL::InitKinect;
%ignore SprBlenderDLL::KinectBone;
%ignore SprBlenderDLL::pSensor;
%ignore SprBlenderDLL::pBodySource;
%ignore SprBlenderDLL::pBodyReader;
%ignore Human::Position;
%ignore Human::state;

%ignore SprBlenderDLL::InitializeGlobalInteractorSnapshot;
%ignore SprBlenderDLL::OnSnapshotCommitted;
%ignore SprBlenderDLL::OnEngineConnectionStateChanged;
%ignore SprBlenderDLL::OnGazeDataEvent;
%ignore SprBlenderDLL::HandleEvent;

#define SPR_CDECL 
%include "SprBlenderDLL.h"
