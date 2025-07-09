@echo off

REM This must be run from inside E:/pip_dev
SET MAYA_MODULE_PATH=%MAYA_MODULE_PATH%;%~dp0modules

REM Launch Maya
START "" "C:\Program Files\Autodesk\Maya2023\bin\maya.exe"
