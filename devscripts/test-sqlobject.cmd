@echo off

SetLocal EnableDelayedExpansion
set SavePATH=%PATH%

for %%V in (27 34 35 36 37 38 39 310) do (
   for %%s in (32 64) do (
      set PATH=C:\Python%%V-%%s;C:\Python%%V-%%s\Scripts;!SavePATH!
      set TOXPYTHON=C:\Python%%V-%%s\python.exe
      !TOXPYTHON! -m tox -e "py%%V-sqlite{-memory,}-w32"
      if !ERRORLEVEL! EQU 0 (echo Ok) else (echo Error && goto Quit)
   )
)

:Quit
set PATH=%SavePATH%
