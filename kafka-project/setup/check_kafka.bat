@echo off
echo ========================================
echo Kafka Status Check
echo ========================================
echo.

set KAFKA_HOME=D:\kafka\kafka_2.13-4.2.0

echo [1/3] Checking if Kafka is running...
wmic process where "name='java.exe' and commandline like '%%kafka%%'" get processid 2>nul

echo.
echo [2/3] Checking topics...
%KAFKA_HOME%\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092

echo.
echo [3/3] Checking topic details...
%KAFKA_HOME%\bin\windows\kafka-topics.bat --describe --topic streaming-events --bootstrap-server localhost:9092

echo.
echo ========================================
echo Check complete!
echo ========================================
pause