from confluent_kafka import Producer
import json
import time
import pyautogui
import sys
import os

# Ajout du chemin parent pour importer config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

def delivery_report(err, msg):
    if err is not None:
        print(f'Erreur lors de la livraison du message: {err}')
    else:
        print(f'Message livré à {msg.topic()} [{msg.partition()}] à offset {msg.offset()}')

def create_producer():
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'client.id': 'cursor_producer'
    }
    return Producer(conf)

def get_cursor_position():
    x, y = pyautogui.position()
    return {
        'timestamp': int(time.time() * 1000),
        'x': x,
        'y': y
    }

def main():
    producer = create_producer()
    print(f"Démarrage du suivi du curseur. Publication sur le topic: {KAFKA_TOPIC}")
    print(f"Appuyez sur Ctrl+C pour arrêter...")
    
    try:
        while True:
            cursor_data = get_cursor_position()
            # Conversion des données en JSON
            message = json.dumps(cursor_data)
            
            # Envoi du message
            producer.produce(
                KAFKA_TOPIC,
                value=message.encode('utf-8'),
                callback=delivery_report
            )
            
            # Appel de poll pour gérer les événements de livraison
            producer.poll(0)
            
            print(f"Position envoyée: x={cursor_data['x']}, y={cursor_data['y']}")
            time.sleep(0.1)  # Attente de 100ms entre chaque capture
            
    except KeyboardInterrupt:
        print("\nArrêt du suivi du curseur...")
    finally:
        # Attente que tous les messages soient envoyés
        print("Attente de l'envoi de tous les messages en attente...")
        producer.flush()
        print("Terminé!")

if __name__ == "__main__":
    main()