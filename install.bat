@echo off

setlocal ENABLEDELAYEDEXPANSION

echo.
echo ##
echo ## SprBlender Installer
echo ##
echo.

cd /d %~dp0
set INSTALLER_DIR=%CD%


rem  ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem 
rem    Detect Blender
rem 

set BLENDER_DIR=C:\Program Files\Blender Foundation\Blender
set /P BLENDER_DIR="Blender�̏ꏊ���w�肵�Ă������� [�f�t�H���g: C:\Program Files\Blender Foundation\Blender] : "

echo.
if exist "%BLENDER_DIR%" (
  echo %BLENDER_DIR% �ɃC���X�g�[�����܂�
  cd %BLENDER_DIR%
) else (
  echo %BLENDER_DIR% ��������܂���
  echo �C���X�g�[���𒆎~���܂�
  echo.
  goto exit
)


rem  ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem 
rem    Detect Blender Version
rem 

set BLENDER_VER=
for /d %%i in (2.*) do ( 
  set BLENDER_VER=%%i
)

echo.
echo Blender %BLENDER_VER% �𔭌����܂���
set /P BLENDER_VER="���̃o�[�W�����ɃC���X�g�[������ꍇ�͓��͂��ĉ����� : "
echo.

set INSTALL_DIR=%BLENDER_DIR%\%BLENDER_VER%\scripts\modules
if exist "%INSTALL_DIR%" (
  echo %BLENDER_DIR%\%BLENDER_VER% �ɃC���X�g�[�����܂�
) else (
  echo %BLENDER_DIR%\%BLENDER_VER% ��������܂���
  echo �C���X�g�[���𒆎~���܂�
  echo.
  goto exit
)


rem  ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem 
rem    Installation
rem 

cd %INSTALL_DIR%

echo.
set DEVEL_MODE=n
set /P DEVEL_MODE="�J���҃��[�h�ŃC���X�g�[�����܂����H [y/N] : "
set INSTALL_MODE=0
if "%DEVEL_MODE%"=="y" set INSTALL_MODE=1
if "%DEVEL_MODE%"=="Y" set INSTALL_MODE=1

if "%INSTALL_MODE%"=="1" (
  rem �J���҃��[�h�C���X�g�[��
  echo.
  echo �J���҃��[�h�ŃC���X�g�[�����܂�
  echo.
  mklink /j  spb %INSTALLER_DIR%\scripts\modules\spb
  echo spb�ւ̃����N���쐬���܂���
  mklink Spr.pyd %INSTALLER_DIR%\spbapi_cpp\bin\x64\Spr.pyd
  echo Spr.pyd�ւ̃����N���쐬���܂���
  echo.

) else (
  rem ���[�U���[�h�C���X�g�[��

)


rem  ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem 
rem    Detect Dependency
rem 

cd "%INSTALLER_DIR%"

echo.

set DEPEND_DIR="..\Springhead\dependency\bin\win64"
if not exist "%DEPEND_DIR%" (
  set DEPEND_DIR=".\depends"
  if not exist "%DEPEND_DIR%" (
    echo �ˑ��t�@�C����������܂���
    echo �C���X�g�[���𒆎~���܂�
    echo.
    goto exit
  )
)

call :add_dependency

set DEPEND_DIR="..\Springhead\core\bin\win64"
if not exist "%DEPEND_DIR%" (
  set DEPEND_DIR=".\depends"
  if not exist "%DEPEND_DIR%" (
    echo �ˑ��t�@�C����������܂���
    echo �C���X�g�[���𒆎~���܂�
    echo.
    goto exit
  )
)

call :add_dependency

set DEPEND_DIR="..\Springhead\closed\bin\win64"
if not exist "%DEPEND_DIR%" (
  set DEPEND_DIR=".\depends"
  if not exist "%DEPEND_DIR%" (
    echo �ˑ��t�@�C����������܂���
    echo �C���X�g�[���𒆎~���܂�
    echo.
    goto exit
  )
)

call :add_dependency


rem  ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem 
rem    Finish
rem 

echo.
echo �C���X�g�[������
echo.

:exit
cd "%INSTALLER_DIR%"

pause

exit






rem  ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem 
rem    Sub Routine
rem 

:add_dependency

rem  ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem 
rem    Copy Dependency (if User Mode Install)
rem 

if not "%INSTALL_MODE%"=="1" (
  echo.
  echo �ˑ��t�@�C�����R�s�[���܂�
  echo.

  rem DEPEND_DIR�������ŏ���������  

)


rem  ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
rem 
rem    Add PATH to Dependency
rem 

for /f "usebackq tokens=*" %%x in (`REG QUERY HKEY_CURRENT_USER\Environment /v PATH`) do @set RESULT=%%x
set USERPATH=%RESULT:~18%

REG QUERY HKEY_CURRENT_USER\Environment /v PATH >nul 2>nul
if ERRORLEVEL 1 (

  for /d %%E in (%DEPEND_DIR%) do (
    setx PATH "%%~fE"
    echo ���[�U���ϐ�PATH���쐬�� %%~fE ��ǉ����܂���
  )

) else (

  for /d %%E in (%DEPEND_DIR%) do ( 
    echo "%%USERPATH%%" | findstr /L /i %%~fE >nul 2>nul
    if ERRORLEVEL 1 (
      setx PATH "!USERPATH!;%%~fE"
      echo ���[�U���ϐ�PATH�� %%~fE ��ǉ����܂���
    ) else (
      echo %%~fE�͊��Ƀ��[�U���ϐ��Ɋ܂܂�Ă��܂�
    )
  )

)

exit /B

