@echo off
REM ===================================================================
REM  DaxiaSaveEditor - Nuitka build script  (UTF-8 no BOM + CRLF)
REM  Output: build_output\DaxiaSaveEditor.dist\DaxiaSaveEditor.exe
REM
REM  NOTES:
REM    1) The data\ folder MUST ship next to the exe (packed below).
REM    2) settings.json / history.json / backups\ are created at runtime,
REM       do NOT pack them.
REM    3) This file must have NO BOM, otherwise cmd decodes the Chinese
REM       file names as GBK garbage and Nuitka fails with
REM       "does not match any files".
REM    4) icon.ico is needed TWICE:
REM         --windows-icon-from-ico  -> the exe file's own icon
REM         --include-data-files     -> copy the ico next to the exe, so
REM                                     the program can load it for the
REM                                     window / taskbar icon at startup
REM       (missing either one gives "exe has icon but window has not",
REM        or the other way around)
REM    5) Keep the comments ASCII-only: cmd locates line boundaries by
REM       byte offset, and a mid-file "chcp 65001" makes it desync and
REM       try to run the tail of a comment line ("'xxx' is not
REM       recognized as an internal or external command").
REM ===================================================================

chcp 65001 >nul

nuitka --standalone ^
    --enable-plugin=pyside6 ^
    --windows-console-mode=disable ^
    --follow-imports ^
    --jobs=4 ^
    --clang ^
    --remove-output ^
    --output-dir=build_output ^
    --windows-icon-from-ico=icon.ico ^
    --include-data-files=icon.ico=icon.ico ^
    --include-data-files=data/物品库.json=data/物品库.json ^
    --include-data-files=data/装备属性库.json=data/装备属性库.json ^
    --include-data-files=data/配方库.json=data/配方库.json ^
    --include-data-files=data/农作库.json=data/农作库.json ^
    --include-data-files=data/NPC库.json=data/NPC库.json ^
    --include-data-files=data/章节任务库.json=data/章节任务库.json ^
    --include-data-files=data/状态库.json=data/状态库.json ^
    --include-data-files=data/场景库.json=data/场景库.json ^
    DaxiaSaveEditor.py

echo.
echo ==== Build finished. Output: build_output\DaxiaSaveEditor.dist\DaxiaSaveEditor.exe ====
pause

