#define _NOT_USE_PYTHON_SPR_LIB

#include <EmbPython/SprEPVersion.h>
#include PYTHON_H_PATH

#include <EmbPython\EmbPython.h>
#include <EmbPython\SprEPUtility.h>

#include "SprBlenderDLL.h"
#include "SprEPSprBlenderDLL.h"
#include "EPSprBlenderDLL.h"

// --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

// 関数テーブル
static PyMethodDef Spr_methods[] = {
	{NULL, NULL}
};

// モジュール定義
static struct PyModuleDef Sprmodule = {
	PyModuleDef_HEAD_INIT,
	EP_MODULE_NAME,
	"Springhead on Python",
	-1,
	Spr_methods,
	NULL,
	NULL,
	NULL,
	NULL
};

// Python <=> Springhead 変数接続マクロ
#define ACCESS_SPR_FROM_PY(cls, name, obj)							\
	{																\
		PyObject* pyObj = (PyObject*)newEP##cls((obj));				\
		Py_INCREF(pyObj);											\
		PyDict_SetItemString(dict, #name, pyObj);					\
	}																\

// Pythonモジュールの初期化（自動で呼ばれる）
extern "C" __declspec(dllexport) PyObject* _cdecl PyInit_Spr(void) {
	PyObject *module_Spr;
	module_Spr = PyModule_Create(&Sprmodule);
	PyObject *dict = PyModule_GetDict(module_Spr);

	// ---

	initUtility();
	initBase(module_Spr);
	initFoundation(module_Spr);
	initFileIO(module_Spr);
	initCollision(module_Spr);
	initPhysics(module_Spr);
	initGraphics(module_Spr);
	initCreature(module_Spr);
	initHumanInterface(module_Spr);
	initFramework(module_Spr);

	initSprBlenderDLL();

	// ---

	SprBlenderDLL* spbapi_cpp = SprBlenderDLL::GetInstance();
	ACCESS_SPR_FROM_PY(SprBlenderDLL, spbapi_cpp, spbapi_cpp);

	return module_Spr;
}
