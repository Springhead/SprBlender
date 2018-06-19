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
set /P BLENDER_DIR="Blenderの場所を指定してください [デフォルト: C:\Program Files\Blender Foundation\Blender] : "

echo.
if exist "%BLENDER_DIR%" (
  echo %BLENDER_DIR% にインストールします
  cd %BLENDER_DIR%
) else (
  echo %BLENDER_DIR% が見つかりません
  echo インストールを中止します
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
echo Blender %BLENDER_VER% を発見しました
set /P BLENDER_VER="他のバージョンにインストールする場合は入力して下さい : "
echo.

set INSTALL_DIR=%BLENDER_DIR%\%BLENDER_VER%\scripts\modules
if exist "%INSTALL_DIR%" (
  echo %BLENDER_DIR%\%BLENDER_VER% にインストールします
) else (
  echo %BLENDER_DIR%\%BLENDER_VER% が見つかりません
  echo インストールを中止します
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
set /P DEVEL_MODE="開発者モードでインストールしますか？ [y/N] : "
set INSTALL_MODE=0
if "%DEVEL_MODE%"=="y" set INSTALL_MODE=1
if "%DEVEL_MODE%"=="Y" set INSTALL_MODE=1

if "%INSTALL_MODE%"=="1" (
  rem 開発者モードインストール
  echo.
  echo 開発者モードでインストールします
  echo.
  mklink /j  spb %INSTALLER_DIR%\scripts\modules\spb
  echo spbへのリンクを作成しました
  mklink Spr.pyd %INSTALLER_DIR%\spbapi_cpp\bin\x64\Spr.pyd
  echo Spr.pydへのリンクを作成しました
  echo.

) else (
  rem ユーザモードインストール

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
    echo 依存ファイルが見つかりません
    echo インストールを中止します
    echo.
    goto exit
  )
)

call :add_dependency

set DEPEND_DIR="..\Springhead\core\bin\win64"
if not exist "%DEPEND_DIR%" (
  set DEPEND_DIR=".\depends"
  if not exist "%DEPEND_DIR%" (
    echo 依存ファイルが見つかりません
    echo インストールを中止します
    echo.
    goto exit
  )
)

call :add_dependency

set DEPEND_DIR="..\Springhead\closed\bin\win64"
if not exist "%DEPEND_DIR%" (
  set DEPEND_DIR=".\depends"
  if not exist "%DEPEND_DIR%" (
    echo 依存ファイルが見つかりません
    echo インストールを中止します
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
echo インストール完了
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
  echo 依存ファイルをコピーします
  echo.

  rem DEPEND_DIRをここで書き換える  

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
    echo ユーザ環境変数PATHを作成し %%~fE を追加しました
  )

) else (

  for /d %%E in (%DEPEND_DIR%) do ( 
    echo "%%USERPATH%%" | findstr /L /i %%~fE >nul 2>nul
    if ERRORLEVEL 1 (
      setx PATH "!USERPATH!;%%~fE"
      echo ユーザ環境変数PATHに %%~fE を追加しました
    ) else (
      echo %%~fEは既にユーザ環境変数に含まれています
    )
  )

)

exit /B

