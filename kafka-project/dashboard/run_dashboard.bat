@echo off
echo ========================================
echo Starting Event Streaming Dashboard
echo ========================================
echo.

cd /d D:\kafka-project\dashboard

echo Activating virtual environment...
call D:\kafka-project\setup\venv\Scripts\activate

echo Starting Streamlit Dashboard...
streamlit run dashboard.py --server.port 8501

pause