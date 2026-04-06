@echo off
echo ========================================
echo Stopping Event Streaming Pipeline
echo ========================================
echo.

set KAFKA_HOME=D:\kafka\kafka_2.13-4.2.0

echo [1/2] Stopping Kafka Broker...
%KAFKA_HOME%\bin\windows\kafka-server-stop.bat

timeout /t 3 /nobreak > nul

echo [2/2] Stopping Zookeeper...
%KAFKA_HOME%\bin\windows\zookeeper-server-stop.bat

timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo ✅ Kafka and Zookeeper stopped!
echo ========================================
pause