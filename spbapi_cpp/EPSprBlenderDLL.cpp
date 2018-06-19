#include "../../Springhead/core/include/Springhead.h"                 
#include "../../Springhead/core/include/EmbPython/SprEPUtility.h"    
#include "../../Springhead/core/include/EmbPython/SprEPBase.h"       
#include "../../Springhead/core/include/EmbPython/SprEPFoundation.h" 
#include "SprBlenderDLL.h"                            
#include "SprEPSprBlenderDLL.h"                       
#pragma warning(disable:4244)                    
//*********** Decl Global variables ***********



//{*********EPPythonGIL*******
int __PYDECL EPPythonGIL_PythonGIL( PyObject* self,PyObject* arg,PyObject* kwds )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if(!arg) return 0;
		EPObject_Ptr(self) = new PythonGIL();
		if(EPObject_Ptr(self) != NULL) return 0;
		else
		{
			PyErr_NoMemory();
			return -1;
		}
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}

static PyMethodDef EPPythonGIL_method_table[] =
{
	{NULL}
};
static PyNumberMethods EPPythonGIL_math_method_table=
{
	(binaryfunc)NULL,/* __add__ */
	(binaryfunc)NULL,/* __sub__ */
	(binaryfunc)NULL,/* __mul__ */
	(binaryfunc)NULL,/* __mod__ */
	(binaryfunc)NULL,/* __divmod__ */
	(ternaryfunc)NULL,/* __pow__ */
	(unaryfunc)NULL,/* __neg__ */
	(unaryfunc)NULL,/* __pos__ */
	(unaryfunc)NULL,/* __abs__ */
	(inquiry)NULL,/* __bool__ */
	(unaryfunc)NULL,/* __invert__ */
	(binaryfunc)NULL,/* __lshift__ */
	(binaryfunc)NULL,/* __rshift__ */
	(binaryfunc)NULL,/* __and__ */
	(binaryfunc)NULL,/* __xor__ */
	(binaryfunc)NULL,/* __or__ */
	(unaryfunc)NULL,/* __int__ */
	(void *)NULL,/* __reserved__ */
	(unaryfunc)NULL,/* __float__ */
	(binaryfunc)NULL,/* __iadd__ */
	(binaryfunc)NULL,/* __isub__ */
	(binaryfunc)NULL,/* __imul__ */
	(binaryfunc)NULL,/* __imod__ */
	(ternaryfunc)NULL,/* __ipow__ */
	(binaryfunc)NULL,/* __ilshift__ */
	(binaryfunc)NULL,/* __irshift__ */
	(binaryfunc)NULL,/* __iand__ */
	(binaryfunc)NULL,/* __ixor__ */
	(binaryfunc)NULL,/* __ior__ */
	(binaryfunc)NULL,/* __floordiv__ */
	(binaryfunc)NULL,/* __div__ */
	(binaryfunc)NULL,/* __ifloordiv__ */
	(binaryfunc)NULL,/* __itruediv__ */
};
static PyGetSetDef EPPythonGIL_getset_table[] =
{
	{NULL}
};
void __PYDECL EPPythonGIL_dealloc(PyObject* self)
{
#ifdef DEBUG_OUTPUT
	printf("PythonGIL dealloc called (MemoryManager=");
	if( ((EPObject*)self)->mm == EP_MM_SPR ) printf("Springhead)\n");
	else if( ((EPObject*)self)->mm == EP_MM_PY ) printf("Python)\n");
#endif
	if ( ((EPObject*)self)->mm == EP_MM_PY ) delete EPObject_Ptr(self);
	self->ob_type->tp_free(self);
}
PyObject* __PYDECL EPPythonGIL_str()
{
	return Py_BuildValue("s","This is EPPythonGILObject.");
}
PyObject* __PYDECL EPPythonGIL_new(PyTypeObject *type,PyObject *args, PyObject *kwds)
{
	try
	{
		PyObject* self;
		self = type->tp_alloc(type,0);
		if ( self != NULL )
		{
			EPObject_Ptr(self) = NULL;
			((EPObject*)self)->mm = EP_MM_PY;
			return self;
		}
		return PyErr_NoMemory();
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyTypeObject EPPythonGILType =
{
	PyVarObject_HEAD_INIT(NULL,0)
	"SprBlenderDLL.PythonGIL",/*tp_name*/
	sizeof(EPObject),/*tp_basicsize*/
	0,/*tp_itemsize*/
	(destructor)EPPythonGIL_dealloc,/*tp_dealloc*/
	0,/*tp_print*/
	0,/*tp_getattr*/
	0,/*tp_setattr*/
	0,/*tp_reserved*/
	0,/*tp_repr*/
	&EPPythonGIL_math_method_table,/*tp_as_number*/
	0,/*tp_as_sequence*/
	0,/*tp_as_mapping*/
	0,/*tp_call*/
	0,/*tp_hash*/
	(reprfunc)EPPythonGIL_str,/*tp_str*/
	0,/*tp_getattro*/
	0,/*tp_setattro*/
	0,/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,/*tp_flags*/
	"PythonGIL",/*tp_doc*/
	0,/*tp_traverse*/
	0,/*tp_clear*/
	0,/*tp_richcompare*/
	0,/*tp_weaklistoffset*/
	0,/*tp_iter*/
	0,/*tp_iternext*/
	EPPythonGIL_method_table,/*tp_methods*/
	0,/*tp_members*/
	EPPythonGIL_getset_table,/*tp_getset*/
	&EPObjectType,
	0,/*tp_dict*/
	0,/*tp_descr_get*/
	0,/*tp_descr_set*/
	0,/*tp_dictoffset*/
	(initproc)EPPythonGIL_PythonGIL,/*tp_init*/
	0,/*tp_alloc*/
	(newfunc)EPPythonGIL_new,/*tp_new*/
};
void initEPPythonGIL(PyObject *rootModule)
{
	if ( PyType_Ready( &EPPythonGILType ) < 0 ) return ;//PythonƒNƒ‰ƒX‚Ìì¬
	string package;
	if(rootModule) package = PyModule_GetName(rootModule);
	else // rootModule‚ª“n‚³‚ê‚½ê‡‚ÍEP_MODULE_NAME‚Í–³Ž‹‚³‚ê‚é
	{
#ifdef EP_MODULE_NAME
		package = EP_MODULE_NAME ".";
		rootModule = PyImport_AddModule( EP_MODULE_NAME );
#else
		package = "";
		rootModule = PyImport_AddModule("__main__");
#endif
	}
#ifdef EP_USE_SUBMODULE
	PyObject *subModule = PyImport_AddModule( (package+"SprBlenderDLL").c_str() );
	Py_INCREF(subModule);
	PyModule_AddObject(rootModule,"SprBlenderDLL",subModule);
#else
	PyObject *subModule = rootModule;
#endif
	Py_INCREF(&EPPythonGILType);
	PyModule_AddObject(subModule,"PythonGIL",(PyObject*)&EPPythonGILType);
}
PyObject* newEPPythonGIL(const PythonGIL* org)
{
	try
	{
		if(org == NULL)
		{
			Py_RETURN_NONE;
		}
		PyObject *ret = EPPythonGIL_new(&EPPythonGILType,NULL,NULL);
		EPObject_Ptr(ret) = org;
		((EPObject*)ret)->mm = EP_MM_SPR;
		return ret;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
void toEPPythonGIL( EPObject* obj)
{
	obj->ob_base.ob_type = &EPPythonGILType;
}
//}PythonGIL

//{*********EPSprBlenderDLL*******
int __PYDECL EPSprBlenderDLL_SprBlenderDLL( PyObject* self,PyObject* arg,PyObject* kwds )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if(!arg) return 0;
		EPObject_Ptr(self) = new SprBlenderDLL();
		if(EPObject_Ptr(self) != NULL) return 0;
		else
		{
			PyErr_NoMemory();
			return -1;
		}
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_AfterStep( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.AfterStep");
			return NULL;
		}
		if(true)
		{
			EPObject_Cast(self,SprBlenderDLL)->AfterStep();
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_BeforeStep( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.BeforeStep");
			return NULL;
		}
		if(true)
		{
			EPObject_Cast(self,SprBlenderDLL)->BeforeStep();
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_CallbackAfterStep( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if(EPObject_Check(arg))
		{
			PyObject * py_param1 = arg;
			void * c_param1 = EPObject_Cast(py_param1,void);

			SprBlenderDLL::CallbackAfterStep(c_param1);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_CallbackBeforeStep( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if(EPObject_Check(arg))
		{
			PyObject * py_param1 = arg;
			void * c_param1 = EPObject_Cast(py_param1,void);

			SprBlenderDLL::CallbackBeforeStep(c_param1);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_CreateHapticPointer( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.CreateHapticPointer");
			return NULL;
		}
		if(arg && PyTuple_Size(arg) == 2&&EPFWSceneIf_Check((PyTuple_GetItem(arg,0))) && EPHIBaseIf_Check((PyTuple_GetItem(arg,1))))
		{
			FWHapticPointerIf* ret_tmp;
			PyObject * py_param1 = (PyTuple_GetItem(arg,0));
			FWSceneIf * c_param1 = EPObject_Cast(py_param1,FWSceneIf);

			PyObject * py_param2 = (PyTuple_GetItem(arg,1));
			HIBaseIf * c_param2 = EPObject_Cast(py_param2,HIBaseIf);

			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->CreateHapticPointer(c_param1,c_param2);
			FWHapticPointerIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPFWHapticPointerIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_CreateLeap( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.CreateLeap");
			return NULL;
		}
		if(true)
		{
			FWSkeletonSensorIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->CreateLeap();
			FWSkeletonSensorIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPFWSkeletonSensorIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_CreateLeapUDP( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.CreateLeapUDP");
			return NULL;
		}
		if(true)
		{
			FWSkeletonSensorIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->CreateLeapUDP();
			FWSkeletonSensorIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPFWSkeletonSensorIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_CreateNovintFalcon( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.CreateNovintFalcon");
			return NULL;
		}
		if(true)
		{
			HINovintFalconIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->CreateNovintFalcon();
			HINovintFalconIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPHINovintFalconIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_CreateSPIDAR( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.CreateSPIDAR");
			return NULL;
		}
		if(true)
		{
			HISpidarGIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->CreateSPIDAR();
			HISpidarGIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPHISpidarGIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_CreateSpaceNavigator( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.CreateSpaceNavigator");
			return NULL;
		}
		if(true)
		{
			HISpaceNavigatorIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->CreateSpaceNavigator();
			HISpaceNavigatorIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPHISpaceNavigatorIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_Enable( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.Enable");
			return NULL;
		}
		if(true)
		{
			PyObject * py_param1 = arg;
			bool c_param1 = (Py_True == py_param1);

			EPObject_Cast(self,SprBlenderDLL)->Enable(c_param1);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_EnablePliant( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.EnablePliant");
			return NULL;
		}
		if(true)
		{
			PyObject * py_param1 = arg;
			bool c_param1 = (Py_True == py_param1);

			EPObject_Cast(self,SprBlenderDLL)->EnablePliant(c_param1);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetCPS( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetCPS");
			return NULL;
		}
		if(true)
		{
			float ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetCPS();
			float c_ret =  ret_tmp;
			PyObject* py_ret = PyFloat_fromAny(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetCRSdk( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetCRSdk");
			return NULL;
		}
		if(true)
		{
			CRSdkIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetCRSdk();
			CRSdkIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPCRSdkIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetCount( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetCount");
			return NULL;
		}
		if(true)
		{
			int ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetCount();
			int c_ret =  ret_tmp;
			PyObject* py_ret = PyLong_fromAny(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetFWSdk( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetFWSdk");
			return NULL;
		}
		if(true)
		{
			FWSdkIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetFWSdk();
			FWSdkIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPFWSdkIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetGRRender( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetGRRender");
			return NULL;
		}
		if(true)
		{
			GRRenderIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetGRRender();
			GRRenderIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPGRRenderIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetHISdk( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetHISdk");
			return NULL;
		}
		if(true)
		{
			HISdkIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetHISdk();
			HISdkIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPHISdkIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetHapticTimer( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetHapticTimer");
			return NULL;
		}
		if(true)
		{
			UTTimerIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetHapticTimer();
			UTTimerIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPUTTimerIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetInstance( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if(true)
		{
			SprBlenderDLL* ret_tmp;
			ret_tmp = SprBlenderDLL::GetInstance();
			SprBlenderDLL* c_ret =  ret_tmp;
			PyObject* py_ret = newEPSprBlenderDLL(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetInterface( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetInterface");
			return NULL;
		}
		if((PyFloat_Check(arg) || PyLong_Check(arg)))
		{
			HIBaseIf* ret_tmp;
			PyObject * py_param1 = arg;
			int c_param1 = PyObject_asLong(py_param1);

			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetInterface(c_param1);
			HIBaseIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPHIBaseIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_GetPhysicsTimer( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.GetPhysicsTimer");
			return NULL;
		}
		if(true)
		{
			UTTimerIf* ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->GetPhysicsTimer();
			UTTimerIf* c_ret =  ret_tmp;
			PyObject* py_ret = newEPUTTimerIf(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			if ( !EPObject_Ptr(py_ret) ) Py_RETURN_NONE;
			EPObject_RuntimeDCast((EPObject*)py_ret,c_ret->GetIfInfo());
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_Init( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.Init");
			return NULL;
		}
		if(true)
		{
			EPObject_Cast(self,SprBlenderDLL)->Init();
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_IsPliantEnabled( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.IsPliantEnabled");
			return NULL;
		}
		if(true)
		{
			bool ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->IsPliantEnabled();
			bool c_ret =  ret_tmp;
			PyObject* py_ret = PyBool_FromLong(c_ret? 1 : 0);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_NInterfaces( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.NInterfaces");
			return NULL;
		}
		if(true)
		{
			int ret_tmp;
			ret_tmp = EPObject_Cast(self,SprBlenderDLL)->NInterfaces();
			int c_ret =  ret_tmp;
			PyObject* py_ret = PyLong_fromAny(c_ret);
			if ( !py_ret )
			{
				PyErr_BadInternalCall();
				return NULL;
			}
			if ( py_ret == Py_None ) Py_RETURN_NONE;
			return py_ret;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_OneStep( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.OneStep");
			return NULL;
		}
		if(true)
		{
			EPObject_Cast(self,SprBlenderDLL)->OneStep();
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_PrintScene( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.PrintScene");
			return NULL;
		}
		if(true)
		{
			EPObject_Cast(self,SprBlenderDLL)->PrintScene();
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_ResetTestSimulation( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.ResetTestSimulation");
			return NULL;
		}
		if(true)
		{
			EPObject_Cast(self,SprBlenderDLL)->ResetTestSimulation();
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_SetPliantSolidContact( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.SetPliantSolidContact");
			return NULL;
		}
		if(arg && PyTuple_Size(arg) == 2&&EPPHSolidIf_Check((PyTuple_GetItem(arg,0))) && true)
		{
			PyObject * py_param1 = (PyTuple_GetItem(arg,0));
			PHSolidIf * c_param1 = EPObject_Cast(py_param1,PHSolidIf);

			PyObject * py_param2 = (PyTuple_GetItem(arg,1));
			bool c_param2 = (Py_True == py_param2);

			EPObject_Cast(self,SprBlenderDLL)->SetPliantSolidContact(c_param1,c_param2);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_SetPliantSolidMass( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.SetPliantSolidMass");
			return NULL;
		}
		if(arg && PyTuple_Size(arg) == 2&&EPPHSolidIf_Check((PyTuple_GetItem(arg,0))) && (PyFloat_Check((PyTuple_GetItem(arg,1))) || PyLong_Check((PyTuple_GetItem(arg,1)))))
		{
			PyObject * py_param1 = (PyTuple_GetItem(arg,0));
			PHSolidIf * c_param1 = EPObject_Cast(py_param1,PHSolidIf);

			PyObject * py_param2 = (PyTuple_GetItem(arg,1));
			double c_param2 = PyObject_asDouble(py_param2);

			EPObject_Cast(self,SprBlenderDLL)->SetPliantSolidMass(c_param1,c_param2);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_SetPliantTorqueLPF( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.SetPliantTorqueLPF");
			return NULL;
		}
		if(arg && PyTuple_Size(arg) == 2&&EPPHJointIf_Check((PyTuple_GetItem(arg,0))) && (PyFloat_Check((PyTuple_GetItem(arg,1))) || PyLong_Check((PyTuple_GetItem(arg,1)))))
		{
			PyObject * py_param1 = (PyTuple_GetItem(arg,0));
			PHJointIf * c_param1 = EPObject_Cast(py_param1,PHJointIf);

			PyObject * py_param2 = (PyTuple_GetItem(arg,1));
			double c_param2 = PyObject_asDouble(py_param2);

			EPObject_Cast(self,SprBlenderDLL)->SetPliantTorqueLPF(c_param1,c_param2);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_StepPliantAfter( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.StepPliantAfter");
			return NULL;
		}
		if(true)
		{
			EPObject_Cast(self,SprBlenderDLL)->StepPliantAfter();
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_StepPliantBefore( PyObject* self )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.StepPliantBefore");
			return NULL;
		}
		if(true)
		{
			EPObject_Cast(self,SprBlenderDLL)->StepPliantBefore();
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_ThreadCallback( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if(arg && PyTuple_Size(arg) == 2&&(PyFloat_Check((PyTuple_GetItem(arg,0))) || PyLong_Check((PyTuple_GetItem(arg,0)))) && EPObject_Check((PyTuple_GetItem(arg,1))))
		{
			PyObject * py_param1 = (PyTuple_GetItem(arg,0));
			int c_param1 = PyObject_asLong(py_param1);

			PyObject * py_param2 = (PyTuple_GetItem(arg,1));
			void * c_param2 = EPObject_Cast(py_param2,void);

			SprBlenderDLL::ThreadCallback(c_param1,c_param2);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_ThreadFunc( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.ThreadFunc");
			return NULL;
		}
		if((PyFloat_Check(arg) || PyLong_Check(arg)))
		{
			PyObject * py_param1 = arg;
			int c_param1 = PyObject_asLong(py_param1);

			EPObject_Cast(self,SprBlenderDLL)->ThreadFunc(c_param1);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_TimerCallback( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if(arg && PyTuple_Size(arg) == 2&&(PyFloat_Check((PyTuple_GetItem(arg,0))) || PyLong_Check((PyTuple_GetItem(arg,0)))) && EPObject_Check((PyTuple_GetItem(arg,1))))
		{
			PyObject * py_param1 = (PyTuple_GetItem(arg,0));
			int c_param1 = PyObject_asLong(py_param1);

			PyObject * py_param2 = (PyTuple_GetItem(arg,1));
			void * c_param2 = EPObject_Cast(py_param2,void);

			SprBlenderDLL::TimerCallback(c_param1,c_param2);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyObject* __PYDECL EPSprBlenderDLL_TimerFunc( PyObject* self,PyObject* arg )
{
	try
	{
		UTAutoLock LOCK(EPCriticalSection);

		if( EPObject_Ptr(self) == NULL )
		{
			PyErr_SetString( PyErr_Spr_NullReference , "Null Reference in SprBlenderDLL.TimerFunc");
			return NULL;
		}
		if((PyFloat_Check(arg) || PyLong_Check(arg)))
		{
			PyObject * py_param1 = arg;
			int c_param1 = PyObject_asLong(py_param1);

			EPObject_Cast(self,SprBlenderDLL)->TimerFunc(c_param1);
			Py_RETURN_NONE;
		}
		PyErr_BadArgument();
		return NULL;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}

static PyMethodDef EPSprBlenderDLL_method_table[] =
{
	{"AfterStep",(PyCFunction)EPSprBlenderDLL_AfterStep,METH_NOARGS ,"EPSprBlenderDLL::AfterStep"},
	{"BeforeStep",(PyCFunction)EPSprBlenderDLL_BeforeStep,METH_NOARGS ,"EPSprBlenderDLL::BeforeStep"},
	{"CallbackAfterStep",(PyCFunction)EPSprBlenderDLL_CallbackAfterStep,METH_O | METH_STATIC,"EPSprBlenderDLL::CallbackAfterStep"},
	{"CallbackBeforeStep",(PyCFunction)EPSprBlenderDLL_CallbackBeforeStep,METH_O | METH_STATIC,"EPSprBlenderDLL::CallbackBeforeStep"},
	{"CreateHapticPointer",(PyCFunction)EPSprBlenderDLL_CreateHapticPointer,METH_VARARGS ,"EPSprBlenderDLL::CreateHapticPointer"},
	{"CreateLeap",(PyCFunction)EPSprBlenderDLL_CreateLeap,METH_NOARGS ,"EPSprBlenderDLL::CreateLeap"},
	{"CreateLeapUDP",(PyCFunction)EPSprBlenderDLL_CreateLeapUDP,METH_NOARGS ,"EPSprBlenderDLL::CreateLeapUDP"},
	{"CreateNovintFalcon",(PyCFunction)EPSprBlenderDLL_CreateNovintFalcon,METH_NOARGS ,"EPSprBlenderDLL::CreateNovintFalcon"},
	{"CreateSPIDAR",(PyCFunction)EPSprBlenderDLL_CreateSPIDAR,METH_NOARGS ,"EPSprBlenderDLL::CreateSPIDAR"},
	{"CreateSpaceNavigator",(PyCFunction)EPSprBlenderDLL_CreateSpaceNavigator,METH_NOARGS ,"EPSprBlenderDLL::CreateSpaceNavigator"},
	{"Enable",(PyCFunction)EPSprBlenderDLL_Enable,METH_O ,"EPSprBlenderDLL::Enable"},
	{"EnablePliant",(PyCFunction)EPSprBlenderDLL_EnablePliant,METH_O ,"EPSprBlenderDLL::EnablePliant"},
	{"GetCPS",(PyCFunction)EPSprBlenderDLL_GetCPS,METH_NOARGS ,"EPSprBlenderDLL::GetCPS"},
	{"GetCRSdk",(PyCFunction)EPSprBlenderDLL_GetCRSdk,METH_NOARGS ,"EPSprBlenderDLL::GetCRSdk"},
	{"GetCount",(PyCFunction)EPSprBlenderDLL_GetCount,METH_NOARGS ,"EPSprBlenderDLL::GetCount"},
	{"GetFWSdk",(PyCFunction)EPSprBlenderDLL_GetFWSdk,METH_NOARGS ,"EPSprBlenderDLL::GetFWSdk"},
	{"GetGRRender",(PyCFunction)EPSprBlenderDLL_GetGRRender,METH_NOARGS ,"EPSprBlenderDLL::GetGRRender"},
	{"GetHISdk",(PyCFunction)EPSprBlenderDLL_GetHISdk,METH_NOARGS ,"EPSprBlenderDLL::GetHISdk"},
	{"GetHapticTimer",(PyCFunction)EPSprBlenderDLL_GetHapticTimer,METH_NOARGS ,"EPSprBlenderDLL::GetHapticTimer"},
	{"GetInstance",(PyCFunction)EPSprBlenderDLL_GetInstance,METH_NOARGS | METH_STATIC,"EPSprBlenderDLL::GetInstance"},
	{"GetInterface",(PyCFunction)EPSprBlenderDLL_GetInterface,METH_O ,"EPSprBlenderDLL::GetInterface"},
	{"GetPhysicsTimer",(PyCFunction)EPSprBlenderDLL_GetPhysicsTimer,METH_NOARGS ,"EPSprBlenderDLL::GetPhysicsTimer"},
	{"Init",(PyCFunction)EPSprBlenderDLL_Init,METH_NOARGS ,"EPSprBlenderDLL::Init"},
	{"IsPliantEnabled",(PyCFunction)EPSprBlenderDLL_IsPliantEnabled,METH_NOARGS ,"EPSprBlenderDLL::IsPliantEnabled"},
	{"NInterfaces",(PyCFunction)EPSprBlenderDLL_NInterfaces,METH_NOARGS ,"EPSprBlenderDLL::NInterfaces"},
	{"OneStep",(PyCFunction)EPSprBlenderDLL_OneStep,METH_NOARGS ,"EPSprBlenderDLL::OneStep"},
	{"PrintScene",(PyCFunction)EPSprBlenderDLL_PrintScene,METH_NOARGS ,"EPSprBlenderDLL::PrintScene"},
	{"ResetTestSimulation",(PyCFunction)EPSprBlenderDLL_ResetTestSimulation,METH_NOARGS ,"EPSprBlenderDLL::ResetTestSimulation"},
	{"SetPliantSolidContact",(PyCFunction)EPSprBlenderDLL_SetPliantSolidContact,METH_VARARGS ,"EPSprBlenderDLL::SetPliantSolidContact"},
	{"SetPliantSolidMass",(PyCFunction)EPSprBlenderDLL_SetPliantSolidMass,METH_VARARGS ,"EPSprBlenderDLL::SetPliantSolidMass"},
	{"SetPliantTorqueLPF",(PyCFunction)EPSprBlenderDLL_SetPliantTorqueLPF,METH_VARARGS ,"EPSprBlenderDLL::SetPliantTorqueLPF"},
	{"StepPliantAfter",(PyCFunction)EPSprBlenderDLL_StepPliantAfter,METH_NOARGS ,"EPSprBlenderDLL::StepPliantAfter"},
	{"StepPliantBefore",(PyCFunction)EPSprBlenderDLL_StepPliantBefore,METH_NOARGS ,"EPSprBlenderDLL::StepPliantBefore"},
	{"ThreadCallback",(PyCFunction)EPSprBlenderDLL_ThreadCallback,METH_VARARGS | METH_STATIC,"EPSprBlenderDLL::ThreadCallback"},
	{"ThreadFunc",(PyCFunction)EPSprBlenderDLL_ThreadFunc,METH_O ,"EPSprBlenderDLL::ThreadFunc"},
	{"TimerCallback",(PyCFunction)EPSprBlenderDLL_TimerCallback,METH_VARARGS | METH_STATIC,"EPSprBlenderDLL::TimerCallback"},
	{"TimerFunc",(PyCFunction)EPSprBlenderDLL_TimerFunc,METH_O ,"EPSprBlenderDLL::TimerFunc"},
	{NULL}
};
static PyNumberMethods EPSprBlenderDLL_math_method_table=
{
	(binaryfunc)NULL,/* __add__ */
	(binaryfunc)NULL,/* __sub__ */
	(binaryfunc)NULL,/* __mul__ */
	(binaryfunc)NULL,/* __mod__ */
	(binaryfunc)NULL,/* __divmod__ */
	(ternaryfunc)NULL,/* __pow__ */
	(unaryfunc)NULL,/* __neg__ */
	(unaryfunc)NULL,/* __pos__ */
	(unaryfunc)NULL,/* __abs__ */
	(inquiry)NULL,/* __bool__ */
	(unaryfunc)NULL,/* __invert__ */
	(binaryfunc)NULL,/* __lshift__ */
	(binaryfunc)NULL,/* __rshift__ */
	(binaryfunc)NULL,/* __and__ */
	(binaryfunc)NULL,/* __xor__ */
	(binaryfunc)NULL,/* __or__ */
	(unaryfunc)NULL,/* __int__ */
	(void *)NULL,/* __reserved__ */
	(unaryfunc)NULL,/* __float__ */
	(binaryfunc)NULL,/* __iadd__ */
	(binaryfunc)NULL,/* __isub__ */
	(binaryfunc)NULL,/* __imul__ */
	(binaryfunc)NULL,/* __imod__ */
	(ternaryfunc)NULL,/* __ipow__ */
	(binaryfunc)NULL,/* __ilshift__ */
	(binaryfunc)NULL,/* __irshift__ */
	(binaryfunc)NULL,/* __iand__ */
	(binaryfunc)NULL,/* __ixor__ */
	(binaryfunc)NULL,/* __ior__ */
	(binaryfunc)NULL,/* __floordiv__ */
	(binaryfunc)NULL,/* __div__ */
	(binaryfunc)NULL,/* __ifloordiv__ */
	(binaryfunc)NULL,/* __itruediv__ */
};
static PyGetSetDef EPSprBlenderDLL_getset_table[] =
{
	{NULL}
};
void __PYDECL EPSprBlenderDLL_dealloc(PyObject* self)
{
#ifdef DEBUG_OUTPUT
	printf("SprBlenderDLL dealloc called (MemoryManager=");
	if( ((EPObject*)self)->mm == EP_MM_SPR ) printf("Springhead)\n");
	else if( ((EPObject*)self)->mm == EP_MM_PY ) printf("Python)\n");
#endif
	if ( ((EPObject*)self)->mm == EP_MM_PY ) delete EPObject_Ptr(self);
	self->ob_type->tp_free(self);
}
PyObject* __PYDECL EPSprBlenderDLL_str()
{
	return Py_BuildValue("s","This is EPSprBlenderDLLObject.");
}
PyObject* __PYDECL EPSprBlenderDLL_new(PyTypeObject *type,PyObject *args, PyObject *kwds)
{
	try
	{
		PyObject* self;
		self = type->tp_alloc(type,0);
		if ( self != NULL )
		{
			EPObject_Ptr(self) = NULL;
			((EPObject*)self)->mm = EP_MM_PY;
			return self;
		}
		return PyErr_NoMemory();
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
PyTypeObject EPSprBlenderDLLType =
{
	PyVarObject_HEAD_INIT(NULL,0)
	"SprBlenderDLL.SprBlenderDLL",/*tp_name*/
	sizeof(EPObject),/*tp_basicsize*/
	0,/*tp_itemsize*/
	(destructor)EPSprBlenderDLL_dealloc,/*tp_dealloc*/
	0,/*tp_print*/
	0,/*tp_getattr*/
	0,/*tp_setattr*/
	0,/*tp_reserved*/
	0,/*tp_repr*/
	&EPSprBlenderDLL_math_method_table,/*tp_as_number*/
	0,/*tp_as_sequence*/
	0,/*tp_as_mapping*/
	0,/*tp_call*/
	0,/*tp_hash*/
	(reprfunc)EPSprBlenderDLL_str,/*tp_str*/
	0,/*tp_getattro*/
	0,/*tp_setattro*/
	0,/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,/*tp_flags*/
	"SprBlenderDLL",/*tp_doc*/
	0,/*tp_traverse*/
	0,/*tp_clear*/
	0,/*tp_richcompare*/
	0,/*tp_weaklistoffset*/
	0,/*tp_iter*/
	0,/*tp_iternext*/
	EPSprBlenderDLL_method_table,/*tp_methods*/
	0,/*tp_members*/
	EPSprBlenderDLL_getset_table,/*tp_getset*/
	&EPObjectType,
	0,/*tp_dict*/
	0,/*tp_descr_get*/
	0,/*tp_descr_set*/
	0,/*tp_dictoffset*/
	(initproc)EPSprBlenderDLL_SprBlenderDLL,/*tp_init*/
	0,/*tp_alloc*/
	(newfunc)EPSprBlenderDLL_new,/*tp_new*/
};
void initEPSprBlenderDLL(PyObject *rootModule)
{
	if ( PyType_Ready( &EPSprBlenderDLLType ) < 0 ) return ;//PythonƒNƒ‰ƒX‚Ìì¬
	string package;
	if(rootModule) package = PyModule_GetName(rootModule);
	else // rootModule‚ª“n‚³‚ê‚½ê‡‚ÍEP_MODULE_NAME‚Í–³Ž‹‚³‚ê‚é
	{
#ifdef EP_MODULE_NAME
		package = EP_MODULE_NAME ".";
		rootModule = PyImport_AddModule( EP_MODULE_NAME );
#else
		package = "";
		rootModule = PyImport_AddModule("__main__");
#endif
	}
#ifdef EP_USE_SUBMODULE
	PyObject *subModule = PyImport_AddModule( (package+"SprBlenderDLL").c_str() );
	Py_INCREF(subModule);
	PyModule_AddObject(rootModule,"SprBlenderDLL",subModule);
#else
	PyObject *subModule = rootModule;
#endif
	Py_INCREF(&EPSprBlenderDLLType);
	PyModule_AddObject(subModule,"SprBlenderDLL",(PyObject*)&EPSprBlenderDLLType);
}
PyObject* newEPSprBlenderDLL(const SprBlenderDLL* org)
{
	try
	{
		if(org == NULL)
		{
			Py_RETURN_NONE;
		}
		PyObject *ret = EPSprBlenderDLL_new(&EPSprBlenderDLLType,NULL,NULL);
		EPObject_Ptr(ret) = org;
		((EPObject*)ret)->mm = EP_MM_SPR;
		return ret;
	}
	catch (const std::exception& e)
	{
		PyErr_SetString(PyErr_Spr_OSException, const_cast<char *>(e.what()));
		return NULL;
	}
}
void toEPSprBlenderDLL( EPObject* obj)
{
	obj->ob_base.ob_type = &EPSprBlenderDLLType;
}
//}SprBlenderDLL
/**************** for Module ******************/
void initSprBlenderDLL(PyObject *rootModule)
{
	initEPPythonGIL(rootModule);
	initEPSprBlenderDLL(rootModule);
}
