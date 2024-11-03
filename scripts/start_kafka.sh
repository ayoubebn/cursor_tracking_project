#!/bin/bash

# Démarrer Zookeeper
start cmd /k "C:\kafka_2.13-3.2.1\bin\windows\zookeeper-server-start.bat C:\kafka_2.13-3.2.1\config\zookeeper.properties"

# Attendre que Zookeeper démarre
timeout 10

# Démarrer Kafka
start cmd /k "C:\kafka_2.13-3.2.1\bin\windows\kafka-server-start.bat C:\kafka_2.13-3.2.1\config\server.properties"