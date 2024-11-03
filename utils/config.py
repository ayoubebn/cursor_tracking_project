# Configuration pour Kafka et Spark
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'cursor_positions'
KAFKA_GROUP_ID = 'cursor_tracking_group'

# Configuration Spark
SPARK_APP_NAME = 'CursorTrackingApp'
SPARK_MASTER = 'local[*]'

# Intervalles de traitement (en secondes)
PROCESSING_INTERVAL = 5