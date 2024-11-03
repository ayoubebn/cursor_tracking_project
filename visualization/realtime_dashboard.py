import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from confluent_kafka import Consumer
import json
import plotly.graph_objs as go
import threading
import queue
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, KAFKA_GROUP_ID

# Queue pour stocker les données
data_queue = queue.Queue(maxsize=1000)

app = dash.Dash(__name__)

# Layout de l'application
app.layout = html.Div([
    html.H1("Suivi du Curseur en Temps Réel"),
    
    # Graphique de la trajectoire
    dcc.Graph(id='live-trajectory', animate=True),
    
    # Graphique des heatmap
    dcc.Graph(id='heatmap'),
    
    # Statistiques en temps réel
    html.Div([
        html.H3("Statistiques"),
        html.Div(id='stats')
    ]),
    
    # Intervalle pour les mises à jour
    dcc.Interval(id='interval-component', interval=100)
])

def kafka_consumer():
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
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
            if data_queue.full():
                data_queue.get()  # Retire le plus ancien point si la queue est pleine
            data_queue.put(data)
            
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        consumer.close()

@app.callback(
    [Output('live-trajectory', 'figure'),
     Output('heatmap', 'figure'),
     Output('stats', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # Récupération des données de la queue
    data = []
    while not data_queue.empty():
        data.append(data_queue.get())
    
    if not data:
        return dash.no_update
        
    # Préparation des données pour les graphiques
    x = [d['x'] for d in data]
    y = [d['y'] for d in data]
    
    # Graphique de trajectoire
    trajectory = {
        'data': [
            go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                name='Trajectoire du curseur'
            )
        ],
        'layout': go.Layout(
            title='Trajectoire du Curseur',
            xaxis=dict(range=[0, 1920]),  # Ajuster selon la résolution
            yaxis=dict(range=[0, 1080])
        )
    }
    
    # Heatmap
    heatmap = {
        'data': [
            go.Histogram2d(
                x=x,
                y=y,
                colorscale='Viridis'
            )
        ],
        'layout': go.Layout(
            title='Heatmap des Positions du Curseur'
        )
    }
    
    # Statistiques
    stats = html.Div([
        html.P(f"Nombre de points: {len(data)}"),
        html.P(f"Position X moyenne: {sum(x)/len(x):.2f}"),
        html.P(f"Position Y moyenne: {sum(y)/len(y):.2f}"),
        html.P(f"Distance parcourue: {sum(((x[i]-x[i-1])**2 + (y[i]-y[i-1])**2)**0.5 for i in range(1, len(x))):.2f} pixels")
    ])
    
    return trajectory, heatmap, stats

def main():
    # Démarrage du consumer Kafka dans un thread séparé
    consumer_thread = threading.Thread(target=kafka_consumer, daemon=True)
    consumer_thread.start()
    
    # Lancement de l'application Dash
    app.run_server(debug=True, port=8050)

if __name__ == '__main__':
    main()