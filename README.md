
# Objectifs du Projet
Nous avons défini les objectifs suivants pour ce projet :
● Capturer les mouvements du curseur en temps réel toutes les 100 millisecondes.
● Analyser et traiter les données pour obtenir des statistiques comme la distance parcourue et les zones d’activité.
● Visualiser les mouvements à travers une interface en temps réel.
● Détecter des gestes spécifiques pour reconnaître certaines formes comme des cercles ou des zigzags

# Structure du Projet


cursor_tracking_project/ 
├── kafka/ 
│ ├── producer.py       # Producteur Kafka pour envoyer les données du curseur
│ └── consumer_spark.py # Consommateur Spark pour traiter les données de Kafka
├── utils/ 
│ └── config.py         # Configuration pour Kafka et Spark
├── scripts/
│ └── start_kafka.sh    # démarrer le serveur Kafka
├── analysis/           # Détection de Gestes
│ └── gesture_detection.py
├── storage/            # Détection de Gestes
│ └── db_handler.py
├── visualization/      # Interface de Visualisation en Temps Réel
│ └── realtime_dashboard.py
├── cursor_tracking.db  # la base de donnée 
└── README.md           # Documentation

 # 1- installation 


pip install confluent-kafka |
pip install pyautogui |
pip install pyspark |
pip install kafka-python pyspark pyautogui |
pip install dash plotly pandas numpy scipy fastdtw sqlalchemy |

# 2- Démarrez Zookeeper et Kafka
 
 Dans le dossier C:\kafka_2.13-3.2.1 

.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
 
 Dans une nouvelle fenêtre

.\bin\windows\kafka-server-start.bat .\config\server.properties

Créez le topic Kafka

.\bin\windows\kafka-topics.bat --create --topic cursor_positions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 

# 3-Lancer le producteur original :
  
  python kafka/producer.py

# 4-Lancer le dashboard de visualisation :
  
   python visualization/realtime_dashboard.py

# 5-Lancer le détecteur de gestes :
 
  python analysis/gesture_detection.py

# 6-Lancer le stockage en base de données :
 
  python storage/db_handler.py
