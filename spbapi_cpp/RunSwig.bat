@echo off
rem ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem <<Settings>>

set MODULE=SprBlenderDLL
set PATH=%PATH%;..\..\Springhead\core\bin;..\..\Springhead\core\bin\swig;..\..\Springhead\buildtool
set INCLUDE=../../Springhead/core/include

rem ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----

call swig.exe -cpperraswarn -sprpy -c++ %MODULE%.i & if errorlevel 1 echo !!!!SWIG FAILED!!!!! & @pause

call AStyle.exe  --style=allman --indent=tab "EP%MODULE%.cpp" "EP%MODULE%.h" "SprEP%MODULE%.h" & if errorlevel 1 @pause
del /Q .\SprEP%MODULE%.*.orig
del /Q .\EP%MODULE%.*.orig

ren EP%MODULE%.cpp EP%MODULE%.cpp.tmp

echo #include "%INCLUDE%/Springhead.h"                 > EP%MODULE%.cpp
echo #include "%INCLUDE%/EmbPython/SprEPUtility.h"    >> EP%MODULE%.cpp
echo #include "%INCLUDE%/EmbPython/SprEPBase.h"       >> EP%MODULE%.cpp
echo #include "%INCLUDE%/EmbPython/SprEPFoundation.h" >> EP%MODULE%.cpp
echo #include "%MODULE%.h"                            >> EP%MODULE%.cpp
echo #include "SprEP%MODULE%.h"                       >> EP%MODULE%.cpp
echo #pragma warning(disable:4244)                    >> EP%MODULE%.cpp

type EP%MODULE%.cpp.tmp >> EP%MODULE%.cpp
del  EP%MODULE%.cpp.tmp

pause

