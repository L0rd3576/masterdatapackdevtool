@echo off
rem Launch Claude Code from the datapack master workspace, with a project folder attached.
rem Usage: mcdp.cmd [project-folder] [extra claude flags...]
rem Example: mcdp.cmd "C:\Users\lrafy\myworld\datapacks\mypack" --model sonnet --effort medium
set "PROJ=%~f1"
if "%~1"=="" set "PROJ=%CD%"
shift
cd /d "C:\Users\lrafy\mc-datapack-tools"
claude --add-dir "%PROJ%" %1 %2 %3 %4 %5 %6 %7 %8 %9
