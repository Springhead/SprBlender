#ifndef SPREPSPRBLENDERDLL_H
#define SPREPSPRBLENDERDLL_H

//{*********EPPythonGIL*******
extern PyTypeObject EPPythonGILType;
#define EPPythonGIL_Check(ob) PyObject_TypeCheck(ob, &EPPythonGILType)
PyObject* newEPPythonGIL(const PythonGIL*);
//}EPPythonGIL

//{*********EPSprBlenderDLL*******
extern PyTypeObject EPSprBlenderDLLType;
#define EPSprBlenderDLL_Check(ob) PyObject_TypeCheck(ob, &EPSprBlenderDLLType)
PyObject* newEPSprBlenderDLL(const SprBlenderDLL*);
//}EPSprBlenderDLL
void initSprBlenderDLL(PyObject *rootModule = NULL) ;
#endif
