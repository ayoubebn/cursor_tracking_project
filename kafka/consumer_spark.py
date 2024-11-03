from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import sys

# Ajout du chemin parent pour importer config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import *

def create_spark_session():
    return SparkSession.builder \
        .appName(SPARK_APP_NAME) \
        .master(SPARK_MASTER) \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.2.1") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()

def create_cursor_stream(spark):
    # Définition du schéma pour les données du curseur
    schema = StructType([
        StructField("timestamp", LongType(), True),
        StructField("x", IntegerType(), True),
        StructField("y", IntegerType(), True)
    ])

    return spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load() \
        .select(from_json(col("value").cast("string"), schema).alias("cursor_data")) \
        .select("cursor_data.*")

def process_cursor_data(df):
    return df \
        .withWatermark("timestamp", f"{PROCESSING_INTERVAL} seconds") \
        .groupBy(
            window("timestamp", f"{PROCESSING_INTERVAL} seconds")
        ).agg(
            avg("x").alias("moyenne_x"),
            avg("y").alias("moyenne_y"),
            min("x").alias("min_x"),
            min("y").alias("min_y"),
            max("x").alias("max_x"),
            max("y").alias("max_y"),
            count("*").alias("nombre_points")
        )

def start_streaming(processed_stream):
    return processed_stream \
        .writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", "false") \
        .option("numRows", 5) \
        .start()

def main():
    print("Démarrage du consumer Spark...")
    
    # Création de la session Spark
    spark = create_spark_session()
    print("Session Spark créée")
    
    try:
        # Création du stream de données
        cursor_stream = create_cursor_stream(spark)
        print("Stream de données créé")
        
        # Traitement du stream
        processed_stream = process_cursor_data(cursor_stream)
        print("Définition du traitement terminée")
        
        # Démarrage du streaming
        query = start_streaming(processed_stream)
        print("Streaming démarré")
        print("Appuyez sur Ctrl+C pour arrêter...")
        
        query.awaitTermination()
        
    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")
    finally:
        spark.stop()
        print("Session Spark arrêtée")

if __name__ == "__main__":
    main()