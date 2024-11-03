import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import json
from confluent_kafka import Consumer, Producer
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

class GestureDetector:
    def __init__(self):
        self.gestures = {
            'circle': self._create_circle_template(),
            'square': self._create_square_template(),
            'zigzag': self._create_zigzag_template()
        }
        self.buffer = []
        self.buffer_size = 50
        
    def _create_circle_template(self):
        t = np.linspace(0, 2*np.pi, 50)
        x = 100 * np.cos(t)
        y = 100 * np.sin(t)
        return np.column_stack((x, y))
        
    def _create_square_template(self):
        points = []
        size = 100
        # Haut
        for i in range(25):
            points.append([i*size/25, 0])
        # Droite
        for i in range(25):
            points.append([size, i*size/25])
        # Bas
        for i in range(25):
            points.append([size-i*size/25, size])
        # Gauche
        for i in range(25):
            points.append([0, size-i*size/25])
        return np.array(points)
        
    def _create_zigzag_template(self):
        points = []
        size = 100
        num_zigs = 4
        for i in range(num_zigs):
            points.extend([
                [i*size/num_zigs, 0],
                [(i+0.5)*size/num_zigs, size],
                [(i+1)*size/num_zigs, 0]
            ])
        return np.array(points)
    
    def add_point(self, x, y):
        self.buffer.append([x, y])
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)
            
    def normalize_trajectory(self, trajectory):
        trajectory = np.array(trajectory)
        # Centrer
        trajectory = trajectory - np.mean(trajectory, axis=0)
        # Mettre à l'échelle
        scale = np.max(np.abs(trajectory))
        if scale > 0:
            trajectory = trajectory / scale * 100
        return trajectory
        
    def detect_gesture(self):
        if len(self.buffer) < self.buffer_size:
            return None
            
        trajectory = self.normalize_trajectory(self.buffer)
        
        best_distance = float('inf')
        detected_gesture = None
        
        for gesture_name, template in self.gestures.items():
            distance, _ = fastdtw(trajectory, template, dist=euclidean)
            if distance < best_distance:
                best_distance = distance
                detected_gesture = gesture_name
                
        # Seuil de détection
        if best_distance < 1000:  # Ajuster ce seuil selon les besoins
            return detected_gesture
        return None

def main():
    # Configuration du consumer
    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'gesture_detector',
        'auto.offset.reset': 'latest'
    }
    
    # Configuration du producer pour les gestes détectés
    producer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS
    }
    
    consumer = Consumer(consumer_conf)
    producer = Producer(producer_conf)
    consumer.subscribe([KAFKA_TOPIC])
    
    detector = GestureDetector()
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Erreur Consumer: {msg.error()}")
                continue
                
            # Traitement du message
            data = json.loads(msg.value().decode('utf-8'))
            detector.add_point(data['x'], data['y'])
            
            # Détection du geste
            gesture = detector.detect_gesture()
            if gesture:
                print(f"Geste détecté: {gesture}")
                # Publication du geste détecté
                gesture_data = {
                    'type': 'gesture',
                    'gesture': gesture,
                    'timestamp': data['timestamp']
                }
                producer.produce(
                    'cursor_gestures',
                    value=json.dumps(gesture_data).encode('utf-8')
                )
                producer.flush()
                
    except KeyboardInterrupt:
        print("Arrêt du détecteur de gestes...")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()