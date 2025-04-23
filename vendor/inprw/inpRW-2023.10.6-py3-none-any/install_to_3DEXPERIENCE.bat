@echo off


:GETADMIN

:-------------------------------------
CLS
REM  --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting elevated administrative privileges...
    goto UACPrompt
) else ( pushd %~dp0
goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
	::pass current directory to new script, since ShellExecute for admin always runs in default directory for application
    echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params% %CD%", "", "runas", 1 >> "%temp%\getadmin.vbs"
	
	pushd %CD%
    call "%temp%\getadmin.vbs"
	del "%temp%\getadmin.vbs"
    exit /B
:-------------------------------------

:gotAdmin
	
	echo %CD%
	CD /D "%1"
	echo %CD%
	
	set "psCommand="(new-object -COM 'Shell.Application').BrowseForFolder(0,'Please specify 3DEXPERIENCE parent folder (default path is C:\Program Files\Dassault Systemes\B424 for 3DEXPERIENCE 2022).',0,0).self.path""

	for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "folder=%%I"


	for /f "delims=" %%j in ('WHERE "%folder%\win_b64\tools\SMApy\python3.7\:python.exe" /F') do set "python3_3dx=%%j"

	::upgrade pip
	::call %python3_3dx% -m pip install --upgrade pip
	
	::install modules
	
	for /f "delims=" %%i in ('DIR inpRW*.whl /b') do call %python3_3dx% -m pip install %%i --upgrade
	pause