@echo off
title Enterprise AI Document Intelligence Center Launcher
echo =============================================================
echo   INITIALIZING END-TO-END DOCUMENT EXTRACTION PORTAL
echo =============================================================
echo.
echo [1/3] Terminating stuck background port loops...
taskkill /f /im python.exe >nul 2>&1
echo [2/3] Mapping workspace tracking environment dynamically...
cd /d "C:\Users\harik\enterprise-doc-ai"
echo [3/3] Activating Anaconda environment packages and booting dashboard...
echo.
start "" "http://127.0.0.1:8501"
"C:\users\harik\anaconda3\python.exe" -m streamlit run frontend.py --server.port 8501 --server.address 127.0.0.1 --server.enableCORS false --server.enableXsrfProtection false --browser.gatherUsageStats false
pause

