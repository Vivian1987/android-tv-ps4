@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Android TV for PS4 - Join download
echo Android TV for PS4 1.0
echo =====================
echo.
pushd "%~dp0"
if errorlevel 1 goto folder_error
set "atv_expected=5564ccb30329123407ad03769732c0c4fc4e63084b1795d7fc7faf04dcf8ff25"
set "atv_output=Android-TV-for-PS4.pkg"
set "atv_partial=Android-TV-for-PS4.pkg.joining-%RANDOM%-%RANDOM%"
set "atv_hashlog=%atv_partial%.sha256.txt"
set "atv_result=1"
if exist "%atv_partial%" goto temp_error
if exist "%atv_hashlog%" goto temp_error
where certutil.exe >nul 2>&1
if errorlevel 1 goto checksum_tool_error
if exist "%atv_output%" goto existing
if not exist "Android-TV-for-PS4.pkg.part1" goto missing_part1
if not exist "Android-TV-for-PS4.pkg.part2" goto missing_part2
for %%F in ("Android-TV-for-PS4.pkg.part1") do if not "%%~zF"=="1610612736" goto size_error
for %%F in ("Android-TV-for-PS4.pkg.part2") do if not "%%~zF"=="1497694208" goto size_error
echo Step 1 of 2: Joining the two downloads. Please leave this window open.
echo You need about 3.2 GB of additional free space in this folder.
copy /b /y "Android-TV-for-PS4.pkg.part1"+"Android-TV-for-PS4.pkg.part2" "%atv_partial%" >nul
if errorlevel 1 goto copy_error
echo Step 2 of 2: Checking the completed package's SHA256...
certutil -hashfile "%atv_partial%" SHA256 >"%atv_hashlog%" 2>&1
if errorlevel 1 goto hash_error
findstr /i /x /c:"%atv_expected%" "%atv_hashlog%" >nul
if errorlevel 1 goto hash_error
if exist "%atv_output%" goto output_appeared
ren "%atv_partial%" "%atv_output%"
if errorlevel 1 goto rename_error
goto success

:existing
echo A PKG already exists. Checking it without replacing it...
certutil -hashfile "%atv_output%" SHA256 >"%atv_hashlog%" 2>&1
if errorlevel 1 goto existing_error
findstr /i /x /c:"%atv_expected%" "%atv_hashlog%" >nul
if errorlevel 1 goto existing_error
goto success

:success
echo.
echo READY: Android-TV-for-PS4.pkg
echo SHA256 verified. Your two downloaded parts have been kept.
echo.
echo Copy this PKG to the top level of an exFAT USB drive.
echo On the PS4, load GoldHEN and install it with the Package Installer.
echo Enable GoldHEN BinLoader on port 9090, then open Android TV for PS4.
echo Allow 5-10 minutes for first installation and boot; about 2 minutes later.
set "atv_result=0"
goto finish

:missing_part1
echo Missing Android-TV-for-PS4.pkg.part1. Put both downloads beside this tool.
goto finish
:missing_part2
echo Missing Android-TV-for-PS4.pkg.part2. Put both downloads beside this tool.
goto finish
:size_error
echo One download has the wrong size. Let both downloads finish, or download them again.
goto finish
:copy_error
echo Could not join the downloads. Check free disk space and folder permissions.
goto cleanup
:hash_error
echo Verification failed. Do not install this output. Download both parts again.
goto cleanup
:output_appeared
echo Another PKG appeared while joining. It has been left unchanged.
goto cleanup
:rename_error
echo Could not save the completed PKG. Check folder permissions and try again.
goto cleanup
:existing_error
echo The existing PKG is different or could not be checked. It has been left unchanged.
echo Move it out of this folder, then run this tool again to join the downloads.
goto finish
:checksum_tool_error
echo Windows certutil is unavailable. Use the manual checksum instructions in the release.
goto finish
:temp_error
echo A temporary filename is already in use. Close this window and try again.
popd
pause
exit /b 1
:cleanup
if exist "%atv_partial%" del /q "%atv_partial%" >nul 2>&1
:finish
if exist "%atv_hashlog%" del /q "%atv_hashlog%" >nul 2>&1
popd
echo.
pause
exit /b %atv_result%
:folder_error
echo Cannot open the download folder. Move this tool and both parts into a writable folder.
pause
exit /b 1
