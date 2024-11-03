from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from confluent_kafka import Consumer
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

Base = declarative_base()

class CursorPosition(Base):
    __tablename__ = 'cursor_positions'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    x = Column(Integer)
    y = Column(Integer)
    
class GestureEvent(Base):
    __tablename__ = 'gesture_events'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    gesture_type = Column(String(50))
    confidence = Column(Float)

def create_database():
    # Utilisation de SQLite pour la simplicité
    engine = create_engine('sqlite:///cursor_tracking.db')
    Base.metadata.create_all(engine)
    return engine

def store_cursor_data(session, data):
    position = CursorPosition(
        timestamp=datetime.fromtimestamp(data['timestamp']/1000),
        x=data['x'],
        y=data['y']
    )
    session.add(position)
    session.commit()

def main():
    # Création de la base de données
    engine = create_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Configuration du consumer
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': 'db_storage',
        'auto.offset.reset': 'latest'
    }
    
    consumer = Consumer(conf)
    consumer.subscribe([KAFKA_TOPIC])
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Erreur Consumer: {msg.error()}")
                continue
                
            data = json.loads(msg.value().decode('utf-8'))
            store_cursor_data(session, data)
            
    except KeyboardInterrupt:
        print("Arrêt du stockage en base de données...")
    finally:
        session.close()
        consumer.close()

if __name__ == '__main__':
    main()