@echo off
echo ========================================
echo Starting Event Streaming Pipeline
echo ========================================
echo.

REM Set paths for kafka-project\setup folder
set KAFKA_HOME=D:\kafka\kafka_2.13-4.2.0
set PROJECT_HOME=D:\kafka-project
set SETUP_HOME=D:\kafka-project\setup

echo Kafka Home: %KAFKA_HOME%
echo Project Home: %PROJECT_HOME%
echo.

REM Check if Kafka exists
if not exist "%KAFKA_HOME%" (
    echo ERROR: Kafka not found at %KAFKA_HOME%
    echo Please install Kafka first!
    pause
    exit /b 1
)

echo [1/3] Starting Zookeeper...
start "Zookeeper" cmd /c "%KAFKA_HOME%\bin\windows\zookeeper-server-start.bat %KAFKA_HOME%\config\zookeeper.properties"

timeout /t 5 /nobreak > nul

echo [2/3] Starting Kafka Broker...
start "Kafka Broker" cmd /c "%KAFKA_HOME%\bin\windows\kafka-server-start.bat %KAFKA_HOME%\config\server.properties"

timeout /t 8 /nobreak > nul

echo [3/3] Creating topic (if not exists)...
%KAFKA_HOME%\bin\windows\kafka-topics.bat --create --topic streaming-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 --if-not-exists

echo.
echo ========================================
echo ✅ Kafka is ready!
echo ✅ Zookeeper and Kafka Broker are running
echo ========================================
echo.
echo 📊 Topic: streaming-events
echo 🔗 Bootstrap: localhost:9092
echo 📁 Logs: D:\kafka\logs
echo.
echo To stop: Run stop_kafka.bat
echo.
pause