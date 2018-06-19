#ifndef EPSPRBLENDERDLL_H
#define EPSPRBLENDERDLL_H

//{*********EPPythonGIL*******
void toEPPythonGIL( EPObject* obj);
//}EPPythonGIL

//{*********EPSprBlenderDLL*******
void toEPSprBlenderDLL( EPObject* obj);
PyObject* __PYDECL EPSprBlenderDLL_AfterStep( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_BeforeStep( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_CallbackAfterStep( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_CallbackBeforeStep( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_CreateHapticPointer( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_CreateLeap( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_CreateLeapUDP( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_CreateNovintFalcon( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_CreateSPIDAR( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_CreateSpaceNavigator( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_Enable( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_EnablePliant( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_GetCPS( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_GetCRSdk( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_GetCount( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_GetFWSdk( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_GetGRRender( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_GetHISdk( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_GetHapticTimer( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_GetInstance( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_GetInterface( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_GetPhysicsTimer( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_Init( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_IsPliantEnabled( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_NInterfaces( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_OneStep( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_PrintScene( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_ResetTestSimulation( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_SetPliantSolidContact( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_SetPliantSolidMass( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_SetPliantTorqueLPF( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_StepPliantAfter( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_StepPliantBefore( PyObject* self );
PyObject* __PYDECL EPSprBlenderDLL_ThreadCallback( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_ThreadFunc( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_TimerCallback( PyObject* self,PyObject* arg );
PyObject* __PYDECL EPSprBlenderDLL_TimerFunc( PyObject* self,PyObject* arg );
//}EPSprBlenderDLL
#endif
